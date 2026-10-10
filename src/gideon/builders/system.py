
import shlex

from gideon.intents import IntentName, ParsedIntent


def build_processes_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    args = ["ps", "aux"]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ps", "Reports process information."),
            ("aux", "Shows processes across users with detailed resource information."),
        ],
        "intent": intent.name.value,
    }


def build_system_info_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    query = str(intent.parameters.get("query", "")).lower()

    if "uptime" in query:
        args = ["uptime"]
        meaning = "Shows how long the system has been running and its load averages."
    elif "hostname" in query:
        args = ["hostname"]
        meaning = "Displays the system hostname."
    elif "who am i" in query or "current user" in query:
        args = ["whoami"]
        meaning = "Displays the effective username."
    elif "memory" in query:
        args = ["free", "-h"]
        meaning = "Displays memory and swap usage in human-readable units."
    elif " id" in f" {query}" or query.strip() == "id":
        args = ["id"]
        meaning = "Displays the current user's identity and group memberships."
    else:
        args = ["uname", "-a"]
        meaning = "Displays kernel and basic system information."

    return {
        "command": shlex.join(args),
        "explanation": [(shlex.join(args), meaning)],
        "intent": IntentName.SHOW_SYSTEM_INFO.value,
    }


def build_ls_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    path = str(intent.parameters.get("path", "."))
    query = str(intent.parameters.get("query", "")).lower()

    args = ["ls"]

    if "hidden" in query:
        args.append("-la")
    else:
        args.append("-l")

    args.extend(["--", path])

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ls", "Lists directory contents."),
            (args[1], "Displays detailed information, including hidden files when requested."),
            (path, "The directory to list."),
        ],
        "intent": IntentName.LIST_FILES.value,
    }
