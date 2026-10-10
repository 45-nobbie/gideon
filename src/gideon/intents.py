
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias


ParameterValue: TypeAlias = str | int | float | bool


class IntentName(str, Enum):
    # Files and text
    FIND_FILES = "find_files"
    SEARCH_TEXT = "search_text"
    LIST_FILES = "list_files"

    # Disk and storage
    DISK_USAGE = "disk_usage"
    FILESYSTEM_USAGE = "filesystem_usage"

    # Networking
    SHOW_INTERFACES = "show_interfaces"
    CHECK_CONNECTIVITY = "check_connectivity"
    SHOW_LISTENERS = "show_listeners"
    SHOW_ROUTES = "show_routes"
    RESOLVE_HOSTNAME = "resolve_hostname"
    MAKE_HTTP_REQUEST = "make_http_request"

    # Processes and system information
    SHOW_PROCESSES = "show_processes"
    SHOW_SYSTEM_INFO = "show_system_info"


@dataclass(frozen=True)
class ParsedIntent:
    """A recognized user request with structured parameters."""

    name: IntentName
    parameters: dict[str, ParameterValue] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandStage:
    """One executable and its arguments, without shell interpretation."""

    executable: str
    arguments: tuple[str, ...] = ()

    @property
    def argv(self) -> list[str]:
        """Return the argument vector suitable for subprocess.run."""
        return [self.executable, *self.arguments]


@dataclass(frozen=True)
class CommandPlan:
    """A proposed command or pipeline, not an executed command."""

    intent: IntentName
    stages: tuple[CommandStage, ...]
    explanation: tuple[tuple[str, str], ...] = ()
