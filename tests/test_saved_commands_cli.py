import pytest
from typer.testing import CliRunner

import gideon.cli as cli
from gideon.saved_commands import SavedCommandStore


runner = CliRunner()


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    """Give each CLI test its own temporary command library."""
    store = SavedCommandStore(tmp_path / "saved_commands.json")
    monkeypatch.setattr(cli, "saved_store", store)
    return store


def test_save_command_through_cli(isolated_store):
    result = runner.invoke(
        cli.app,
        ["save", "grep -ri TODO src", "--as", "find-todos"],
    )

    assert result.exit_code == 0
    assert "Saved" in result.output
    assert "not executed" in result.output

    entry = isolated_store.get("find-todos")
    assert entry["command"] == "grep -ri TODO src"


def test_saved_lists_commands(isolated_store):
    isolated_store.save("find-todos", "grep TODO src")

    result = runner.invoke(cli.app, ["saved"])

    assert result.exit_code == 0
    assert "find-todos" in result.output
    assert "grep TODO src" in result.output


def test_saved_searches_command_text(isolated_store):
    isolated_store.save("find-todos", "grep TODO src")
    isolated_store.save("disk-check", "df -h")

    result = runner.invoke(cli.app, ["saved", "GREP"])

    assert result.exit_code == 0
    assert "find-todos" in result.output
    assert "disk-check" not in result.output


def test_saved_searches_alias(isolated_store):
    isolated_store.save("find-todos", "grep TODO src")
    isolated_store.save("disk-check", "df -h")

    result = runner.invoke(cli.app, ["saved", "FIND"])

    assert result.exit_code == 0
    assert "find-todos" in result.output
    assert "disk-check" not in result.output


def test_duplicate_alias_shows_readable_error(isolated_store):
    isolated_store.save("find-todos", "grep TODO src")

    result = runner.invoke(
        cli.app,
        ["save", "grep ERROR logs", "--as", "FIND-TODOS"],
    )

    assert result.exit_code != 0
    assert "already exists" in result.output
    assert "Traceback" not in result.output




def test_show_displays_command_without_executing_it(
    isolated_store, tmp_path
):
    marker = tmp_path / "should-not-exist"
    command = f"touch {marker}"
    isolated_store.save("test-command", command)

    result = runner.invoke(cli.app, ["show", "test-command"])

    assert result.exit_code == 0
    assert "test-command" in result.output
    assert "touch" in result.output
    assert "not executed" in result.output
    assert not marker.exists()





def test_show_missing_alias_shows_readable_error(isolated_store):
    result = runner.invoke(cli.app, ["show", "missing"])

    assert result.exit_code != 0
    assert "was not found" in result.output
    assert "Traceback" not in result.output


def test_forget_removes_saved_command(isolated_store):
    isolated_store.save("find-todos", "grep TODO src")

    result = runner.invoke(cli.app, ["forget", "find-todos"])

    assert result.exit_code == 0
    assert "Forgot" in result.output
    assert isolated_store.list_all() == []


def test_forget_missing_alias_shows_readable_error(isolated_store):
    result = runner.invoke(cli.app, ["forget", "missing"])

    assert result.exit_code != 0
    assert "was not found" in result.output
    assert "Traceback" not in result.output