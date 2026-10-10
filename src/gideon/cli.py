import json
from multiprocessing.util import info
import re
from pathlib import Path
from rich import box
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import shlex
from gideon.generator import generate_from_intent
from gideon.knowledge import COMMANDS
import shutil
import subprocess
from gideon.saved_commands import (
    AliasAlreadyExistsError,
    AliasNotFoundError,
    InvalidAliasError,
    SavedCommandError,
    SavedCommandStore,
)
from rich.table import Table

app = typer.Typer(
    name="gideon",
    help="Sir Gideon, the All-Knowing — your command-line companion.",
    no_args_is_help=True,
)

console = Console()

saved_store = SavedCommandStore()

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



@app.command("how")
def how_gideon(
    request: str = typer.Argument(
        ...,
        help="Describe what you want to accomplish in Linux.",
    ),
) -> None:
    """Suggest and explain a Linux command from natural language."""
    result = generate_from_intent(request)

    if result is None:
        console.print(
            "[yellow]Gideon doesn't recognize that request yet.[/yellow]"
        )
        console.print(
            "Try describing a file, storage, networking, "
            "or system-information task."
        )
        raise typer.Exit(code=1)

    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Panel(
            request,
            title="Gideon understood your request",
            border_style="cyan",
        )
    )

    console.print(
        Panel(
            str(result["command"]),
            title="Proposed command — review before running",
            border_style="green",
        )
    )

    explanation = Table(
        title="How the command works",
        show_header=True,
    )
    explanation.add_column("Syntax", style="cyan")
    explanation.add_column("Meaning")

    for token, meaning in result["explanation"]:
        explanation.add_row(str(token), str(meaning))

    console.print(explanation)
    console.print(
        "\n[dim]Gideon has not executed this command.[/dim]"
    )




