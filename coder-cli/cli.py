"""
Coder CLI - Autonomous AI Terminal Assistant
Beautiful TUI Edition (No Token Tracking)
"""
import sys
import os
import glob
import re
import subprocess
import requests
import socket
import getpass
import datetime
import platform
import argparse
import time
import json
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.traceback import install
    from rich import box
    install(show_locals=False)
except ImportError:
    print("FATAL ERROR: The 'rich' library is not installed.")
    print("Please install it by running: pip3 install rich")
    sys.exit(1)
console = Console()
API_URL = os.getenv("CODER_API_URL", "http://127.0.0.1:8000").rstrip("/")
VERSION = "3.0.0-UI"
RPI_CONFIG_PATH = os.path.expanduser("~/.config/coder-bot/rpi.json")
chat_history = []
def load_rpi_config() -> dict:
    try:
        with open(RPI_CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)
            return config if isinstance(config, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
def save_rpi_config(config: dict) -> None:
    os.makedirs(os.path.dirname(RPI_CONFIG_PATH), exist_ok=True)
    with open(RPI_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)
def rpi_command(command: str) -> None:
    config = load_rpi_config()
    host, user = config.get("host"), config.get("user", "pi")
    port = str(config.get("port", 22))
    if not host:
        console.print("[yellow]Configure the RPI first with: rpi-config[/yellow]")
        return
    target = f"{user}@{host}"
    console.print(Panel(f"[bold cyan]{target}:{port}[/bold cyan]\n{command}",
                        title=" Raspberry Pi command", box=box.ROUNDED, border_style="magenta"))
    if not Confirm.ask("Send this command to the RPI?", default=False):
        console.print("[italic dim]Skipped.[/italic dim]")
        return
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
             "-p", port, target, command],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            console.print(Panel(result.stdout.strip(), title="[bold green]RPI output[/bold green]", border_style="green"))
        if result.stderr.strip():
            console.print(Panel(result.stderr.strip(), title="[bold red]RPI error[/bold red]", border_style="red"))
        if result.returncode != 0:
            console.print(f"[red]SSH exited with status {result.returncode}.[/red]")
    except FileNotFoundError:
        console.print("[red]SSH is not installed or is not on PATH.[/red]")
    except subprocess.TimeoutExpired:
        console.print("[red]RPI connection timed out.[/red]")
def configure_rpi() -> None:
    current = load_rpi_config()
    host = Prompt.ask("RPI hostname or IP", default=current.get("host", ""))
    if not host:
        console.print("[red]A hostname or IP is required.[/red]")
        return
    user = Prompt.ask("SSH user", default=current.get("user", "pi"))
    port = Prompt.ask("SSH port", default=str(current.get("port", 22)))
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        console.print("[red]SSH port must be between 1 and 65535.[/red]")
        return
    save_rpi_config({"host": host, "user": user, "port": int(port)})
    console.print(f"[green]RPI saved: {user}@{host}:{port}[/green]")
def api_status() -> None:
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        response.raise_for_status()
        console.print(Panel(f"API online at {API_URL}", title=" API status", border_style="green"))
    except requests.RequestException as error:
        console.print(Panel(str(error), title=f" API unavailable ({API_URL})", border_style="red"))
def debug_request(language: str, code: str, headers: dict) -> None:
    try:
        response = requests.post(f"{API_URL}/debug",
            json={"language": language, "code": code}, headers=headers, timeout=120)
        if response.status_code != 200:
            console.print(f"[red]API Error {response.status_code}:[/red] {response.text}")
            return
        console.print(Panel(Markdown(response.json().get("response", "")),
                            title="🐞 Debug result", border_style="yellow"))
    except requests.RequestException as error:
        console.print(f"[red]API connection failed:[/red] {error}")
