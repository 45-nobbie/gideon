
import pytest

from gideon.intents import IntentName
from gideon.parser import parse_intent


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("find all .log files", IntentName.FIND_FILES),
        ("find files larger than 500MB", IntentName.FIND_FILES),
        ("show disk usage of each directory", IntentName.DISK_USAGE),
        ("search for 'ERROR' in logs", IntentName.SEARCH_TEXT),
        ("show my IP addresses", IntentName.SHOW_INTERFACES),
        ("show listening ports", IntentName.SHOW_LISTENERS),
        ("show the routing table", IntentName.SHOW_ROUTES),
        ("show running processes", IntentName.SHOW_PROCESSES),
        ("show the Linux version", IntentName.SHOW_SYSTEM_INFO),
        ("list hidden files", IntentName.LIST_FILES),
        ("show hidden files", IntentName.LIST_FILES),
    ],
)
def test_recognizes_supported_intents(query, expected):
    result = parse_intent(query)
    assert result is not None
    assert result.name == expected


@pytest.mark.parametrize(
    "query",
    [
        "",
        "find me a way to make a sandwich",
        "tell me a joke",
        "make me a sandwich",
    ],
)
def test_rejects_unsupported_requests(query):
    assert parse_intent(query) is None


def test_extracts_file_search_parameters():
    result = parse_intent("find .log files larger than 500MB")

    assert result is not None
    assert result.name == IntentName.FIND_FILES
    assert result.parameters["extension"] == "log"
    assert result.parameters["size"] == 500
    assert result.parameters["size_unit"] == "MB"
    assert result.parameters["size_comparison"] == "greater"


def test_extracts_network_host():
    result = parse_intent("ping example.com")

    assert result is not None
    assert result.name == IntentName.CHECK_CONNECTIVITY
    assert result.parameters["host"] == "example.com"


def test_extracts_search_pattern():
    result = parse_intent("grep for 'TODO' in src")

    assert result is not None
    assert result.name == IntentName.SEARCH_TEXT
    assert result.parameters["pattern"] == "TODO"
    assert result.parameters["path"] == "src"
