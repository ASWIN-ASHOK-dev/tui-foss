"""Hacker Codex - Tactical Command Encyclopedia for CyberShell RPG v2.0.

Author: Akash (Hacker Codex & Chmod Minigame)
Role: An in-game "TLDR spellbook" describing Linux/security commands, their
      flags, examples, and tactical pipeline combos. Designed so additional
      commands can be added simply by registering another entry.

Entries are stored as plain dictionaries (schema below) so they are easy to
extend, while ``CodexEntry`` DTO contract objects can be produced on demand
for integration with the rest of the game:

    {
        "name": "ls",
        "description": "...",
        "syntax": "...",
        "flags": {"-l": "...", "-a": "..."},
        "examples": ["..."],
        "combos": ["..."]
    }
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from cybershell.contracts import CodexEntry

# Schema of a registered codex entry.
REQUIRED_KEYS: Tuple[str, ...] = ("name", "description", "syntax", "flags", "examples", "combos")

# ---------------------------------------------------------------------------
# Command database
# ---------------------------------------------------------------------------

COMMANDS: Dict[str, Dict[str, Any]] = {
    "ls": {
        "name": "ls",
        "description": "List directory contents - scan a sector for loot, keys, and agents.",
        "syntax": "ls [options] [path]",
        "flags": {
            "-l": "Long format: show permissions, owner, and size (STUX scan).",
            "-a": "Include hidden files - ghost signals often lurk in dotfiles.",
            "-la": "Composite: long format plus hidden files.",
        },
        "examples": [
            "ls",
            "ls -la",
            "ls -l /var/log",
        ],
        "combos": [
            "ls → cd → cat   # scope the sector, move in, read the intel",
        ],
    },
    "cd": {
        "name": "cd",
        "description": "Change the working directory - navigate the mainframe tree.",
        "syntax": "cd [path]",
        "flags": {
            "~": "Jump to the operative home node.",
            "..": "Move one level up the directory tree.",
            "-": "Return to the previous working directory.",
        },
        "examples": [
            "cd /tmp",
            "cd ..",
            "cd ~/logs",
        ],
        "combos": [
            "ls → cd → cat   # recon a sector, then tunnel deeper and read intel",
        ],
    },
    "cat": {
        "name": "cat",
        "description": "Concatenate files to stdout - dump file contents into the terminal.",
        "syntax": "cat [file...]",
        "flags": {
            "-n": "Number all output lines (indexed intel).",
            "-A": "Show all characters including invisible control glyphs.",
        },
        "examples": [
            "cat mission_brief.txt",
            "cat -n logs.txt",
        ],
        "combos": [
            "cat /var/log/auth.log → grep 'Failed'   # surface failed entry attempts",
        ],
    },
    "grep": {
        "name": "grep",
        "description": "Search text for patterns - filter a stream for the intel that matters.",
        "syntax": "grep [options] PATTERN [file...]",
        "flags": {
            "-i": "Case-insensitive match - ignore case while hunting.",
            "-r": "Recursive search through directories.",
            "-n": "Show line numbers of matches.",
            "-c": "Count matching lines instead of printing them.",
        },
        "examples": [
            "grep 'password' logs.txt",
            "grep -r 'ACCESS' /etc",
            "grep -c 'ERROR' app.log",
        ],
        "combos": [
            "find → grep → cat   # locate the file, filter it, then read the prize",
            "cat logs.txt | grep 'denied'",
        ],
    },
    "chmod": {
        "name": "chmod",
        "description": "Change file permission bits - reforge access codes on secured nodes.",
        "syntax": "chmod [mode] [file]",
        "flags": {
            "755": "rwxr-xr-x: owner full access, group/others read+execute.",
            "644": "rw-r--r--: owner read/write, group/others read-only.",
            "600": "rw-------: private file, owner-only access.",
            "700": "rwx------: private executable, owner-only access.",
        },
        "examples": [
            "chmod 755 script.sh",
            "chmod 600 credentials.key",
            "chmod -R 700 /secure",
        ],
        "combos": [
            "chmod 755 script.sh → ./script.sh   # arm and fire a payload",
            "chmod 600 secrets.txt → cat secrets.txt",
        ],
    },
    "rm": {
        "name": "rm",
        "description": "Remove files or directories - purge evidence and cleanup trails.",
        "syntax": "rm [options] [target...]",
        "flags": {
            "-r": "Recursive removal of a directory tree.",
            "-f": "Force removal, ignore missing operands.",
            "-i": "Prompt before every removal - a cautious touch.",
        },
        "examples": [
            "rm temp.log",
            "rm -r old_sector_data",
            "rm -f crash_dumps/*.dmp",
        ],
        "combos": [
            "rm -r /var/log → shutdown   # scrub the node before you ghost out",
        ],
    },
    "touch": {
        "name": "touch",
        "description": "Create an empty file or stamp a timestamp - spawn a fresh node.",
        "syntax": "touch [file]",
        "flags": {
            "-a": "Update the access time only.",
            "-m": "Update the modification time only.",
        },
        "examples": [
            "touch payload.sh",
            "touch /tmp/beacon.txt",
        ],
        "combos": [
            "touch key.txt → echo 'CYBER_KEY' > key.txt   # fabricate a marker, then fill it",
        ],
    },
    "mkdir": {
        "name": "mkdir",
        "description": "Create directories - establish new sectors in the tree.",
        "syntax": "mkdir [options] [dir]",
        "flags": {
            "-p": "Create parent directories as required (no error if existing).",
            "-v": "Verbose output for each directory crafted.",
        },
        "examples": [
            "mkdir drops",
            "mkdir -p /tmp/vault/keys",
        ],
        "combos": [
            "mkdir -p /tmp/ops → cd /tmp/ops → touch log.txt   # stage an operation node",
        ],
    },
}


# ---------------------------------------------------------------------------
# Codex registry / lookup API
# ---------------------------------------------------------------------------

class Codex:
    """Encyclopedia of commands with lookup, search, and display helpers."""

    def __init__(self, entries: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Build a codex. Defaults to the built-in command database."""
        self._commands: Dict[str, Dict[str, Any]] = dict(
            entries if entries is not None else COMMANDS
        )
        self._validate_entries()

    # -- internal helpers ---------------------------------------------------

    def _validate_entries(self) -> None:
        """Ensure every registered command follows the expected schema."""
        for name, data in self._commands.items():
            if not isinstance(name, str) or not name:
                raise ValueError(f"Codex command name must be a non-empty string: {name!r}")
            for key in REQUIRED_KEYS:
                if key not in data:
                    raise ValueError(f"Codex entry for {name!r} is missing key {key!r}")
            if data.get("name") != name:
                message = (
                    f"Codex entry key {name!r} does not match entry name {data.get('name')!r}"
                )
                raise ValueError(message)
            if not isinstance(data["flags"], dict):
                raise ValueError(f"Codex entry for {name!r}: 'flags' must be a dict")
            if not isinstance(data.get("examples"), list):
                raise ValueError(f"Codex entry for {name!r}: 'examples' must be a list")
            if not isinstance(data.get("combos"), list):
                raise ValueError(f"Codex entry for {name!r}: 'combos' must be a list")

    # -- retrieval ----------------------------------------------------------

    def command_names(self) -> List[str]:
        """Return sorted command names registered in the codex."""
        return sorted(self._commands)

    def has_command(self, name: str) -> bool:
        """Return True when a command exists in the codex."""
        return str(name).strip().lower() in self._commands

    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a command record, or None when it is unknown."""
        return self._commands.get(str(name).strip().lower())

    def get_command_data(self, name: str) -> Optional[Dict[str, Any]]:
        """Alias of :meth:`get_command` returning the full dictionary record."""
        return self.get_command(name)

    def list_commands(self) -> List[Dict[str, Any]]:
        """Return all command records sorted alphabetically by name."""
        return [self._commands[name] for name in self.command_names()]

    def get_flags(self, name: str) -> Dict[str, str]:
        """Retrieve the flags for a command, or an empty dict when unknown."""
        entry = self.get_command(name)
        return dict(entry["flags"]) if entry else {}

    def get_combos(self, name: str) -> List[str]:
        """Retrieve tactical command combos for a command."""
        entry = self.get_command(name)
        return list(entry["combos"]) if entry else []

    def get_examples(self, name: str) -> List[str]:
        """Retrieve usage examples for a command."""
        entry = self.get_command(name)
        return list(entry["examples"]) if entry else []

    # -- search -------------------------------------------------------------

    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Case-insensitive search across names, descriptions, flags, and combos."""
        needle = str(query).strip().lower()
        if not needle:
            return []
        matches: List[Dict[str, Any]] = []
        for entry in self.list_commands():
            haystack = [str(entry["name"]), str(entry["description"]), str(entry["syntax"])]
            haystack.extend(str(k) for k in entry["flags"])
            haystack.extend(str(v) for v in entry["flags"].values())
            haystack.extend(str(e) for e in entry["examples"])
            haystack.extend(str(c) for c in entry["combos"])
            if any(needle in token.lower() for token in haystack):
                matches.append(entry)
        return matches

    # -- display ------------------------------------------------------------

    def to_codex_entry(self, name: str) -> Optional[CodexEntry]:
        """Convert a command record into the shared ``CodexEntry`` DTO."""
        data = self.get_command(name)
        if not data:
            return None
        return CodexEntry(
            command=data["name"],
            syntax=data["syntax"],
            description=data["description"],
            flags=dict(data["flags"]),
            combos=list(data["combos"]),
        )

    def display_command(self, name: str, width: int = 60) -> str:
        """Render a full command detail card, or an error notice when unknown."""
        entry = self.get_command(name)
        if not entry:
            return f"[ CODEX // UNKNOWN ENTRY ] No intel on command {name!r}."

        marker = "=" * max(10, width)
        lines = [
            marker,
            f"[ HACKER CODEX // {entry['name']} ]",
            marker,
            f"Syntax: {entry['syntax']}",
            f"Summary: {entry['description']}",
            "",
        ]
        if entry["flags"]:
            lines.append("Flags:")
            for flag, meaning in entry["flags"].items():
                lines.append(f"  {flag:<8} {meaning}")
            lines.append("")
        if entry["examples"]:
            lines.append("Examples:")
            lines.extend(f"  > {example}" for example in entry["examples"])
            lines.append("")
        if entry["combos"]:
            lines.append("Tactical combos:")
            lines.extend(f"  » {combo}" for combo in entry["combos"])
        return "\n".join(lines)

    def display_list(self) -> str:
        """Render a compact overview of every registered command."""
        lines = ["[ HACKER CODEX // SPELLBOOK OVERVIEW ]"]
        for entry in self.list_commands():
            lines.append(f"  {entry['name']:<10} {entry['description']}")
        lines.append("")
        lines.append("Type a command name to decrypt its full entry.")
        return "\n".join(lines)


