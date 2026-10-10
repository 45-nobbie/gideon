
import shlex

from gideon.intents import CommandPlan, CommandStage, IntentName, ParsedIntent


def build_find_command(intent: ParsedIntent) -> dict[str, object]:
    path = str(intent.parameters.get("path", "."))
    args = [path, "-type", "f"]

    extension = intent.parameters.get("extension")
    if extension:
        args.extend(["-name", f"*.{extension}"])

    size = intent.parameters.get("size")
    unit = intent.parameters.get("size_unit")

    if size is not None and unit is not None:
        comparison = intent.parameters.get("size_comparison", "greater")
        unit_map = {
            "KB": "K",
            "KIB": "K",
            "MB": "M",
            "MIB": "M",
            "GB": "G",
            "GIB": "G",
            "TB": "T",
            "TIB": "T",
        }
        if unit not in unit_map:
            return {"error": f"Unsupported size unit: {unit}"}

        prefix = "+" if comparison == "greater" else "-"
        args.extend(["-size", f"{prefix}{size}{unit_map[unit]}"])

    days = intent.parameters.get("days")
    if days is not None:
        args.extend(["-mtime", f"-{days}"])

    args.append("-print")

    plan = CommandPlan(
        intent=IntentName.FIND_FILES,
        stages=(CommandStage("find", tuple(args)),),
    )

    return {
        "command": shlex.join(plan.stages[0].argv),
        "explanation": [
            ("find", "Searches for matching filesystem entries."),
            ("-type f", "Restricts results to regular files."),
            ("-print", "Prints the matching paths."),
        ],
        "intent": intent.name.value,
    }


def build_grep_command(intent: ParsedIntent) -> dict[str, object]:
    pattern = str(intent.parameters["pattern"])
    path = str(intent.parameters.get("path", "."))

    plan = CommandPlan(
        intent=IntentName.SEARCH_TEXT,
        stages=(
            CommandStage("grep", ("-rn", "--", pattern, path)),
        ),
    )

    return {
        "command": shlex.join(plan.stages[0].argv),
        "explanation": [
            ("grep", "Searches text using a pattern."),
            ("-r", "Searches directories recursively."),
            ("-n", "Displays line numbers."),
            ("--", "Marks the end of options."),
            (pattern, "The text pattern to search for."),
            (path, "The file or directory to search."),
        ],
        "intent": intent.name.value,
    }