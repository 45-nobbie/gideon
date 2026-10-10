
import re
import shlex
from urllib.parse import urlsplit

from gideon.intents import IntentName, ParsedIntent


def _valid_host(host: str) -> bool:
    if len(host) > 253:
        return False

    # Accept IPv4 literals or ordinary DNS names.
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        return all(int(part) <= 255 for part in host.split("."))

    return bool(
        re.fullmatch(
            r"(?=.{1,253}$)"
            r"(?:[a-zA-Z0-9]"
            r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
            r"(?:\.(?:[a-zA-Z0-9]"
            r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?))*",
            host,
        )
    )


def build_interfaces_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    args = ["ip", "addr"]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ip", "Inspects and manages network configuration."),
            ("addr", "Displays network interfaces and their addresses."),
        ],
        "intent": intent.name.value,
    }


def build_ping_command(intent: ParsedIntent) -> dict[str, object]:
    host = str(intent.parameters.get("host", ""))

    if not _valid_host(host):
        return {"error": "A valid hostname or IPv4 address is required."}

    args = ["ping", "-c", "4", "--", host]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ping", "Tests network reachability using ICMP."),
            ("-c 4", "Sends four probes, where supported."),
            (host, "The destination host."),
        ],
        "intent": IntentName.CHECK_CONNECTIVITY.value,
    }


def build_listeners_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    args = ["ss", "-lntup"]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ss", "Inspects socket information."),
            ("-l", "Shows listening sockets."),
            ("-n", "Displays numeric addresses and ports."),
            ("-t", "Includes TCP sockets."),
            ("-u", "Includes UDP sockets."),
            ("-p", "Shows process information when permitted."),
        ],
        "intent": intent.name.value,
    }


def build_routes_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    args = ["ip", "route", "show"]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("ip route show", "Displays the IPv4 routing table."),
        ],
        "intent": intent.name.value,
    }


def build_resolve_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    hostname = str(intent.parameters.get("hostname", ""))

    if not _valid_host(hostname):
        return {"error": "A valid hostname is required."}

    args = ["getent", "hosts", hostname]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("getent hosts", "Looks up addresses using configured name services."),
            (hostname, "The hostname to resolve."),
        ],
        "intent": intent.name.value,
    }


def build_curl_command(
    intent: ParsedIntent,
) -> dict[str, object]:
    url = str(intent.parameters.get("url", ""))
    parsed = urlsplit(url)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        return {
            "error": "A valid HTTP or HTTPS URL without embedded credentials is required."
        }

    if not _valid_host(parsed.hostname):
        return {"error": "The URL contains an invalid hostname."}

    args = ["curl", "--head", "--max-time", "10", "--", url]

    return {
        "command": shlex.join(args),
        "explanation": [
            ("curl", "Makes an HTTP request."),
            ("--head", "Requests response headers without the response body."),
            ("--max-time 10", "Limits the transfer time to ten seconds."),
            (url, "The target URL."),
        ],
        "intent": intent.name.value,
    }