@app.command("ofnir")
def show_manual(
    command: str = typer.Argument(
        ...,
        help="The command whose manual page you want to read.",
    ),
) -> None:
    """Read an installed Linux manual page."""
    man = shutil.which("man")

    if man is None:
        console.print(
            "[red]The 'man' utility is unavailable.[/red]"
        )
        console.print(
            "On Ubuntu/Debian, install it with: "
            "sudo apt install man-db manpages"
        )
        raise typer.Exit(code=1)

    try:
        result = subprocess.run(
            [man, "-P", "cat", command],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except subprocess.TimeoutExpired:
        console.print("[red]Manual lookup timed out.[/red]")
        raise typer.Exit(code=1)

    if result.returncode != 0 or not result.stdout.strip():
        console.print(
            f"[yellow]No manual page found for "
            f"{command!r}.[/yellow]"
        )
        raise typer.Exit(code=1)

    console.print(
        f"\n[bold cyan]Gideon is consulting the "
        f"manual for {command}[/bold cyan]\n"
    )

    console.print(result.stdout, markup=False)



@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Describe a command or topic to search for.",
    ),
) -> None:
    """Search installed Linux manual pages."""
    apropos = shutil.which("apropos")

    if apropos is None:
        console.print(
            "[red]The 'apropos' utility is unavailable.[/red]"
        )
        console.print(
            "Install man-db on Ubuntu/Debian with: "
            "sudo apt install man-db"
        )
        raise typer.Exit(code=1)

    result = subprocess.run(
        [apropos, query],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0 or not result.stdout.strip():
        console.print(
            f"[yellow]No manual-page matches for {query!r}.[/yellow]"
        )
        raise typer.Exit(code=1)

    table = Table(title=f"Gideon found: {query}")
    table.add_column("Manual", style="cyan")
    table.add_column("Description")

    for line in result.stdout.splitlines():
        if " - " in line:
            name, description = line.split(" - ", 1)
        else:
            name, description = line, ""

        table.add_row(name, description)

    console.print(table)



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


DATA_FILE = Path(__file__).parent / "data" / "commands.json"


def load_commands() -> list[dict]:
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


@app.command()
def howto(
    query: str = typer.Argument(
        ...,
        help="Describe what you want to accomplish.",
    ),
    shell: str = typer.Option(
        "bash",
        "--shell",
        "-s",
        help="Command environment: bash, powershell, or cmd.",
    ),
) -> None:
    """Find a command by describing the task."""
    commands = load_commands()

    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    results = []

    for item in commands:
        if item["shell"] != shell.lower():
            continue

        searchable = set(
            item["tags"]
            + re.findall(
                r"[a-z0-9]+",
                item["description"].lower(),
            )
            + re.findall(
                r"[a-z0-9]+",
                item["command"].lower(),
            )
        )

        score = len(words & searchable)

        if score:
            results.append((score, item))

    results.sort(key=lambda result: result[0], reverse=True)

    if not results:
        console.print(
            "[yellow]Gideon has no wisdom on this matter yet.[/yellow]"
        )
        console.print(
            "Try different keywords or add a recipe to commands.json."
        )
        raise typer.Exit(code=1)

    for score, item in results[:5]:
        console.print()
        console.print(
            Panel(
                f"[bold cyan]{item['command']}[/bold cyan]\n\n"
                f"{item['description']}\n"
                f"[dim]Shell: {item['shell']} | "
                f"Match score: {score}[/dim]",
                title=f"[bold]{item['id']}[/bold]",
                border_style="cyan",
            )
        )

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Syntax")
        table.add_column("Meaning")

        for syntax, meaning in item["explanation"]:
            table.add_row(syntax, meaning)

        console.print(table)


def _tokenize_command(command: str) -> list[str]:
    """Tokenize a limited shell-like expression without executing it."""
    lexer = shlex.shlex(
        command,
        posix=True,
        punctuation_chars="|;&<>",
    )
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _expand_short_flags(
    token: str,
    options: dict,
) -> list[str]:
    """Expand combined flags only when every character is a known flag."""
    if token in options or not token.startswith("-") or token.startswith("--"):
        return [token]

    if len(token) <= 2:
        return [token]

    flags = ["-" + character for character in token[1:]]

    if all(
        flag in options and not options[flag]["takes_value"]
        for flag in flags
    ):
        return flags

    return [token]



def _explain_stage(
    tokens: list[str],
    table: Table,
    deep: bool = False,
) -> None:
    """Explain one command stage using the knowledge registry."""
    if not tokens:
        table.add_row("(empty stage)", "No command found.", "Unsupported")
        return

    name = tokens[0]
    info = COMMANDS.get(name)

    if info is None:
        table.add_row(
            name,
            "Command is not in Gideon's knowledge base.",
            "Unknown command",
        )
        for token in tokens[1:]:
            table.add_row(token, "Not analyzed.", "Unverified")
        return

    table.add_row(name, info["summary"], "Recognized")

    options = info["options"]
    argument_definitions = info.get("arguments", [])
    argument_index = 0
    i = 1
    options_ended = False

    while i < len(tokens):
        token = tokens[i]

        # "--" ends option parsing; it is not an argument.
        if not options_ended and token == "--":
            table.add_row(
                token,
                "End of options; subsequent tokens are treated as arguments.",
                "Recognized",
            )
            options_ended = True
            i += 1
            continue

        # Check options before treating a token as an argument.
        if not options_ended:
            expanded = _expand_short_flags(token, options)

            if expanded != [token]:
                for flag in expanded:
                    option = options[flag]
                    table.add_row(
                        flag,
                        option["description"],
                        "Recognized",
                    )
                i += 1
                continue

            option = options.get(token)

            if option is not None:
                explanation = option["description"]

                if option["takes_value"]:
                    if i + 1 >= len(tokens):
                        table.add_row(
                            token,
                            explanation,
                            "Missing value",
                        )
                        i += 1
                        continue

                    value = tokens[i + 1]
                    meaning = option.get("values", {}).get(value)

                    if meaning:
                        explanation += f" Value {value!r}: {meaning}."

                    table.add_row(
                        f"{token} {value}",
                        explanation,
                        "Recognized",
                    )
                    i += 2
                    continue

                table.add_row(token, explanation, "Recognized")
                i += 1
                continue

            if token.startswith("-"):
                table.add_row(
                    token,
                    "Option not found in Gideon's knowledge base. "
                    "Check the command's manual page.",
                    "Unverified",
                )
                i += 1
                continue

        # Positional argument: use the command's argument definitions.
        if argument_index < len(argument_definitions):
            argument = argument_definitions[argument_index]

            table.add_row(
                token,
                f"{argument['name']}: {argument['description']}",
                "Recognized argument",
            )
            argument_index += 1
        else:
            table.add_row(
                token,
                "Additional positional argument; its meaning is not documented.",
                "Unverified",
            )

        i += 1

    if deep:
        console.print(
            f"[dim]Command purpose: {info['summary']}[/dim]"
        )
        console.print(
            "[dim]Only options and arguments documented in "
            "Gideon's knowledge base are verified.[/dim]"
        )



@app.command()
def explain(
    command: str = typer.Argument(
        ...,
        help="The command line you want explained.",
    ),
    deep: bool = typer.Option(
        False,
        "--deep",
        help="Include additional context and interpretation.",
    ),
) -> None:
    """Explain a command or supported pipeline."""
    try:
        tokens = _tokenize_command(command)
    except ValueError as exc:
        console.print(f"[red]Could not parse input:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    if not tokens:
        console.print("[yellow]Nothing to explain.[/yellow]")
        raise typer.Exit(code=1)

    # Support simple pipelines. Do not pretend to parse other shell operators.
    unsupported_operators = {"&&", "||", ";", ">", ">>", "<", "<<", "&"}
    if any(token in unsupported_operators for token in tokens):
        console.print(
            "[yellow]This shell expression uses syntax Gideon "
            "doesn't analyze yet.[/yellow]"
        )
        console.print(
            "For now, try a single command or a pipeline using '|'."
        )
        raise typer.Exit(code=2)

    stages: list[list[str]] = [[]]
    for token in tokens:
        if token == "|":
            stages.append([])
        else:
            stages[-1].append(token)

    if any(not stage for stage in stages):
        console.print(
            "[yellow]The pipeline contains an empty stage.[/yellow]"
        )
        raise typer.Exit(code=2)

    console.print(
        Panel(
            f"[bold cyan]{command}[/bold cyan]",
            title="Sir Gideon explains",
            border_style="cyan",
        )
    )

    for index, stage in enumerate(stages, start=1):
        if len(stages) > 1:
            console.print(f"\n[bold]Pipeline stage {index}[/bold]")

        table = Table(
            title="Command breakdown",
            show_header=True,
        )
        table.add_column("Token", style="cyan")
        table.add_column("Explanation")
        table.add_column("Status")

        _explain_stage(stage, table, deep=deep)
        console.print(table)

    if len(stages) > 1:
        console.print(
            "\n[dim]Pipeline: each stage's standard output is passed "
            "to the next stage's standard input. Gideon has not "
            "verified that the combined pipeline behaves as intended.[/dim]"
        )

    if deep:
        console.print(
            "\n[dim]Deep mode provides extra context, not a guarantee "
            "that every shell behavior or command option is understood.[/dim]"
        )



def _report_saved_command_error(exc: SavedCommandError) -> None:
    """Display a storage error without exposing a traceback."""
    console.print(f"[red]Error:[/red] {exc}")


@app.command()
def save(
    command: str = typer.Argument(
        ...,
        help="The shell command to save. This command is never executed.",
    ),
    as_alias: str = typer.Option(
        ...,
        "--as",
        help="Alias to assign to the command.",
    ),
) -> None:
    """Save a shell command under a named alias."""
    try:
        entry = saved_store.save(as_alias, command)
    except SavedCommandError as exc:
        _report_saved_command_error(exc)
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Saved[/green] [bold]{entry['alias']}[/bold]"
    )
    console.print(f"[cyan]{entry['command']}[/cyan]")
    console.print("[dim]The command was saved, not executed.[/dim]")


@app.command()
def saved(
    search: str | None = typer.Argument(
        None,
        help="Optional text to search in aliases and saved commands.",
    ),
) -> None:
    """List saved commands or search them."""
    try:
        entries = (
            saved_store.search(search)
            if search is not None
            else saved_store.list_all()
        )
    except SavedCommandError as exc:
        _report_saved_command_error(exc)
        raise typer.Exit(code=1) from exc

    if not entries:
        console.print("[yellow]No saved commands found.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title="Gideon's saved commands")
    table.add_column("Alias", style="cyan")
    table.add_column("Command")
    table.add_column("Created at", style="dim")

    for entry in entries:
        table.add_row(
            entry["alias"],
            entry["command"],
            entry["created_at"],
        )

    console.print(table)


@app.command()
def show(
    alias: str = typer.Argument(..., help="Alias to display."),
) -> None:
    """Display a saved command."""
    try:
        entry = saved_store.get(alias)
    except SavedCommandError as exc:
        _report_saved_command_error(exc)
        raise typer.Exit(code=1) from exc

    console.print(
        Panel(
            f"[bold cyan]{entry['alias']}[/bold cyan]\n\n"
            f"{entry['command']}",
            title="Saved command",
            border_style="cyan",
        )
    )
    console.print("[dim]The command was not executed.[/dim]")


@app.command()
def forget(
    alias: str = typer.Argument(..., help="Alias to remove."),
) -> None:
    """Delete a saved command."""
    try:
        entry = saved_store.delete(alias)
    except SavedCommandError as exc:
        _report_saved_command_error(exc)
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Forgot[/green] [bold]{entry['alias']}[/bold]"
    )


if __name__ == "__main__":
    app()
