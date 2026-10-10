
from typer.testing import CliRunner

import gideon.cli as cli


runner = CliRunner()


def test_howto_uses_intent_generation(monkeypatch):
    monkeypatch.setattr(
        cli,
        "generate_from_intent",
        lambda query: {
            "command": "ls -la -- .",
            "explanation": [
                ("ls", "Lists directory contents."),
                ("-la", "Includes hidden files."),
            ],
            "intent": "list_files",
        },
    )

    result = runner.invoke(cli.app, ["howto", "show hidden files"])

    assert result.exit_code == 0
    assert "ls -la -- ." in result.output
    assert "Gideon has not executed this command." in result.output


def test_howto_falls_back_to_recipes(monkeypatch):
    monkeypatch.setattr(cli, "generate_from_intent", lambda query: None)
    monkeypatch.setattr(
        cli,
        "search_recipes",
        lambda query, shell: [
            (
                3,
                {
                    "id": "find-by-name",
                    "command": "find . -type f -name '*.log' -print",
                    "description": "Find files ending in .log.",
                    "shell": "bash",
                    "explanation": [
                        ("find", "Searches for files."),
                        ("-type f", "Matches regular files."),
                    ],
                },
            )
        ],
    )

    result = runner.invoke(cli.app, ["howto", "find log files"])

    assert result.exit_code == 0
    assert "find-by-name" in result.output
    assert "Find files ending in .log." in result.output


def test_howto_reports_when_no_match_exists(monkeypatch):
    monkeypatch.setattr(cli, "generate_from_intent", lambda query: None)
    monkeypatch.setattr(cli, "search_recipes", lambda query, shell: [])

    result = runner.invoke(cli.app, ["howto", "some unfamiliar task"])

    assert result.exit_code == 1
    assert "couldn't find a suitable command" in result.output
