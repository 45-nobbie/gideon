
from pydoc import text
import re
import shlex
from gideon.builders.files import build_find_command, build_grep_command
from gideon.builders.network import build_curl_command, build_interfaces_command, build_listeners_command, build_ping_command, build_resolve_command, build_routes_command
from gideon.builders.storage import build_df_command, build_du_command
from gideon.builders.system import build_ls_command, build_processes_command, build_system_info_command
from gideon.parser import parse_intent
from gideon.intents import IntentName
from gideon.builders import BUILDERS
from gideon.parser import parse_intent


def generate(query: str) -> dict[str, object] | None:
    """Generate a command for a supported natural-language request."""
    text = query.lower().strip()

    if not text:
        return None

    # Intent 1: Disk usage by directory
    if (
        "disk usage" in text
        or "space used by each director" in text
        or "size of each director" in text
    ):
        return {
            "command": "du -h --max-depth=1 .",
            "explanation": [
                ("du", "Measures disk usage."),
                ("-h", "Displays sizes in human-readable units."),
                ("--max-depth=1", "Shows the current directory and its immediate subdirectories."),
                (".", "Starts at the current directory."),
            ],
            "intent": "disk_usage",
        }

    # Intent 2: Find files

    file_search_phrases = (
        "find files",
        "find a file",
        "find all files",
        "search for files",
        "search for a file",
        "search files",
        "list files",
        "show me files",
        "show files",
        "locate files",
        "locate a file",
        "files modified",
        "files larger than",
        "files smaller than",
        "log files",
        "configuration files",
    )

    wants_find = any(
        phrase in text for phrase in file_search_phrases
    )

    if not wants_find:
        return None


    parts = ["find", ".", "-type", "f"]
    explanations = [
        ("find .", "Searches recursively from the current directory."),
        ("-type f", "Restricts results to regular files."),
    ]

    # File extension, e.g. .log or .conf
    extension_match = re.search(
        r"\.([a-zA-Z0-9_-]+)\b",
        text,
    )

    if extension_match:
        pattern = f"*.{extension_match.group(1)}"
        parts.extend(["-name", pattern])
        explanations.append(
            ("-name " + shlex.quote(pattern),
             "Matches filenames with this extension.")
        )

    # Size, e.g. 500MB or 2GB
    size_match = re.search(
        r"\b(?:larger than|bigger than|over|greater than)\s+"
        r"(\d+)\s*(kb|kib|mb|mib|gb|gib|tb|tib)\b",
        text,
    )

    if size_match:
        amount = size_match.group(1)
        unit = size_match.group(2).upper()
        unit_map = {
            "KB": "K", "KIB": "K",
            "MB": "M", "MIB": "M",
            "GB": "G", "GIB": "G",
            "TB": "T", "TIB": "T",
        }
        size_arg = f"+{amount}{unit_map[unit]}"
        parts.extend(["-size", size_arg])
        explanations.append(
            (f"-size {size_arg}",
             f"Matches files larger than approximately {amount} {unit}.")
        )

    # Modification age, e.g. last 7 days
    days_match = re.search(
        r"(?:last|past|within)\s+(\d+)\s+days?",
        text,
    )

    if days_match:
        days = days_match.group(1)
        parts.extend(["-mtime", f"-{days}"])
        explanations.append(
            (f"-mtime -{days}",
             f"Matches files modified less than {days} "
             "24-hour periods ago.")
        )

    parts.append("-print")
    explanations.append(
        ("-print", "Prints the paths of matching files.")
    )

    command = " ".join(
        shlex.quote(part) if part.startswith("*") else part
        for part in parts
    )

    return {
        "command": command,
        "explanation": explanations,
        "intent": "find_files",
    }


def generate_from_intent(query: str) -> dict[str, object] | None:
    """Parse a request and generate a command using a registered builder."""
    intent = parse_intent(query)

    if intent is None:
        return None

    builder = BUILDERS.get(intent.name)

    if builder is None:
        return None

    return builder(intent)


def generate_from_intent(query: str) -> dict[str, object] | None:
    """Parse a natural-language request and build a proposed command."""
    intent = parse_intent(query)

    if intent is None:
        return None

    builder = BUILDERS.get(intent.name)

    if builder is None:
        return None

    return builder(intent)
