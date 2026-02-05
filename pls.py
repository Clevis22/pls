#!/usr/bin/env python3
import sys
import time
import subprocess
import signal
import warnings
import requests
import ollama
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.style import Style

# --- CONFIGURATION ---
MODEL = "llama3.1:8b"
OLLAMA_API_URL = "http://127.0.0.1:11434"
console = Console()

# --- SILENCE WARNINGS ---
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")

def cleanup_zombies():
    subprocess.run(["pkill", "-9", "-f", "ollama"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_ollama_running():
    try:
        requests.get(OLLAMA_API_URL, timeout=0.5)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False

def start_ollama():
    # Use Rich's status spinner
    with console.status(f"[bold yellow]⚡ Waking up {MODEL}...[/bold yellow]", spinner="dots"):
        process = subprocess.Popen(
            ["ollama", "serve"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        retries = 0
        while not is_ollama_running():
            time.sleep(0.5)
            retries += 1
            if retries > 20:
                console.print("[bold red]Error: Could not start Ollama.[/bold red]")
                sys.exit(1)
    return process

def stop_ollama(process):
    if process:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

def sanitize_command(raw: str) -> str:
    raw = raw.strip()

    # 1. Remove markdown code blocks (```bash ... ```)
    if "```" in raw:
        lines = raw.splitlines()
        # Keep only lines that are NOT the ``` markers
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        # Re-join them
        raw = "\n".join(lines).strip()

    # 2. Remove inline backticks (`command`)
    if raw.startswith("`") and raw.endswith("`") and len(raw) > 2:
        raw = raw[1:-1].strip()

    # 3. Return the FULL string, not just the first line
    return raw

# --- MAIN LOGIC ---
server_process = None

def signal_handler(sig, frame):
    console.print(f"\n[bold red]🛑 Interrupted! Shutting down...[/bold red]")
    if server_process:
        stop_ollama(server_process)
    sys.exit(0)

def main():
    global server_process
    signal.signal(signal.SIGINT, signal_handler)

    # --- DETECT MODE ---
    ask_mode = False
    if "-a" in sys.argv:
        ask_mode = True
        sys.argv.remove("-a")

    if len(sys.argv) < 2:
        console.print(f"[bold]Usage:[/bold] {sys.argv[0]} [-a] 'your query here'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Clean start logic
    if not is_ollama_running():
        cleanup_zombies()
        
    was_already_running = is_ollama_running()

    try:
        if not was_already_running:
            server_process = start_ollama()
        
        # --- SYSTEM PROMPT ---
        if ask_mode:
            system_instruction = (
                "You are a concise macOS (Apple Silicon) assistant. "
                "Answer clearly and accurately."
            )
        else:
            system_instruction = (
                "You are an expert macOS (Apple Silicon) terminal assistant. "
                "Output ONLY the raw, single-line command string. No markdown. No explanations.\n"
                "GUIDELINES:\n"
                "1. TOOLS: Use modern native tools (pmset for battery, ipconfig for IP, diskutil, etc). "
                "Avoid Linux-specific flags (e.g. use 'grep -E', never 'grep -P').\n"
                "2. FORMAT: Chain commands with '&&' or '|' into a single line. "
                "Be robust with regex (match units like '%' to avoid false positives).\n"
                "3. OUTPUT: Print to STDOUT by default. Only use '| pbcopy' if the user explicitly asks to 'copy' or 'clip'."
            )

        # --- THE THINKING ANIMATION ---
        content = ""
        with console.status(f"[bold cyan]🧠 {MODEL} is thinking...[/bold cyan]", spinner="aesthetic"):
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': system_instruction},
                    # --- TEACH BY EXAMPLE ---
                    {'role': 'user', 'content': 'get battery'},
                    {'role': 'assistant', 'content': 'pmset -g batt | grep -o "[0-9]*%"'},
                    {'role': 'user', 'content': 'copy ip address'},
                    {'role': 'assistant', 'content': 'ipconfig getifaddr en0 | pbcopy'},
                    # --- REAL QUERY ---
                    {'role': 'user', 'content': query}
                ],
                options={"keep_alive": 0} 
            )
            content = response['message']['content'].strip()

        # --- DISPLAY OUTPUT ---
        if ask_mode:
            console.print(Panel(content, title="[bold cyan]Answer[/bold cyan]", border_style="cyan"))
        else:
            command = sanitize_command(content)
            if not command:
                console.print("[bold red]Error:[/bold red] Model returned an empty command.")
                return

            # Highlight the command code
            syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title="[bold green]Suggested Command[/bold green]", border_style="green"))
            
            confirm = console.input(f"[grey50][?][/grey50] Run this? ([bold]Y[/bold]/n): ").lower()
            if confirm in ['', 'y', 'yes']:
                subprocess.run(command, shell=True)
            else:
                console.print("[dim]Aborted.[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

    finally:
        if not was_already_running and server_process:
            stop_ollama(server_process)
            console.print(f"[dim]💤 {MODEL} put back to sleep.[/dim]")

if __name__ == "__main__":
    main()