def check_and_load_previous_chats() -> None:
    """Scans for previous chat logs and loads them elegantly."""
    chat_files = sorted(glob.glob("chat_*.md"))
    if not chat_files:
        return
    console.print(Panel(
        f"🔍 Found {len(chat_files)} previous session log(s): [cyan]{', '.join(chat_files)}[/cyan]",
        title="[bold green]Restore Session?[/bold green]",
        box=box.ROUNDED,
        border_style="green"
    ))
    if Confirm.ask("Load the latest chat history into memory?", default=True):
        latest_file = chat_files[-1]
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                content = f.read()
            blocks = re.findall(r"### (User|Assistant)\n(.*?)(?=\n### |\Z)", content, re.DOTALL)
            for role, text in blocks:
                cleaned_text = text.strip()
                if cleaned_text:
                    chat_history.append({
                        "role": role.lower(),
                        "content": cleaned_text
                    })
            console.print(f"[bold green] Loaded {len(chat_history)} messages from {latest_file}[/bold green]\n")
        except Exception as e:
            console.print(f"[bold red] Failed to load chat log {latest_file}:[/bold red] {e}\n")
def save_chat_log_on_exit() -> None:
    """Saves the session to a beautiful Markdown file."""
    if not chat_history:
        console.print("[italic dim]No chat history to save. Goodbye![/italic dim]")
        return
    if Confirm.ask("\n💾 Save session to a markdown log?", default=True):
        idx = 1
        while os.path.exists(f"chat_{idx:03d}.md"):
            idx += 1
        filename = f"chat_{idx:03d}.md"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"#  Coder CLI Session Log\n\n")
                f.write(f"**Date:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n")
                f.write(f"**Host:** `{socket.gethostname()}` | **User:** `{getpass.getuser()}`\n")
                f.write("---\n\n")
                for entry in chat_history:
                    role_title = "User" if entry["role"] == "user" else "Assistant"
                    f.write(f"### {role_title}\n{entry['content']}\n\n")
            console.print(f"[bold green] Session saved to [underline]{filename}[/underline][/bold green]")
        except Exception as e:
            console.print(f"[bold red] Error saving log:[/bold red] {e}")
def get_context_payload(prompt: str, extra_args: dict = None) -> dict:
    """Builds the AI payload with system context injected."""
    current_dir = os.getcwd()
    try:
        dir_items = sorted(os.listdir(current_dir))[:15]
        dir_summary = ", ".join(dir_items) if dir_items else "Empty directory"
    except Exception:
        dir_summary = "Permission Denied"
    history_summary = ""
    if chat_history:
        history_summary = "\n=== RECENT HISTORY ===\n"
        for msg in chat_history[-6:]:
            role = msg['role'].upper()
            content = msg['content']
            if len(content) > 600:
                content = content[:600] + "\n...[Truncated]..."
            history_summary += f"[{role}]: {content}\n\n"
    system_instruction = (
        f"You are a GitHub Copilot-style terminal assistant.\n"
        f"• Working Directory: '{current_dir}'\n"
        f"• Files: [{dir_summary}]\n"
        f"{history_summary}\n"
        f"INSTRUCTIONS:\n"
        f"1. Provide brief explanations.\n"
        f"2. Output executable commands inside ```bash blocks.\n"
        f"3. Analyze command output when provided."
    )
    payload = {
        "prompt": prompt,
        "cwd": current_dir,
        "platform": sys.platform,
        "system_info": system_instruction,
        "history": chat_history 
    }
    if extra_args:
        payload.update(extra_args)
    return payload
def execute_local_command(cmd_str: str) -> tuple[bool, str]:
    """Safely executes bash commands with a beautiful output panel."""
    cmd_str = cmd_str.strip()
    if not cmd_str or cmd_str.startswith("`"):
        return False, ""
    console.print(Panel(
        f"[bold cyan]{cmd_str}[/bold cyan]", 
        title=" [bold yellow]Proposed Execution[/bold yellow]", 
        box=box.HEAVY, 
        border_style="yellow"
    ))
    if Confirm.ask("Allow execution?", default=False):
        try:
            with console.status("[bold magenta]Executing on host...[/bold magenta]", spinner="dots2"):
                result = subprocess.run(
                    cmd_str,
                    shell=True,
                    capture_output=True,
                    text=True,
                    executable="/bin/bash" if os.path.exists("/bin/bash") else None
                )
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            output = stdout if stdout else stderr
            if not output:
                output = "(Command executed successfully with no terminal output)"
            if stdout:
                console.print(Panel(stdout, title="[bold green] Standard Output[/bold green]", box=box.ROUNDED, border_style="green"))
            if stderr:
                console.print(Panel(stderr, title="[bold red]️ Standard Error[/bold red]", box=box.ROUNDED, border_style="red"))
            return True, output
        except Exception as e:
            console.print(f"[bold red]Execution Exception:[/bold red] {e}")
            return False, f"Error: {e}"
    else:
        console.print("[italic dim]Skipped.[/italic dim]")
        return False, "User rejected execution."