# Convariance: default module-level codex + convenience functions so both
# object-oriented and functional call styles are supported.

CODEX: Codex = Codex()


def get_command(name: str) -> Optional[Dict[str, Any]]:
    """Retrieve a command record from the default codex."""
    return CODEX.get_command(name)


def list_commands() -> List[Dict[str, Any]]:
    """List all commands registered in the default codex."""
    return CODEX.list_commands()


def command_names() -> List[str]:
    """Return the names of all commands in the default codex."""
    return CODEX.command_names()


def search_commands(query: str) -> List[Dict[str, Any]]:
    """Search the default codex for a query string."""
    return CODEX.search_commands(query)


def get_flags(name: str) -> Dict[str, str]:
    """Retrieve a command's flags from the default codex."""
    return CODEX.get_flags(name)


def get_combos(name: str) -> List[str]:
    """Retrieve a command's tactical combos from the default codex."""
    return CODEX.get_combos(name)


def get_examples(name: str) -> List[str]:
    """Retrieve a command's examples from the default codex."""
    return CODEX.get_examples(name)


def display_command(name: str) -> str:
    """Render a full command detail card from the default codex."""
    return CODEX.display_command(name)


def display_list() -> str:
    """Render the compact overview of all commands in the default codex."""
    return CODEX.display_list()


__all__ = [
    "COMMANDS",
    "REQUIRED_KEYS",
    "Codex",
    "CODEX",
    "get_command",
    "list_commands",
    "command_names",
    "search_commands",
    "get_flags",
    "get_combos",
    "get_examples",
    "display_command",
    "display_list",
]
