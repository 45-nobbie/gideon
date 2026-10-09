
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="gideon",
    help="Sir Gideon, the All-Knowing — your command-line companion.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main() -> None:
    """Consult the ancient command-line wizard."""


@app.command()
def hello() -> None:
    """Summon Sir Gideon."""
    title = Text("SIR GIDEON", style="bold bright_magenta")
    subtitle = Text("The All-Knowing", style="italic cyan")

    console.print(Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="bright_magenta",
        subtitle="Keeper of Flags • Interpreter of Shells",
    ))
    console.print(
        "\n[green]Gideon awakens.[/green] "
        "State your command, mortal."
    )


@app.command()
def demo() -> None:
    """Demonstrate Rich formatting."""
    table = Table(title="The Ancient Knowledge")

    table.add_column("Flag", style="cyan", no_wrap=True)
    table.add_column("Meaning", style="white")
    table.add_column("Example", style="green")

    table.add_row("-type d", "Match directories", "find . -type d")
    table.add_row("-iname", "Case-insensitive name", 'find . -iname "*.log"')
    table.add_row("-mtime", "Filter by modification age", "find . -mtime -7")

    console.print(table)


if __name__ == "__main__":
    app()
