
import shlex

from gideon.intents import IntentName, ParsedIntent


def build_du_command(intent: ParsedIntent) -> dict[str, object]:
    path = str(intent.parameters.get("path", "."))

    args = ["du", "-h", "--max-depth=1", "--", path]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("du", "Measures disk usage."),
            ("-h", "Displays sizes in human-readable units."),
            ("--max-depth=1", "Shows immediate subdirectories."),
            ("--", "Marks the end of command options."),
            (path, "The directory to inspect."),
        ],
        "intent": IntentName.DISK_USAGE.value,
    }


def build_df_command(intent: ParsedIntent) -> dict[str, object]:
    path = str(intent.parameters.get("path", "."))

    args = ["df", "-h", "--", path]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("df", "Reports filesystem space usage."),
            ("-h", "Displays sizes in human-readable units."),
            (path, "The path whose filesystem is inspected."),
        ],
        "intent": IntentName.FILESYSTEM_USAGE.value,
    }
