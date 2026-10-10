
import pytest

from gideon.generator import generate


@pytest.mark.parametrize(
    "query",
    [
        "find me a way to make a sandwich",
        "show me how to learn Python",
        "list the best movies",
        "how do I find my way home",
        "make me a sandwich",
    ],
)
def test_unrelated_requests_are_rejected(query):
    assert generate(query) is None


@pytest.mark.parametrize(
    "query",
    [
        "find all log files",
        "show me files",
        "list files modified in the last 3 days",
        "find files larger than 500MB",
    ],
)
def test_file_search_requests_are_recognized(query):
    result = generate(query)
    assert result is not None
    assert result["intent"] == "find_files"


def test_log_file_search_quotes_wildcard():
    result = generate("find files ending in .log")

    assert result is not None
    assert result["command"] == "find . -type f -name '*.log' -print"
