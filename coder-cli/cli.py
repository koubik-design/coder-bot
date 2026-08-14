import os
import sys
import json
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

# Configuration
CONFIG_FILE = os.path.expanduser("~/.coder_cli.json")
API_URL = "http://127.0.0.1:8000/v1/chat" # Change this if hosting online

console = Console()
session = PromptSession()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def setup_cli():
    console.print(Panel.fit("[bold cyan]🤖 Coder CLI Setup[/bold cyan]", border_style="cyan"))
    config = load_config()
    
    if "api_key" not in config:
        console.print("Generate an API key by typing [bold green]c!api[/bold green] in your Discord server.")
        key = console.input("[bold yellow]Paste your API Key:[/bold yellow] ").strip()
        config["api_key"] = key
        save_config(config)
        console.print("[bold green]✅ API Key saved![/bold green]\n")
        
    return config["api_key"]

def process_command(api_key: str, user_input: str):
    parts = user_input.split(" ", 1)
    command = parts[0].lower()
    
    if command not in ["/ask", "/code", "/plan"]:
        console.print("[bold red]❌ Unknown command. Use /ask, /code, or /plan.[/bold red]")
        return

    if len(parts) < 2:
        console.print(f"[bold red]❌ Please provide a prompt for {command}[/bold red]")
        return

    prompt = parts[1]
    language = None
    
    if command == "/code":
        # Extract language for code command (e.g., /code python a snake game)
        sub_parts = prompt.split(" ", 1)
        if len(sub_parts) > 1:
            language = sub_parts[0]
            prompt = sub_parts[1]
        else:
            language = "python" # default fallback

    payload = {
        "api_key": api_key,
        "command": command,
        "prompt": prompt,
        "language": language
    }

    try:
        with Live(Spinner("dots", text="[cyan]Coder is thinking...[/cyan]"), transient=True, console=console):
            response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            console.print(Panel(Markdown(data["response"]), border_style="green", title="🤖 Coder"))
        elif response.status_code == 401:
            console.print("[bold red]❌ Invalid API Key. Please delete ~/.coder_cli.json and setup again.[/bold red]")
        else:
            console.print(f"[bold red]❌ API Error: {response.json().get('detail', 'Unknown error')}[/bold red]")
            
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Could not connect to API server. Is it running?[/bold red]")

def main():
    api_key = setup_cli()
    console.print("[bold bright_black]Type /ask, /code <lang>, /plan, or /exit[/bold bright_black]")
    
    # Custom prompt styling
    style = Style.from_dict({"prompt": "ansicyan bold",})
    
    while True:
        try:
            text = session.prompt("coder> ", style=style).strip()
            if not text: continue
            if text.lower() in ["/exit", "/quit", "exit()"]:
                console.print("[bold cyan]Goodbye![/bold cyan]")
                sys.exit(0)
            
            if text.startswith("/"):
                process_command(api_key, text)
            else:
                # Default behavior if they don't use a slash command
                process_command(api_key, f"/ask {text}")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