def run_copilot_loop(endpoint: str, initial_prompt: str, headers: dict, title: str, spinner_text: str, extra_args: dict = None) -> None:
    """Communicates with the AI, displays markdown, and handles automatic execution."""
    chat_history.append({"role": "user", "content": initial_prompt})
    payload = get_context_payload(initial_prompt, extra_args)
    try:
        with console.status(f"[bold cyan] {spinner_text}...[/bold cyan]", spinner="bouncingBar"):
            res = requests.post(f"{API_URL}/{endpoint}", json=payload, headers=headers, timeout=120)
            if res.status_code != 200:
                console.print(f"[bold red] API Error {res.status_code}:[/bold red] {res.text}")
                return
            data = res.json()
        response_text = data.get("response", "No response received.")
        console.print(Panel(
            Markdown(response_text),
            title=f" [bold blue]{title}[/bold blue]",
            box=box.ROUNDED,
            border_style="blue"
        ))
        chat_history.append({"role": "assistant", "content": response_text})
        raw_blocks = re.findall(r"```(?:bash|sh)\n(.*?)\n```", response_text, re.DOTALL)
        valid_commands = [line.strip() for block in raw_blocks for line in block.strip().split("\n") if line.strip() and not line.startswith("#")]
        for cmd in valid_commands:
            executed, output = execute_local_command(cmd)
            if executed:
                follow_up = f"Executed: `{cmd}`\nOutput:\n```\n{output}\n```"
                chat_history.append({"role": "user", "content": follow_up})
    except requests.exceptions.ConnectionError:
        console.print(f"\n[bold red] Connection Error:[/bold red] Could not reach AI backend at {API_URL}")
        console.print("[dim]Is the local backend running?[/dim]\n")
    except Exception as e:
        console.print(f"\n[bold red] Unexpected Error:[/bold red] {e}")
def display_help():
    """Renders a beautiful Help Table."""
    table = Table(title="[bold magenta]Available Commands[/bold magenta]", box=box.SIMPLE_HEAVY, header_style="bold cyan")
    table.add_column("Command", justify="left", style="green", no_wrap=True)
    table.add_column("Description", justify="left")
    table.add_row("ask <query>", "Ask a general question or get coding advice")
    table.add_row("code <req>", "Ask the AI to generate a script or code block")
    table.add_row("plan <req>", "Create an implementation roadmap")
    table.add_row("debug <lang> <code>", "Review code and suggest fixes")
    table.add_row("exec <cmd>", "Force execute a raw shell command immediately")
    table.add_row("rpi-config", "Configure the Raspberry Pi SSH target")
    table.add_row("rpi <cmd>", "Run a confirmed command on the Raspberry Pi")
    table.add_row("rpi-status", "Check the Raspberry Pi SSH connection")
    table.add_row("api-status", "Check the API server connection")
    table.add_row("history", "View current session history in memory")
    table.add_row("sysinfo", "Print current system and environment context")
    table.add_row("clear", "Clear the terminal screen")
    table.add_row("exit / quit", "Exit the CLI and optionally save log")
    console.print(table)
def display_sysinfo():
    """Renders a beautiful System Info Panel."""
    info = (
        f"**OS:** {platform.system()} {platform.release()}\n"
        f"**Host:** {socket.gethostname()}\n"
        f"**User:** {getpass.getuser()}\n"
        f"**Directory:** `{os.getcwd()}`\n"
        f"**Python:** {sys.version.split(' ')[0]}\n"
    )
    console.print(Panel(Markdown(info), title="[bold cyan]System Information[/bold cyan]", box=box.ROUNDED, border_style="cyan"))
