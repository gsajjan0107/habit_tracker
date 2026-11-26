from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_header():
    title = Text("HABIT TRACKER", style="bold cyan")
    subtitle = Text("Build consistency. Build character.", style="dim")

    header = Text()
    header.append(title)
    header.append("\n")
    header.append(subtitle)

    console.print(Panel(
        header,
        border_style="cyan",
        padding=(1, 2),
        expand=True
    ))