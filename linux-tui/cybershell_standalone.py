#!/usr/bin/env python3
"""CyberShell RPG v2.0 - Standalone Single-File Distribution Bundle.

Author: Amy (Project Lead & Master Integrator)
Role: Zero-dependency, single-file distribution bundle of CyberShell RPG v2.0.
      Packages contracts, in-memory VFS, command interpreter, double-border UI,
      hacker codex, and sector quests into an executable script for instant play.

Run with standard Python 3.8+:
    python3 cybershell_standalone.py
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import os
import posixpath
import re
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# =============================================================================
# PART 1: DAY 1 CONTRACTS & SHARED DTOS
# =============================================================================

DEFAULT_MAX_HP: int = 100
DEFAULT_BACKLASH_DAMAGE: int = 15
DEFAULT_HINT_PENALTY: int = 5

RANKS: List[Tuple[int, str]] = [
    (1, "Script Kiddie"),
    (2, "Junior Operative"),
    (3, "Cyber Mercenary"),
    (4, "Netrunner"),
    (5, "Daemon Infiltrator"),
    (6, "Root Architect"),
]


def calculate_rank(level: int) -> str:
    """Determine operative rank title based on level."""
    current_rank = RANKS[0][1]
    for lvl, title in RANKS:
        if level >= lvl:
            current_rank = title
        else:
            break
    return current_rank


@dataclass
class Item:
    """Inventory item representing hardware chips, exploits, keys, or consumables."""
    id: str
    name: str
    description: str
    category: str = "hardware"
    rarity: str = "common"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Item:
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "Unknown Item")),
            description=str(data.get("description", "")),
            category=str(data.get("category", "hardware")),
            rarity=str(data.get("rarity", "common")),
            properties=dict(data.get("properties", {})),
        )


@dataclass
class Objective:
    """Single quest objective evaluated against VFS or player state."""
    id: str
    description: str
    hint: str = ""
    predicate_type: str = "file_exists"
    predicate_target: str = ""
    predicate_expected: Any = True
    completed: bool = False
    xp_reward: int = 50

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Objective:
        return cls(
            id=str(data.get("id", "")),
            description=str(data.get("description", "")),
            hint=str(data.get("hint", "")),
            predicate_type=str(data.get("predicate_type", "file_exists")),
            predicate_target=str(data.get("predicate_target", "")),
            predicate_expected=data.get("predicate_expected", True),
            completed=bool(data.get("completed", False)),
            xp_reward=int(data.get("xp_reward", 50)),
        )


@dataclass
class Quest:
    """Sector mission containing narrative briefings and objectives."""
    id: str
    sector_id: int
    sector_name: str
    npc_name: str
    lore: str
    dialogue: List[str] = field(default_factory=list)
    objectives: List[Objective] = field(default_factory=list)
    reward_item: Optional[Item] = None
    reward_xp: int = 100
    completed: bool = False

    @property
    def is_completed(self) -> bool:
        if not self.objectives:
            return self.completed
        return all(obj.completed for obj in self.objectives)

    @property
    def current_objective(self) -> Optional[Objective]:
        for obj in self.objectives:
            if not obj.completed:
                return obj
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sector_id": self.sector_id,
            "sector_name": self.sector_name,
            "npc_name": self.npc_name,
            "lore": self.lore,
            "dialogue": list(self.dialogue),
            "objectives": [obj.to_dict() for obj in self.objectives],
            "reward_item": self.reward_item.to_dict() if self.reward_item else None,
            "reward_xp": self.reward_xp,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Quest:
        raw_reward = data.get("reward_item")
        reward_item = Item.from_dict(raw_reward) if raw_reward else None
        objectives = [Objective.from_dict(o) for o in data.get("objectives", [])]
        return cls(
            id=str(data.get("id", "")),
            sector_id=int(data.get("sector_id", 0)),
            sector_name=str(data.get("sector_name", "Unknown Sector")),
            npc_name=str(data.get("npc_name", "Handler")),
            lore=str(data.get("lore", "")),
            dialogue=list(data.get("dialogue", [])),
            objectives=objectives,
            reward_item=reward_item,
            reward_xp=int(data.get("reward_xp", 100)),
            completed=bool(data.get("completed", False)),
        )


@dataclass
class PlayerStats:
    """Player progression, hit points, rank, and inventory."""
    character_name: str = "Byte"
    hp: int = DEFAULT_MAX_HP
    max_hp: int = DEFAULT_MAX_HP
    xp: int = 0
    level: int = 1
    rank: str = "Script Kiddie"
    inventory: List[Item] = field(default_factory=list)
    current_sector: int = 0
    completed_sectors: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rank = calculate_rank(self.level)

    def take_damage(self, amount: int) -> int:
        if amount <= 0:
            return 0
        actual = min(self.hp, amount)
        self.hp = max(0, self.hp - amount)
        return actual

    def heal(self, amount: int) -> int:
        if amount <= 0:
            return 0
        missing = self.max_hp - self.hp
        restored = min(missing, amount)
        self.hp += restored
        return restored

    def gain_xp(self, amount: int) -> bool:
        if amount <= 0:
            return False
        self.xp += amount
        leveled_up = False
        while self.xp >= self.level * 100:
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.rank = calculate_rank(self.level)
            leveled_up = True
        return leveled_up

    def add_item(self, item: Item) -> bool:
        if any(existing.id == item.id for existing in self.inventory):
            return False
        self.inventory.append(item)
        return True

    def has_item(self, item_id: str) -> bool:
        return any(item.id == item_id for item in self.inventory)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "xp": self.xp,
            "level": self.level,
            "rank": self.rank,
            "inventory": [i.to_dict() for i in self.inventory],
            "current_sector": self.current_sector,
            "completed_sectors": list(self.completed_sectors),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlayerStats:
        inv = [Item.from_dict(i) for i in data.get("inventory", [])]
        return cls(
            character_name=str(data.get("character_name", "Byte")),
            hp=int(data.get("hp", DEFAULT_MAX_HP)),
            max_hp=int(data.get("max_hp", DEFAULT_MAX_HP)),
            xp=int(data.get("xp", 0)),
            level=int(data.get("level", 1)),
            rank=str(data.get("rank", "Script Kiddie")),
            inventory=inv,
            current_sector=int(data.get("current_sector", 0)),
            completed_sectors=list(data.get("completed_sectors", [])),
        )


@dataclass
class CommandResult:
    """Execution output and combat backlash report."""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    backlash_damage: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0

    @property
    def has_backlash(self) -> bool:
        return self.backlash_damage > 0


# =============================================================================
# PART 2: IN-MEMORY VIRTUAL FILESYSTEM (VFS)
# =============================================================================

class FSNode:
    """Base node inside the in-memory virtual filesystem."""
    def __init__(
        self,
        name: str,
        parent: Optional[DirectoryNode] = None,
        permissions: int = 0o644,
        owner: str = "root",
        group: str = "root",
    ) -> None:
        self.name: str = name
        self.parent: Optional[DirectoryNode] = parent
        self.permissions: int = permissions & 0o777
        self.owner: str = owner
        self.group: str = group
        self.created_at: float = time.time()
        self.modified_at: float = self.created_at

    @property
    def is_directory(self) -> bool:
        return isinstance(self, DirectoryNode)

    @property
    def is_file(self) -> bool:
        return isinstance(self, FileNode)

    def get_path(self) -> str:
        if self.parent is None:
            return "/" if self.is_directory else f"/{self.name}"
        parent_path = self.parent.get_path()
        return posixpath.join(parent_path, self.name)


class FileNode(FSNode):
    """File node with text read/write capabilities."""
    def __init__(
        self,
        name: str,
        content: str = "",
        parent: Optional[DirectoryNode] = None,
        permissions: int = 0o644,
        owner: str = "root",
        group: str = "root",
    ) -> None:
        super().__init__(name, parent, permissions, owner, group)
        self._content: str = content

    def read(self) -> str:
        return self._content

    def write(self, content: str) -> None:
        self._content = content
        self.modified_at = time.time()

    def append(self, content: str) -> None:
        self._content += content
        self.modified_at = time.time()

    @property
    def size(self) -> int:
        return len(self._content.encode("utf-8"))


class DirectoryNode(FSNode):
    """Directory node containing child nodes."""
    def __init__(
        self,
        name: str,
        parent: Optional[DirectoryNode] = None,
        permissions: int = 0o755,
        owner: str = "root",
        group: str = "root",
    ) -> None:
        super().__init__(name, parent, permissions, owner, group)
        self.children: Dict[str, FSNode] = {}

    def add_child(self, node: FSNode) -> None:
        node.parent = self
        self.children[node.name] = node
        self.modified_at = time.time()

    def remove_child(self, name: str) -> Optional[FSNode]:
        if name in self.children:
            removed = self.children.pop(name)
            self.modified_at = time.time()
            return removed
        return None

    def get_child(self, name: str) -> Optional[FSNode]:
        return self.children.get(name)


class VirtualFileSystem:
    """In-memory Linux Virtual Filesystem tree and path resolver."""
    def __init__(self, default_user: str = "operative") -> None:
        self.user = default_user
        self.home_dir = f"/home/{default_user}"
        self.root = DirectoryNode(name="", parent=None, permissions=0o755, owner="root")
        self.cwd: DirectoryNode = self.root

        for d in ["/bin", "/etc", "/home", self.home_dir, "/tmp", "/var", "/var/log"]:
            self.mkdir_p(d)
        self.cd(self.home_dir)

    def normalize_path(self, path: str) -> str:
        if path.startswith("~"):
            path = posixpath.join(self.home_dir, path[1:].lstrip("/"))
        if not path.startswith("/"):
            path = posixpath.join(self.get_cwd_path(), path)
        return posixpath.normpath(path)

    def get_cwd_path(self) -> str:
        return self.cwd.get_path()

    def cd(self, path: str = "~") -> str:
        norm = self.normalize_path(path)
        node = self.get_node(norm)
        if node is None:
            raise FileNotFoundError(f"cd: {path}: No such file or directory")
        if not node.is_directory:
            raise NotADirectoryError(f"cd: {path}: Not a directory")
        self.cwd = node  # type: ignore
        return self.get_cwd_path()

    def get_node(self, path: str) -> Optional[FSNode]:
        norm = self.normalize_path(path)
        if norm == "/":
            return self.root
        parts = [p for p in norm.split("/") if p]
        curr: FSNode = self.root
        for part in parts:
            if not curr.is_directory:
                return None
            curr = curr.get_child(part)  # type: ignore
            if curr is None:
                return None
        return curr

    def exists(self, path: str) -> bool:
        return self.get_node(path) is not None

    def list_dir(self, path: str = ".", show_hidden: bool = False) -> List[FSNode]:
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(f"ls: cannot access '{path}': No such file or directory")
        if not node.is_directory:
            return [node]
        dir_node: DirectoryNode = node  # type: ignore
        items = list(dir_node.children.values())
        if not show_hidden:
            items = [i for i in items if not i.name.startswith(".")]
        return sorted(items, key=lambda n: n.name.lower())

    def touch(self, path: str) -> FileNode:
        norm = self.normalize_path(path)
        parent_dir, name = posixpath.split(norm)
        p_node = self.get_node(parent_dir)
        if p_node is None or not p_node.is_directory:
            raise FileNotFoundError(f"touch: cannot touch '{path}': No such directory")
        existing = p_node.get_child(name)  # type: ignore
        if existing:
            if existing.is_file:
                existing.modified_at = time.time()
                return existing  # type: ignore
            raise IsADirectoryError(f"touch: '{path}' is a directory")
        new_file = FileNode(name=name, content="", permissions=0o644, owner=self.user)
        p_node.add_child(new_file)  # type: ignore
        return new_file

    def mkdir(self, path: str, permissions: int = 0o755) -> DirectoryNode:
        norm = self.normalize_path(path)
        parent_dir, name = posixpath.split(norm)
        p_node = self.get_node(parent_dir)
        if p_node is None or not p_node.is_directory:
            raise FileNotFoundError(f"mkdir: cannot create directory '{path}': No such file or directory")
        if p_node.get_child(name):  # type: ignore
            raise FileExistsError(f"mkdir: cannot create directory '{path}': File exists")
        new_dir = DirectoryNode(name=name, permissions=permissions, owner=self.user)
        p_node.add_child(new_dir)  # type: ignore
        return new_dir

    def mkdir_p(self, path: str, permissions: int = 0o755) -> DirectoryNode:
        norm = self.normalize_path(path)
        parts = [p for p in norm.split("/") if p]
        curr: DirectoryNode = self.root
        for part in parts:
            child = curr.get_child(part)
            if child is None:
                new_dir = DirectoryNode(name=part, permissions=permissions, owner=self.user)
                curr.add_child(new_dir)
                curr = new_dir
            elif child.is_directory:
                curr = child  # type: ignore
            else:
                raise NotADirectoryError(f"mkdir -p: '{child.get_path()}' is not a directory")
        return curr

    def read_file(self, path: str) -> str:
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(f"cat: {path}: No such file or directory")
        if not node.is_file:
            raise IsADirectoryError(f"cat: {path}: Is a directory")
        return node.read()  # type: ignore

    def write_file(self, path: str, content: str, append: bool = False) -> FileNode:
        norm = self.normalize_path(path)
        node = self.get_node(norm)
        if node is None:
            node = self.touch(norm)
        elif not node.is_file:
            raise IsADirectoryError(f"write: '{path}' is a directory")
        file_node: FileNode = node  # type: ignore
        if append:
            file_node.append(content)
        else:
            file_node.write(content)
        return file_node

    def chmod(self, path: str, mode: Union[int, str]) -> None:
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(f"chmod: cannot access '{path}': No such file or directory")
        if isinstance(mode, str):
            mode = int(mode, 8) if mode.isdigit() else 0o755
        node.permissions = mode & 0o777


# =============================================================================
# PART 3: ANSI FIXED-FRAME TUI RENDERER
# =============================================================================

ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", str(text))


def visual_len(text: str) -> int:
    return len(strip_ansi(text))


def terminal_size() -> Tuple[int, int]:
    try:
        size = shutil.get_terminal_size((80, 24))
        return max(size.columns, 80), max(size.lines, 24)
    except Exception:
        return 80, 24


def draw_double_header(
    character_name: str,
    hp: int,
    max_hp: int,
    xp: int,
    title: str,
    width: int,
) -> str:
    inner_width = max(width - 2, 10)
    pct = max(0.0, min(1.0, hp / max_hp)) if max_hp > 0 else 0.0
    filled = int(round(pct * 10))
    bar = "█" * filled + "░" * (10 - filled)
    left_str = f"OPERATIVE: {character_name}    HP: [{bar}] {int(pct * 100)}%    XP: {xp}"
    right_str = ""

    pad_top = inner_width - visual_len(left_str) - visual_len(right_str)
    line1 = f"║{left_str}{' ' * max(pad_top, 0)}{right_str}║"
    line2 = f"║{title.center(inner_width)}║"

    top_border = "╔" + "═" * inner_width + "╗"
    bottom_border = "╚" + "═" * inner_width + "╝"
    return f"{top_border}\n{line1}\n{line2}\n{bottom_border}"


def draw_split_panels(
    left_title: str,
    left_lines: List[str],
    right_title: str,
    right_lines: List[str],
    width: int,
    max_height: int = 12,
) -> str:
    col_width = (width - 4) // 2
    inner_w = col_width - 2

    def format_col(t: str, lines: List[str]) -> List[str]:
        out = [f"╭── {t} " + "─" * max(inner_w - visual_len(t) - 4, 0) + "╮"]
        for i in range(max_height):
            raw = lines[i] if i < len(lines) else ""
            clean = raw[:inner_w]
            pad = inner_w - visual_len(clean)
            out.append(f"│ {clean}{' ' * max(pad - 1, 0)}│")
        out.append("╰" + "─" * inner_w + "╯")
        return out

    left_box = format_col(left_title, left_lines)
    right_box = format_col(right_title, right_lines)

    rows = []
    for l_line, r_line in zip(left_box, right_box):
        rows.append(f"{l_line}  {r_line}")
    return "\n".join(rows)


# =============================================================================
# PART 4: HACKER CODEX & SECTOR CAMPAIGN QUESTS
# =============================================================================

CODEX_SPELLS = [
    ("pwd", "pwd", "Print working directory coordinates", "pwd"),
    ("ls", "ls [-la] [path]", "Scan and list directory nodes", "ls -la /home/operative"),
    ("cd", "cd <path>", "Traverse filesystem directory hierarchy", "cd /var/log"),
    ("cat", "cat <file>", "Read plain text content of targeted file", "cat flag.txt"),
    ("touch", "touch <file>", "Initialize empty file node in VFS", "touch security.lock"),
    ("mkdir", "mkdir [-p] <dir>", "Create memory directory partition", "mkdir -p /tmp/payload"),
    ("chmod", "chmod <mode> <file>", "Decouple/modify permission security shields", "chmod 755 run.sh"),
]

CAMPAIGN_QUESTS = [
    Quest(
        id="quest_0",
        sector_id=0,
        sector_name="Quarantine Zone",
        npc_name="Byte",
        lore="Corporate security placed your shell in an isolated sandbox.",
        dialogue=[
            "Operative! Wake up. The system has suffered memory corruption.",
            "Verify your coordinates with 'pwd', then inspect files with 'ls -la'.",
        ],
        objectives=[
            Objective("obj_0_1", "Run 'pwd' to check sector coordinates", "pwd", "cwd_equals", "/home/operative", True, False, 50),
            Objective("obj_0_2", "Run 'ls' or 'ls -la' to scan directory", "ls -la", "file_exists", "/home/operative", True, False, 50),
        ],
        reward_item=Item("chip_0", "Quarantine Bypass Chip", "Decrypts Sector 1 Security Gates.", "hardware", "rare"),
        reward_xp=100,
    ),
    Quest(
        id="quest_1",
        sector_id=1,
        sector_name="The File Vault",
        npc_name="Cipher",
        lore="The corporate ledger holds encrypted keys. Create an intrusion script.",
        dialogue=[
            "Good work escaping quarantine. Now create 'script.sh' with touch.",
            "Make it executable with 'chmod 755 script.sh'.",
        ],
        objectives=[
            Objective("obj_1_1", "Create 'script.sh' in home with touch", "touch script.sh", "file_exists", "/home/operative/script.sh", True, False, 50),
            Objective("obj_1_2", "Make 'script.sh' executable with 'chmod 755 script.sh'", "chmod 755 script.sh", "permission_equals", "/home/operative/script.sh", 0o755, False, 75),
        ],
        reward_item=Item("exploit_1", "Root Keyring", "Access to system services.", "cipher", "epic"),
        reward_xp=150,
    ),
]


# =============================================================================
# PART 5: INTERACTIVE GAME CONTROLLER
# =============================================================================

def execute_shell_command(vfs: VirtualFileSystem, cmd_str: str) -> CommandResult:
    line = cmd_str.strip()
    if not line:
        return CommandResult()

    parts = line.split()
    binary = parts[0]
    args = parts[1:]

    if binary == "pwd":
        return CommandResult(stdout=f"{vfs.get_cwd_path()}\n", exit_code=0)

    if binary == "cd":
        target = args[0] if args else "~"
        try:
            cwd = vfs.cd(target)
            return CommandResult(stdout="", exit_code=0, metadata={"cwd": cwd})
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    if binary == "ls":
        show_hidden = any(a in ("-a", "-la", "-al") for a in args)
        long_mode = any(a in ("-l", "-la", "-al") for a in args)
        target = "."
        for a in args:
            if not a.startswith("-"):
                target = a
                break
        try:
            nodes = vfs.list_dir(target, show_hidden=show_hidden)
            lines = []
            for n in nodes:
                if long_mode:
                    sym = ("d" if n.is_directory else "-") + "rwxr-xr-x"
                    lines.append(f"{sym}  {n.owner}  {n.name}")
                else:
                    lines.append(n.name)
            return CommandResult(stdout="\n".join(lines) + ("\n" if lines else ""), exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    if binary == "echo":
        text = " ".join(args).strip("'\"")
        return CommandResult(stdout=f"{text}\n", exit_code=0)

    if binary == "touch":
        if not args:
            return CommandResult(stderr="touch: missing file operand\n", exit_code=1)
        try:
            vfs.touch(args[0])
            return CommandResult(stdout="", exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    if binary == "mkdir":
        if not args:
            return CommandResult(stderr="mkdir: missing operand\n", exit_code=1)
        try:
            if "-p" in args:
                vfs.mkdir_p([a for a in args if a != "-p"][0])
            else:
                vfs.mkdir(args[0])
            return CommandResult(stdout="", exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    if binary == "cat":
        if not args:
            return CommandResult(stderr="cat: missing operand\n", exit_code=1)
        try:
            content = vfs.read_file(args[0])
            return CommandResult(stdout=content + ("\n" if not content.endswith("\n") else ""), exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    if binary == "chmod":
        if len(args) < 2:
            return CommandResult(stderr="chmod: missing operand\n", exit_code=1)
        try:
            vfs.chmod(args[1], args[0])
            return CommandResult(stdout="", exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"{err}\n", exit_code=1)

    # Electrical Backlash Damage on unknown syntax!
    return CommandResult(
        stdout="",
        stderr=f"cybershell: command not found: {binary}\n",
        exit_code=127,
        backlash_damage=DEFAULT_BACKLASH_DAMAGE,
    )


def run_standalone(character: str = "Byte", start_sector: int = 0) -> None:
    """Launch the self-contained CyberShell standalone game loop."""
    player = PlayerStats(character_name=character, hp=100, current_sector=start_sector)
    vfs = VirtualFileSystem(default_user="operative")
    active_sector_idx = start_sector
    quest = CAMPAIGN_QUESTS[active_sector_idx]

    ticker_msg = "CYBERSHELL v2.0 ONLINE // Zero-Dependency Standalone Edition"
    logs = [
        "operative@cybershell:~$ Mainframe session initialized.",
        "operative@cybershell:~$ Type 'help' or command to begin infiltration.",
    ]

    while True:
        width, _ = terminal_size()
        sys.stdout.write("\033[H\033[J")

        header = draw_double_header(
            player.character_name,
            player.hp,
            player.max_hp,
            player.xp,
            f"SECTOR {quest.sector_id}: {quest.sector_name.upper()}",
            width,
        )

        obj = quest.current_objective
        obj_text = obj.description if obj else "All Objectives Liberated! Sector Complete."
        intel = [
            f"Handler: [{quest.npc_name}]",
            f"Sector: {quest.sector_id} ({quest.sector_name})",
            f"Rank: {player.rank} (Level {player.level})",
            "",
            "--- ACTIVE DIRECTIVE ---",
            obj_text,
            "",
            f"Loot: {len(player.inventory)} items acquired",
            "Shortcuts: [codex] [map] [items] [help] [exit]",
        ]

        panels = draw_split_panels("SECTOR INTEL", intel, "CYBERSHELL CONSOLE", logs[-12:], width)
        sys.stdout.write(f"{header}\n{panels}\n[{ticker_msg}]\n")

        if player.hp <= 0:
            print("\n💀 ELECTRICAL BACKLASH OVERLOAD. OPERATIVE RESPAWNED IN SAFE MODE. 💀".center(width))
            player.hp = 100
            input("Press Enter to revive operative...")
            continue

        try:
            cwd_str = vfs.get_cwd_path().replace(f"/home/{vfs.user}", "~")
            cmd_in = input(f"operative@cybershell:{cwd_str}$ ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSafe shutdown initiated. Goodbye, operative.")
            break

        if not cmd_in:
            continue

        if cmd_in.lower() in ("exit", "quit"):
            print("Disconnecting from CyberShell mainframe...")
            break

        if cmd_in.lower() == "help":
            logs.append("operative@cybershell:~$ help")
            logs.append("Commands: pwd, cd, ls, cat, touch, mkdir, chmod, echo, clear, help")
            logs.append("Hacker Views: codex, map, items, exit")
            ticker_msg = "COMMAND ARCHIVES ACCESSED"
            continue

        if cmd_in.lower() == "clear":
            logs = []
            continue

        if cmd_in.lower() in ("codex", "2"):
            print("\n" + "=" * width)
            print("--- HACKER CODEX (SPELLBOOK) ---".center(width))
            for spell, syn, desc, comb in CODEX_SPELLS:
                print(f"  ⚡ {spell:<8} : {desc}")
                print(f"     Syntax: {syn} | Example: {comb}\n")
            input("Press Enter to return to mission...")
            continue

        if cmd_in.lower() in ("map", "4"):
            print("\n" + "=" * width)
            print("--- MAINFRAME TOPOLOGY MAP ---".center(width))
            for q in CAMPAIGN_QUESTS:
                status = "🟢 ACTIVE" if q.sector_id == player.current_sector else ("🔵 LIBERATED" if q.sector_id in player.completed_sectors else "🔒 LOCKED")
                print(f"  [{q.sector_id}] {q.sector_name:<24} Status: {status}")
            input("\nPress Enter to return to mission...")
            continue

        if cmd_in.lower() in ("items", "inventory", "3"):
            print("\n" + "=" * width)
            print("--- OPERATIVE INVENTORY ---".center(width))
            if not player.inventory:
                print("  [Inventory is currently empty]")
            for itm in player.inventory:
                print(f"  🎁 {itm.name} ({itm.rarity.upper()}) : {itm.description}")
            input("\nPress Enter to return to mission...")
            continue

        # Execute command in VFS
        logs.append(f"operative@cybershell:{cwd_str}$ {cmd_in}")
        res = execute_shell_command(vfs, cmd_in)

        if res.stdout:
            for ol in res.stdout.splitlines():
                logs.append(ol)
        if res.stderr:
            for el in res.stderr.splitlines():
                logs.append(f"\033[31m{el}\033[0m")

        # Combat backlash
        if res.has_backlash:
            dmg = player.take_damage(res.backlash_damage)
            ticker_msg = f"⚡ ELECTRICAL BACKLASH! -{dmg} HP (Syntax Shock)"
        else:
            ticker_msg = f"Command '{cmd_in.split()[0]}' executed."

        # Objective evaluation
        active_obj = quest.current_objective
        if active_obj and not active_obj.completed:
            satisfied = False
            bin_name = cmd_in.split()[0]
            if active_obj.id == "obj_0_1" and bin_name == "pwd":
                satisfied = True
            elif active_obj.id == "obj_0_2" and bin_name == "ls":
                satisfied = True
            elif active_obj.id == "obj_1_1" and vfs.exists("/home/operative/script.sh"):
                satisfied = True
            elif active_obj.id == "obj_1_2":
                nd = vfs.get_node("/home/operative/script.sh")
                if nd and nd.permissions == 0o755:
                    satisfied = True

            if satisfied:
                active_obj.completed = True
                leveled = player.gain_xp(active_obj.xp_reward)
                ticker_msg = f"🎯 OBJECTIVE FULFILLED! +{active_obj.xp_reward} XP"
                if leveled:
                    ticker_msg += f" 🌟 LEVEL UP! Rank: {player.rank}"

                if quest.is_completed:
                    quest.completed = True
                    player.completed_sectors.append(quest.sector_id)
                    if quest.reward_item:
                        player.add_item(quest.reward_item)
                        ticker_msg += f" 🎁 LOOT: {quest.reward_item.name}!"
                    if active_sector_idx + 1 < len(CAMPAIGN_QUESTS):
                        active_sector_idx += 1
                        player.current_sector = active_sector_idx
                        quest = CAMPAIGN_QUESTS[active_sector_idx]
                        ticker_msg += f" 🚀 ADVANCING TO SECTOR {active_sector_idx}!"


def main() -> int:
    parser = argparse.ArgumentParser(description="CyberShell Standalone Distribution")
    parser.add_argument("--name", "-n", default="Byte", help="Operative name")
    parser.add_argument("--sector", "-s", type=int, default=0, help="Start sector")
    parser.add_argument("--demo", action="store_true", help="Show demo and exit")
    args = parser.parse_args()

    if args.demo:
        w, _ = terminal_size()
        hdr = draw_double_header(args.name, 100, 100, 50, "STANDALONE DEMO", w)
        print(hdr)
        return 0

    run_standalone(args.name, args.sector)
    return 0


if __name__ == "__main__":
    sys.exit(main())
