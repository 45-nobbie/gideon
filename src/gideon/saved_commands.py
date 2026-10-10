
"""Local storage for Gideon's saved shell commands."""

import json
import os
import re
from pathlib import Path
from typing import Any


ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,49}$")


class SavedCommandError(Exception):
    """Base exception for saved-command operations."""


class AliasAlreadyExistsError(SavedCommandError):
    """Raised when an alias is already in use."""


class AliasNotFoundError(SavedCommandError):
    """Raised when a requested alias does not exist."""


class InvalidAliasError(SavedCommandError):
    """Raised when an alias does not meet naming rules."""


def _default_storage_path() -> Path:
    """Return the platform-appropriate configuration file path."""
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        config_dir = Path(base) if base else Path.home() / "AppData" / "Roaming"
    else:
        base = os.environ.get("XDG_CONFIG_HOME")
        config_dir = Path(base) if base else Path.home() / ".config"

    return config_dir / "gideon" / "saved_commands.json"


def _validate_alias(alias: str) -> None:
    """Reject aliases that are empty or unsafe for CLI use."""
    if not ALIAS_PATTERN.fullmatch(alias):
        raise InvalidAliasError(
            "Aliases must be 1–50 characters and contain only "
            "letters, numbers, underscores, or hyphens. "
            "They must start with a letter or number."
        )


class SavedCommandStore:
    """Persist named shell commands in a local JSON file."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else _default_storage_path()

    def _load(self) -> dict[str, dict[str, Any]]:
        """Load saved commands, returning an empty mapping if absent."""
        if not self.path.exists():
            return {}

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise SavedCommandError(
                f"Saved-command file contains invalid JSON: {self.path}"
            ) from exc

        if not isinstance(data, dict):
            raise SavedCommandError(
                "Saved-command file must contain a JSON object."
            )

        for alias, entry in data.items():
            if (
                not isinstance(alias, str)
                or not isinstance(entry, dict)
                or not isinstance(entry.get("command"), str)
                or not isinstance(entry.get("created_at"), str)
            ):
                raise SavedCommandError(
                    "Saved-command file has an invalid entry."
                )

        return data

    def _write(self, data: dict[str, dict[str, Any]]) -> None:
        """Write saved commands, creating the configuration directory."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")

        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                file.write("\n")

            temporary_path.replace(self.path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def save(self, alias: str, command: str) -> dict[str, Any]:
        """Save a command under a unique alias. Never executes it."""
        _validate_alias(alias)

        if not command or not command.strip():
            raise SavedCommandError("Command cannot be empty.")

        data = self._load()
        normalized_alias = alias.casefold()

        if any(key.casefold() == normalized_alias for key in data):
            raise AliasAlreadyExistsError(
                f"Alias '{alias}' already exists."
            )

        from datetime import datetime, timezone

        entry = {
            "command": command.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        data[alias] = entry
        self._write(data)
        return {"alias": alias, **entry}

    def list_all(self) -> list[dict[str, Any]]:
        """Return saved commands ordered by alias."""
        data = self._load()
        return [
            {"alias": alias, **entry}
            for alias, entry in sorted(
                data.items(),
                key=lambda item: item[0].casefold(),
            )
        ]

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search aliases and command text, ignoring case."""
        needle = query.strip().casefold()

        if not needle:
            return self.list_all()

        return [
            entry
            for entry in self.list_all()
            if needle in entry["alias"].casefold()
            or needle in entry["command"].casefold()
        ]

    def get(self, alias: str) -> dict[str, Any]:
        """Retrieve one saved command by case-insensitive alias."""
        data = self._load()

        for saved_alias, entry in data.items():
            if saved_alias.casefold() == alias.casefold():
                return {"alias": saved_alias, **entry}

        raise AliasNotFoundError(f"Alias '{alias}' was not found.")

    def delete(self, alias: str) -> dict[str, Any]:
        """Delete a saved command by case-insensitive alias."""
        data = self._load()

        matching_alias = next(
            (
                saved_alias
                for saved_alias in data
                if saved_alias.casefold() == alias.casefold()
            ),
            None,
        )

        if matching_alias is None:
            raise AliasNotFoundError(f"Alias '{alias}' was not found.")

        removed = {"alias": matching_alias, **data.pop(matching_alias)}
        self._write(data)
        return removed