def display_history():
    """Renders the current session history."""
    if not chat_history:
        console.print("[italic dim]No history in current session.[/italic dim]")
        return
    for i, msg in enumerate(chat_history):
        role_color = "green" if msg["role"] == "user" else "blue"
        role_icon = "👤 User" if msg["role"] == "user" else " Assistant"
        content = msg["content"]
        if len(content) > 300:
             content = content[:300] + " ...[truncated]"
        console.print(Panel(
            content,
            title=f"[{role_color}]{role_icon} (Msg {i+1})[/{role_color}]",
            box=box.ROUNDED,
            border_style=role_color
        ))
def main():
    parser = argparse.ArgumentParser(description="Coder CLI (Beautiful Edition)")
    parser.add_argument("api_key", nargs="?", default=os.getenv("CODER_API_KEY", ""), type=str)
    args = parser.parse_args()
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""[bold cyan]
  ____          _               ____ _     ___ 
 / ___|___   __| | ___ _ __    / ___| |   |_ _|
| |   / _ \\ / _` |/ _ \\ '__|  | |   | |    | | 
| |__| (_) | (_| |  __/ |     | |___| |___ | | 
 \\____\\___/ \\__,_|\\___|_|      \\____|_____|___|[/bold cyan]
[italic]Autonomous Terminal Assistant v{VERSION}[/italic]
[dim]Type [bold green]'help'[/bold green] to see commands or [bold green]'exit'[/bold green] to leave.[/dim]
"""
    console.print(Panel(banner, box=box.HEAVY, border_style="cyan", padding=(1, 2)))
    check_and_load_previous_chats()
    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json"
    }
    headers["X-API-Key"] = args.api_key
    headers.pop("Authorization", None)
    while True:
        try:
            cwd = os.getcwd()
            base_dir = os.path.basename(cwd) or "/"
            prompt_str = (
                f"\n[bold green]{getpass.getuser()}[/bold green]"
                f"@[bold blue]{socket.gethostname()}[/bold blue]:"
                f"[bold magenta]{base_dir}[/bold magenta]  "
            )
            user_input = Prompt.ask(prompt_str).strip()
            if not user_input:
                continue
            parts = user_input.split(" ", 1)
            cmd = parts[0].lower()
            c_args = parts[1] if len(parts) > 1 else ""
            if cmd in ["exit", "quit", "q"]:
                save_chat_log_on_exit()
                break
            elif cmd == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            elif cmd == "help":
                display_help()
            elif cmd == "sysinfo":
                display_sysinfo()
            elif cmd == "history":
                display_history()
            elif cmd == "api-status":
                api_status()
            elif cmd == "rpi-config":
                configure_rpi()
            elif cmd == "rpi-status":
                rpi_command("printf 'RPI online: '; hostname")
            elif cmd == "rpi":
                if c_args:
                    rpi_command(c_args)
                else:
                    console.print("[red]Usage: rpi <command>[/red]")
            elif cmd == "exec":
                if c_args:
                    execute_local_command(c_args)
                else:
                    console.print("[red]Usage: exec <command>[/red]")
            elif cmd == "ask":
                if c_args:
                    run_copilot_loop("ask", c_args, headers, "Copilot Answer", "Thinking")
                else:
                    console.print("[red]Usage: ask <your question>[/red]")
            elif cmd == "code":
                if c_args:
                    run_copilot_loop("code", c_args, headers, "Code Generation", "Writing code")
                else:
                    console.print("[red]Usage: code <description of script to write>[/red]")
            elif cmd == "plan":
                if c_args:
                    run_copilot_loop("plan", c_args, headers, "Implementation Plan", "Planning")
                else:
                    console.print("[red]Usage: plan <project or feature>[/red]")
            elif cmd == "debug":
                debug_parts = c_args.split(" ", 1)
                if len(debug_parts) == 2:
                    debug_request(debug_parts[0], debug_parts[1], headers)
                else:
                    console.print("[red]Usage: debug <language> <code>[/red]")
            else:
                if Confirm.ask(f"[dim]Unknown local command '[bold]{cmd}[/bold]'. Send to AI?[/dim]", default=True):
                    run_copilot_loop("ask", user_input, headers, "Copilot Answer", "Processing")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Interrupt detected.[/bold red]")
            save_chat_log_on_exit()
            break
        except Exception as e:
            console.print_exception(show_locals=False)
if __name__ == "__main__":
    main()
