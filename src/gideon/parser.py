
import re

from rich import text

from gideon.intents import IntentName, ParsedIntent


def parse_intent(query: str) -> ParsedIntent | None:
    """Convert a natural-language request into a structured intent."""
    text = query.lower().strip()

    if not text:
        return None

   
    # 1. Text search — extract the pattern and optional path together.
    text_search = re.search(
        r"(?:search for|grep for|find lines containing|"
        r"find text|search for text|look for)\s+"
        r"['\"]([^'\"]+)['\"]"
        r"(?:\s+(?:in|inside|under)\s+(.+))?",
        query,
        re.IGNORECASE,
    )

    if text_search:
        pattern = text_search.group(1)
        path = text_search.group(2) or "."

        return ParsedIntent(
            IntentName.SEARCH_TEXT,
            {
                "pattern": pattern,
                "path": path.strip(),
            },
        )


    if any(phrase in text for phrase in (
        "disk usage",
        "space used by each director",
        "size of each director",
    )):
        return ParsedIntent(
            IntentName.DISK_USAGE,
            {"path": "."},
        )

    if any(phrase in text for phrase in (
        "free disk space",
        "filesystem usage",
        "file system usage",
        "how much disk space is free",
    )):
        return ParsedIntent(IntentName.FILESYSTEM_USAGE)

    # 2. Networking
    if any(phrase in text for phrase in (
        "network interfaces",
        "show my ip address",
        "show ip addresses",
        "ip address of this machine",
    )):
        return ParsedIntent(IntentName.SHOW_INTERFACES)

    if any(phrase in text for phrase in (
        "listening ports",
        "listening sockets",
        "open ports",
        "what ports are listening",
    )):
        return ParsedIntent(IntentName.SHOW_LISTENERS)

    if any(phrase in text for phrase in (
        "routing table",
        "show routes",
        "show network routes",
        "default gateway",
    )):
        return ParsedIntent(IntentName.SHOW_ROUTES)


    # Networking: connectivity checks
    connectivity_patterns = (
        r"\bping\s+(?P<host>[a-zA-Z0-9.-]+)\b",
        r"\bcheck\s+(?:whether|if)\s+"
        r"(?P<host>[a-zA-Z0-9.-]+)\s+is\s+reachable\b",
        r"\bis\s+(?P<host>[a-zA-Z0-9.-]+)\s+reachable\b",
        r"\btest\s+connectivity\s+to\s+"
        r"(?P<host>[a-zA-Z0-9.-]+)\b",
    )

    for pattern in connectivity_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return ParsedIntent(
                IntentName.CHECK_CONNECTIVITY,
                {"host": match.group("host")},
            )


    resolution = re.search(
        r"(?:resolve|look up|lookup)\s+"
        r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        text,
    )

    if resolution:
        return ParsedIntent(
            IntentName.RESOLVE_HOSTNAME,
            {"hostname": resolution.group(1)},
        )

    if any(phrase in text for phrase in (
        "http request",
        "make a get request",
        "fetch this url",
    )):
        url = re.search(r"https?://[^\s'\"]+", query)

        if url:
            return ParsedIntent(
                IntentName.MAKE_HTTP_REQUEST,
                {"url": url.group(0)},
            )

        return None

    # 3. Processes and system information
    if any(phrase in text for phrase in (
        "running processes",
        "list processes",
        "show processes",
        "processes running",
    )):
        return ParsedIntent(IntentName.SHOW_PROCESSES)

    if any(phrase in text for phrase in (
        "system information",
        "linux version",
        "kernel version",
        "system uptime",
        "hostname",
        "who am i",
        "current user",
        "available memory",
        "memory usage",
    )):
        return ParsedIntent(
            IntentName.SHOW_SYSTEM_INFO,
            {"query": text},
        )

    # 4. File and directory operations
    if any(phrase in text for phrase in (
        "list files",
        "show files",
        "list directory",
        "show directory contents",
        "list hidden files",
        "show hidden files",
    )):
        return ParsedIntent(
            IntentName.LIST_FILES,
            {"path": ".", "query": text},
        )

    wants_file_search = any(phrase in text for phrase in (
        "find files",
        "find a file",
        "find all files",
        "search for files",
        "search for a file",
        "search files",
        "list files matching",
        "files modified",
        "files larger than",
        "files smaller than",
        "log files",
        "configuration files",
    ))

    if wants_file_search:
        parameters: dict[str, str | int | float | bool] = {
            "path": ".",
        }

        extension = re.search(
            r"\.([a-zA-Z0-9_-]+)\b",
            text,
        )

        if extension:
            parameters["extension"] = extension.group(1)

        size = re.search(
            r"\b(larger than|bigger than|over|greater than|"
            r"smaller than|less than|under)\s+"
            r"(\d+)\s*(kib|kb|mib|mb|gib|gb|tib|tb)\b",
            text,
        )

        if size:
            parameters["size_comparison"] = (
                "greater" if size.group(1) in (
                    "larger than", "bigger than", "over",
                    "greater than",
                ) else "less"
            )
            parameters["size"] = int(size.group(2))
            parameters["size_unit"] = size.group(3).upper()

        days = re.search(
            r"(?:last|past|within)\s+(\d+)\s+days?",
            text,
        )

        if days:
            parameters["days"] = int(days.group(1))

        return ParsedIntent(
            IntentName.FIND_FILES,
            parameters,
        )

    return None
