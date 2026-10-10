
import json

import pytest

from gideon.saved_commands import (
    AliasAlreadyExistsError,
    AliasNotFoundError,
    InvalidAliasError,
    SavedCommandError,
    SavedCommandStore,
)


@pytest.fixture
def store(tmp_path):
    """Use a temporary file so tests never touch real saved commands."""
    return SavedCommandStore(tmp_path / "saved_commands.json")


def test_save_and_retrieve_command(store):
    saved = store.save("find-todos", "grep -ri TODO src")

    assert saved["alias"] == "find-todos"
    assert saved["command"] == "grep -ri TODO src"
    assert saved["created_at"]

    retrieved = store.get("find-todos")
    assert retrieved["command"] == "grep -ri TODO src"


def test_saved_commands_persist_between_store_instances(tmp_path):
    path = tmp_path / "saved_commands.json"

    first_store = SavedCommandStore(path)
    first_store.save("disk-check", "df -h")

    second_store = SavedCommandStore(path)
    assert second_store.get("disk-check")["command"] == "df -h"


def test_list_commands_is_sorted_by_alias(store):
    store.save("zebra", "ls")
    store.save("alpha", "pwd")
    store.save("middle", "df -h")

    aliases = [item["alias"] for item in store.list_all()]
    assert aliases == ["alpha", "middle", "zebra"]


def test_search_matches_alias_and_command_case_insensitively(store):
    store.save("find-todos", "grep -ri TODO src")
    store.save("disk-check", "df -h")

    alias_matches = store.search("FIND")
    assert [item["alias"] for item in alias_matches] == ["find-todos"]

    command_matches = store.search("GREP")
    assert [item["alias"] for item in command_matches] == ["find-todos"]


def test_empty_search_returns_all_commands(store):
    store.save("find-todos", "grep TODO src")
    store.save("disk-check", "df -h")

    assert len(store.search("")) == 2
    assert len(store.search("   ")) == 2


def test_duplicate_alias_is_rejected_case_insensitively(store):
    store.save("find-todos", "grep TODO src")

    with pytest.raises(AliasAlreadyExistsError):
        store.save("FIND-TODOS", "grep ERROR logs")


@pytest.mark.parametrize(
    "alias",
    [
        "",
        "two words",
        "-starts-with-hyphen",
        "semi;colon",
        "name/with/slash",
        "a" * 51,
    ],
)
def test_invalid_aliases_are_rejected(store, alias):
    with pytest.raises(InvalidAliasError):
        store.save(alias, "ls")


def test_empty_command_is_rejected(store):
    with pytest.raises(SavedCommandError):
        store.save("empty-command", "   ")


def test_missing_alias_raises_error(store):
    with pytest.raises(AliasNotFoundError):
        store.get("does-not-exist")


def test_delete_removes_command(store):
    store.save("disk-check", "df -h")

    removed = store.delete("disk-check")

    assert removed["alias"] == "disk-check"
    assert store.list_all() == []

    with pytest.raises(AliasNotFoundError):
        store.get("disk-check")


def test_delete_is_case_insensitive(store):
    store.save("disk-check", "df -h")

    removed = store.delete("DISK-CHECK")

    assert removed["alias"] == "disk-check"
    assert store.list_all() == []


def test_corrupt_json_raises_helpful_error(tmp_path):
    path = tmp_path / "saved_commands.json"
    path.write_text("{invalid json", encoding="utf-8")
    store = SavedCommandStore(path)

    with pytest.raises(SavedCommandError, match="invalid JSON"):
        store.list_all()


def test_invalid_entry_structure_is_rejected(tmp_path):
    path = tmp_path / "saved_commands.json"
    path.write_text(
        json.dumps({"broken": {"command": 123}}),
        encoding="utf-8",
    )
    store = SavedCommandStore(path)

    with pytest.raises(SavedCommandError, match="invalid entry"):
        store.list_all()


def test_saving_creates_parent_directory(tmp_path):
    path = tmp_path / "config" / "gideon" / "saved_commands.json"
    store = SavedCommandStore(path)

    store.save("disk-check", "df -h")

    assert path.exists()
    assert store.get("disk-check")["command"] == "df -h"
