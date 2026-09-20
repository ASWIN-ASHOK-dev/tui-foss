#!/usr/bin/env python3
"""CyberShell RPG v2.0 - Main Executable Launcher.

Author: Amy (Project Lead & Master Integrator)
Role: CLI launcher, argument parser, environment bootstrapper,
      and main game loop controller.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import sys
import textwrap
from typing import Any, Dict, List, Optional, Tuple

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    readline = None
    READLINE_AVAILABLE = False

# Ensure src/ and project root are on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == "cybershell":
    SRC_DIR = os.path.dirname(SCRIPT_DIR)
else:
    SRC_DIR = os.path.join(SCRIPT_DIR, "src")
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cybershell import __version__
from cybershell.contracts import (
    DEFAULT_BACKLASH_DAMAGE,
    CommandResult,
    Item,
    Objective,
    PlayerStats,
    Quest,
)
from cybershell.engine.node import DirectoryNode, FSNode
from cybershell.engine.vfs import VirtualFileSystem
from cybershell.engine.interpreter import Interpreter
from cybershell.game.evaluator import QuestEvaluator
from cybershell.game.quests import get_sector_quests
from cybershell.tools.chmod_minigame import ChmodMinigame
from cybershell.tools.codex import Codex
from cybershell.tools.map import MainframeMap
from cybershell.ui.ascii_art import (
    BLUE,
    BOLD,
    CYAN,
    DIM,
    GREEN,
    MAGENTA,
    RED,
    RESET,
    WHITE,
    YELLOW,
    format_boss_hp_bar,
    get_logo,
    get_portrait,
    get_siren_banner,
)
from cybershell.ui.renderer import (
    draw_double_header,
    draw_panel,
    draw_split_panels,
    pad_to_width,
    terminal_size,
    visual_len,
)
from cybershell.ui.rpg_app import RPGApp


def wrap_text(text: str, width: int, prefix: str = "", style: str = "") -> List[str]:
    """Wrap text into readable complete sentences fitting width."""
    width = max(10, width)
    raw_text = str(text).strip()
    if not raw_text:
        return []
    lines = textwrap.wrap(raw_text, width=max(10, width - len(prefix)))
    if not lines:
        return [f"{style}{prefix}{RESET}"]
    reset = RESET if style else ""
    return [
        f"{style}{prefix if i == 0 else ' ' * len(prefix)}{line}{reset}"
        for i, line in enumerate(lines)
    ]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="cybershell",
        description="CyberShell RPG v2.0 - Terminal-based Linux & Cyber Adventure",
    )
    parser.add_argument(
        "--name", "-n",
        default="Byte",
        help="Operative codename (default: Byte)",
    )
    parser.add_argument(
        "--sector", "-s",
        type=int,
        default=0,
        help="Starting sector ID (0-5, default: 0)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run UI demo showcase and exit",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run quick architectural smoke tests and exit",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"CyberShell RPG v{__version__}",
    )
    return parser.parse_args()


def run_smoke_test() -> int:
    """Execute Amy's integration test suite as a diagnostic pre-flight check."""
    import unittest
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    if not os.path.isdir(tests_dir):
        tests_dir = "tests"
    suite = unittest.defaultTestLoader.discover(tests_dir, pattern="test_integration.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


# =============================================================================
# PERSISTENCE & BEGINNER-FRIENDLY ASSIST TOOLS
# =============================================================================

SAVE_FILE_PATH = os.path.expanduser("~/.cybershell_save.json")


def save_game(
    player: PlayerStats,
    cadet_mode: bool = True,
    filepath: str = SAVE_FILE_PATH,
) -> bool:
    """Save player progression and game settings to JSON checkpoint file."""
    try:
        data = {
            "character_name": player.character_name,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "xp": player.xp,
            "level": player.level,
            "rank": player.rank,
            "current_sector": player.current_sector,
            "completed_sectors": list(player.completed_sectors),
            "inventory": [item.to_dict() for item in player.inventory],
            "cadet_mode": cadet_mode,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_saved_game(
    filepath: str = SAVE_FILE_PATH,
) -> Optional[Tuple[PlayerStats, bool]]:
    """Load player progression and game settings from checkpoint file."""
    if not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        player = PlayerStats(
            character_name=str(data.get("character_name", "Byte")),
            hp=int(data.get("hp", 100)),
            max_hp=int(data.get("max_hp", 100)),
            xp=int(data.get("xp", 0)),
            current_sector=int(data.get("current_sector", 0)),
        )
        player.level = int(data.get("level", 1))
        player.rank = str(data.get("rank", "Cadet"))
        player.completed_sectors = set(data.get("completed_sectors", []))
        raw_inv = data.get("inventory", [])
        for item_dict in raw_inv:
            if isinstance(item_dict, dict):
                player.add_item(Item.from_dict(item_dict))
        cadet_mode = bool(data.get("cadet_mode", True))
        return player, cadet_mode
    except Exception:
        return None


def delete_saved_game(filepath: str = SAVE_FILE_PATH) -> bool:
    """Remove checkpoint save file."""
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False


KNOWN_COMMANDS = [
    "pwd", "ls", "cd", "cat", "touch", "mkdir", "chmod", "grep",
    "clear", "help", "hint", "tree", "explain", "menu", "codex",
    "items", "inventory", "map", "minigame", "cadet", "operative",
    "save", "exit", "quit",
]


def check_typo_or_syntax(cmd_str: str) -> Optional[Tuple[str, str]]:
    """Analyze command input for common beginner typos and missing spaces.

    Returns (suggested_command, coaching_explanation) if detected, else None.
    """
    raw = cmd_str.strip()
    if not raw:
        return None

    # Missing space after cd: cd.., cd/, cd~
    if raw.startswith("cd") and len(raw) > 2 and raw[2] in (".", "/", "~", "$"):
        suggested = f"cd {raw[2:]}"
        return (
            suggested,
            "In Linux, 'cd' requires a space before the destination path.",
        )

    # Missing space after ls: ls-la, ls-l, ls-a
    if raw.startswith("ls-"):
        suggested = f"ls -{raw[3:]}"
        return (
            suggested,
            "Command options require a space after 'ls' (e.g., 'ls -la').",
        )

    # Missing space after cat: catfile.txt -> cat file.txt
    if raw.startswith("cat") and len(raw) > 3 and raw[3] not in (" ", "-"):
        suggested = f"cat {raw[3:]}"
        return (
            suggested,
            "'cat' requires a space before the filename argument.",
        )

    # Common command misspellings
    typo_map = {
        "pdw": ("pwd", "'pwd' stands for Print Working Directory."),
        "pwd.": ("pwd", "Do not include a trailing dot after 'pwd'."),
        "sl": ("ls", "'ls' is used to list directory files."),
        "lss": ("ls", "'ls' is used to list directory files."),
        "cpt": ("cat", "'cat' is used to display file contents."),
        "caat": ("cat", "'cat' is used to display file contents."),
        "toush": ("touch", "'touch' creates an empty file."),
        "touh": ("touch", "'touch' creates an empty file."),
        "mrdir": ("mkdir", "'mkdir' creates a new directory folder."),
        "mdkir": ("mkdir", "'mkdir' creates a new directory folder."),
        "chomd": ("chmod", "'chmod' modifies file access permissions."),
        "chmdo": ("chmod", "'chmod' modifies file access permissions."),
        "gerp": ("grep", "'grep' searches files for matching text patterns."),
        "grpe": ("grep", "'grep' searches files for matching text patterns."),
        "clera": ("clear", "'clear' wipes the terminal display."),
        "claer": ("clear", "'clear' wipes the terminal display."),
        "clea": ("clear", "'clear' wipes the terminal display."),
        "exlpain": ("explain", "'explain' shows syntax breakdowns for commands."),
        "explayn": ("explain", "'explain' shows syntax breakdowns for commands."),
    }
    first_token = raw.split()[0].lower()
    if first_token in typo_map:
        corr, explanation = typo_map[first_token]
        rest = raw[len(first_token):]
        return (f"{corr}{rest}", explanation)

    # Check 1-character edit distance against known commands
    if len(first_token) >= 3 and first_token not in KNOWN_COMMANDS:
        for known in KNOWN_COMMANDS:
            if abs(len(first_token) - len(known)) <= 1:
                diffs = sum(
                    1 for a, b in zip(first_token, known) if a != b
                ) + abs(len(first_token) - len(known))
                if diffs == 1:
                    rest = raw[len(first_token):]
                    return (
                        f"{known}{rest}",
                        f"Command '{first_token}' is not recognized.",
                    )

    return None


def render_vfs_tree(
    start_node: DirectoryNode,
    max_depth: int = 3,
) -> List[str]:
    """Render a visual directory tree of VFS folders and files with Unicode branches."""
    root_name = start_node.name or "/"
    lines: List[str] = [f"{BLUE}{BOLD}{root_name}{RESET}"]

    def _walk(dir_node: DirectoryNode, prefix: str, current_depth: int) -> None:
        if current_depth > max_depth:
            return
        items = sorted(
            dir_node.children.items(),
            key=lambda x: (not x[1].is_directory, x[0]),
        )
        total = len(items)
        for i, (name, child) in enumerate(items):
            is_last = (i == total - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "
            if child.is_directory:
                lines.append(f"{prefix}{connector}{BLUE}{BOLD}{name}/{RESET}")
                _walk(child, prefix + child_prefix, current_depth + 1)
            else:
                color = GREEN if (child.permissions & 0o111) else WHITE
                lines.append(f"{prefix}{connector}{color}{name}{RESET}")

    _walk(start_node, "", 1)
    return lines


def colorize_ls_output(stdout: str) -> List[str]:
    """Colorize directory contents in 'ls' and 'ls -la' output."""
    lines: List[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            lines.append("")
            continue
        parts = line.split()
        if len(parts) >= 6 and len(parts[0]) in (9, 10):
            perms = parts[0]
            filename = " ".join(parts[5:])
            prefix_str = " ".join(parts[:5])
            if perms.startswith("d"):
                colored_name = f"{BLUE}{BOLD}{filename}/{RESET}"
            elif "x" in perms:
                colored_name = f"{GREEN}{BOLD}{filename}{RESET}"
            elif filename.startswith("."):
                colored_name = f"{DIM}{filename}{RESET}"
            else:
                colored_name = f"{WHITE}{filename}{RESET}"
            lines.append(f"{prefix_str} {colored_name}")
        else:
            colored_tokens: List[str] = []
            for token in parts:
                if token.endswith("/"):
                    colored_tokens.append(f"{BLUE}{BOLD}{token}{RESET}")
                elif token.startswith("."):
                    colored_tokens.append(f"{DIM}{token}{RESET}")
                else:
                    colored_tokens.append(f"{WHITE}{token}{RESET}")
            lines.append("  ".join(colored_tokens) if colored_tokens else line)
    return lines


class VFSTabCompleter:
    """Interactive command and path autocompleter using readline."""

    def __init__(self, vfs: VirtualFileSystem):
        self.vfs = vfs
        self.commands = list(KNOWN_COMMANDS)

    def complete(self, text: str, state: int) -> Optional[str]:
        """Return match for text at given state index."""
        begidx = readline.get_begidx() if readline else 0

        if begidx == 0:
            matches = [c for c in self.commands if c.startswith(text)]
        else:
            try:
                prefix = text
                dirname, basename = posixpath.split(prefix)
                target_node = self.vfs.cwd
                if dirname:
                    resolved = self.vfs.resolve_path(dirname)
                    if resolved and resolved.is_directory:
                        target_node = resolved
                matches = []
                for name, child in target_node.children.items():
                    if name.startswith(basename):
                        full_match = posixpath.join(dirname, name) if dirname else name
                        if child.is_directory:
                            full_match += "/"
                        matches.append(full_match)
            except Exception:
                matches = []

        if state < len(matches):
            return matches[state]
        return None


def setup_tab_completion(vfs: VirtualFileSystem) -> None:
    """Configure readline tab completion for shell commands and VFS files."""
    if not READLINE_AVAILABLE or readline is None:
        return
    completer = VFSTabCompleter(vfs)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")
    try:
        readline.set_completer_delims(" \t\n")
    except Exception:
        pass


def get_progressive_hint(
    active_obj: Objective,
    tier: int,
    cadet_mode: bool = True,
) -> Tuple[str, int]:
    """Return progressive 3-tier hint and associated HP penalty.

    - Tier 1 (Concept): General guidance (0 HP Cadet / 2 HP Operative).
    - Tier 2 (Syntax): Expected command syntax pattern (0 HP Cadet / 3 HP Operative).
    - Tier 3 (Direct): Exact command solution (0 HP Cadet / 5 HP Operative).
    """
    if tier == 1:
        msg = f"[HINT TIER 1 // CONCEPT] Focus on the directive objective: {active_obj.description}"
        cost = 0 if cadet_mode else 2
    elif tier == 2:
        syntax_tip = active_obj.syntax if active_obj.syntax else active_obj.command
        msg = f"[HINT TIER 2 // SYNTAX PATTERN] Use the syntax: {syntax_tip}"
        cost = 0 if cadet_mode else 3
    else:
        sol = active_obj.command if active_obj.command else (active_obj.hint or "Execute directive.")
        msg = f"[HINT TIER 3 // DIRECT SOLUTION] Enter exact command: {sol}"
        cost = 0 if cadet_mode else 5
    return msg, cost


def explain_command(
    cmd_input: str,
    active_obj: Optional[Objective] = None,
) -> List[str]:
    """Provide an interactive, beginner-friendly breakdown of command syntax."""
    tokens = cmd_input.strip().split()
    if len(tokens) <= 1:
        if active_obj and active_obj.command:
            return [
                f"{YELLOW}{BOLD}[ ACTIVE DIRECTIVE COMMAND EXPLANATION ]{RESET}",
                f"  {CYAN}Command:{RESET} {WHITE}{BOLD}{active_obj.command}{RESET}",
                f"  {CYAN}Syntax:{RESET}  {YELLOW}{active_obj.syntax}{RESET}",
                f"  {CYAN}Purpose:{RESET} {WHITE}{active_obj.explanation}{RESET}",
                f"  {DIM}Type 'explain <cmd>' to inspect any other command (e.g. 'explain chmod 755 run.sh').{RESET}",
            ]
        return [
            f"{YELLOW}[ COMMAND EXPLAINER ]{RESET}",
            f"{WHITE}Type 'explain <command>' to break down syntax, flags, and arguments.{RESET}",
            f"{DIM}Examples: 'explain ls -la', 'explain chmod 755 script.sh', 'explain grep error log.txt'{RESET}",
        ]

    cmd = tokens[1].lower()
    args = tokens[2:]

    lines = [f"{YELLOW}{BOLD}[ COMMAND BREAKDOWN: {' '.join(tokens[1:])} ]{RESET}"]

    if cmd == "pwd":
        lines.append(f"  {CYAN}pwd{RESET} : 'Print Working Directory'. Outputs your full coordinates.")
        lines.append(f"  {WHITE}No arguments are needed. It returns your current folder path.{RESET}")
    elif cmd == "ls":
        lines.append(f"  {CYAN}ls{RESET} : 'List'. Displays files and folders in directory.")
        if any("-l" in a for a in args) or any("l" in a for a in args if a.startswith("-")):
            lines.append(f"  {YELLOW}-l{RESET} : Long listing format (shows permissions, owner, size, and date).")
        if any("-a" in a for a in args) or any("a" in a for a in args if a.startswith("-")):
            lines.append(f"  {YELLOW}-a{RESET} : All files including hidden files starting with a dot (e.g. .env).")
        targets = [a for a in args if not a.startswith("-")]
        if targets:
            lines.append(f"  {WHITE}Target path(s): {', '.join(targets)}{RESET}")
    elif cmd == "cd":
        lines.append(f"  {CYAN}cd{RESET} : 'Change Directory'. Moves your shell session to another folder.")
        dest = args[0] if args else "~"
        if dest == "..":
            lines.append(f"  {YELLOW}..{RESET} : Moves up one level to the parent directory.")
        elif dest in ("~", ""):
            lines.append(f"  {YELLOW}~{RESET}  : Shortcut for your operative home directory (/home/operative).")
        elif dest == "/":
            lines.append(f"  {YELLOW}/{RESET}  : Jumps directly to the mainframe root directory.")
        else:
            lines.append(f"  {WHITE}Navigates to: {dest}{RESET}")
    elif cmd == "cat":
        lines.append(f"  {CYAN}cat{RESET} : 'Concatenate'. Reads and prints file contents to your screen.")
        if args:
            lines.append(f"  {WHITE}Files to read: {', '.join(args)}{RESET}")
    elif cmd == "touch":
        lines.append(f"  {CYAN}touch{RESET} : Creates a new empty file or updates its timestamp.")
        if args:
            lines.append(f"  {WHITE}Target file(s) to create: {', '.join(args)}{RESET}")
    elif cmd == "mkdir":
        lines.append(f"  {CYAN}mkdir{RESET} : 'Make Directory'. Creates a new folder.")
        if "-p" in args:
            lines.append(f"  {YELLOW}-p{RESET} : Creates parent directories automatically as needed.")
        dirs = [a for a in args if not a.startswith("-")]
        if dirs:
            lines.append(f"  {WHITE}Folder(s) to create: {', '.join(dirs)}{RESET}")
    elif cmd == "chmod":
        lines.append(f"  {CYAN}chmod{RESET} : 'Change Mode'. Modifies file read, write, and execute permissions.")
        if args:
            mode = args[0]
            lines.append(f"  {YELLOW}Mode {mode}{RESET} : 3 octal digits [Owner][Group][Others].")
            lines.append(f"    • 4 = Read (r), 2 = Write (w), 1 = Execute (x)")
            if mode == "755":
                lines.append(f"    • 7 (4+2+1=rwx) for Owner, 5 (4+0+1=r-x) for Group & Others.")
            elif mode == "644":
                lines.append(f"    • 6 (4+2+0=rw-) for Owner, 4 (4+0+0=r--) for Group & Others.")
            elif mode == "700":
                lines.append(f"    • 7 (rwx) for Owner, 0 (---) for others (strictly private).")
            if len(args) > 1:
                lines.append(f"  {WHITE}Target file: {args[1]}{RESET}")
    elif cmd == "grep":
        lines.append(f"  {CYAN}grep{RESET} : 'Global Regular Expression Print'. Searches lines for matching text.")
        if args:
            lines.append(f"  {YELLOW}Search pattern:{RESET} '{args[0]}'")
            if len(args) > 1:
                lines.append(f"  {WHITE}Target file:{RESET} '{args[1]}'")
    elif cmd == "tree":
        lines.append(f"  {CYAN}tree{RESET} : Displays a visual hierarchy tree of directories and files.")
    elif cmd == "clear":
        lines.append(f"  {CYAN}clear{RESET} : Wipes the terminal console logs for a clean display.")
    else:
        lines.append(f"  {WHITE}Command '{cmd}' recognized. Type 'codex' for its tactical manual entry.{RESET}")

    return lines


# =============================================================================
# DEDICATED OPENING SCREEN & NAVIGATION
# =============================================================================

def render_opening_screen(
    player: PlayerStats,
    width: int = 80,
    cadet_mode: bool = True,
    has_save: bool = False,
) -> str:
    """Render the primary opening screen displaying the name, description, and navigation options."""
    width = max(60, width)
    inner_w = max(40, width - 4)

    # 1. ASCII Title Logo & Header
    logo_raw = get_logo(styled=True)
    logo_lines = [
        pad_to_width(line, width, align="center")
        for line in logo_raw.strip("\n").splitlines()
    ]

    # 2. Operative status line
    hp_pct = max(0, min(10, int((player.hp / max(1, player.max_hp)) * 10)))
    hp_bar = f"{GREEN}{'█' * hp_pct}{RED}{'░' * (10 - hp_pct)}{RESET}"
    mode_tag = (
        f"{GREEN}[CADET: SAFE]{RESET}"
        if cadet_mode
        else f"{RED}[OPERATIVE: -15 HP]{RESET}"
    )
    status_text_1 = (
        f"{CYAN}Operative:{RESET} {WHITE}{BOLD}{player.character_name}{RESET}  "
        f"{YELLOW}Rank:{RESET} {player.rank} (Lvl {player.level})  "
        f"{RED}HP:{RESET} [{hp_bar}] {player.hp}/{player.max_hp}  "
        f"{MAGENTA}XP:{RESET} {player.xp}"
    )
    status_text_2 = (
        f"{CYAN}Security Clearance:{RESET} Active  |  "
        f"{YELLOW}Difficulty:{RESET} {mode_tag}"
    )
    status_line_1 = pad_to_width(status_text_1, width, align="center")
    status_line_2 = pad_to_width(status_text_2, width, align="center")

    border_double = f"{CYAN}{'═' * width}{RESET}"
    border_single = f"{DIM}{'─' * width}{RESET}"

    # 3. Complete Sentences Description of What CyberShell Does
    about_title = f"{YELLOW}{BOLD}[ WHAT IS CYBERSHELL? ]{RESET}"
    desc_p1 = (
        "CyberShell is an interactive terminal-based cyberpunk role-playing game "
        "designed to help you learn and master real Linux command-line skills, filesystem "
        "navigation, file inspection, and system security."
    )
    desc_p2 = (
        "You play as an elite terminal operative infiltrating a compromised corporate mainframe. "
        "By executing genuine Linux commands against an in-memory virtual filesystem, you must "
        "bypass security firewalls, inspect critical data, reconfigure file permissions, "
        "and liberate core sectors from rogue AI daemons."
    )
    desc_p3 = (
        "In Cadet Mode, electrical backlash damage is waived to ensure a safe learning "
        "environment. In Operative Mode, syntax errors cause -15 HP electrical backlash. "
        "Every sector features exactly 3 focused directives with syntax guidance directly on screen."
    )

    about_lines = [
        f"  {about_title}",
        "",
    ]
    for p in (desc_p1, desc_p2, desc_p3):
        for w_line in textwrap.wrap(p, width=inner_w):
            about_lines.append(f"  {WHITE}{w_line}{RESET}")
        about_lines.append("")

    # 4. Navigation Options
    menu_title = f"{GREEN}{BOLD}[ MAIN DIRECTORY // SELECT STATION ]{RESET}"
    mode_label = "CADET (SAFE)" if cadet_mode else "OPERATIVE (HARD)"

    if has_save:
        options = [
            ("1", "Continue Campaign", f"Resume Sector {player.current_sector} active directives"),
            ("2", "New Campaign", "Start fresh infiltration from Sector 0"),
            ("3", "Hacker Codex", "Tactical command reference & keyword search"),
            ("4", "Operative Inventory", "Inspect hardware tokens, chips, and loot"),
            ("5", "Tactical Map", "Mainframe sector topology & status map"),
            ("6", "Security Lockpick", "Chmod octal permission hacking for bonus XP"),
            ("7", "Field Manual & Rules", "Review combat rules, tools, and controls"),
            ("8", "Toggle Mode", f"Switch mode (Currently: {mode_label})"),
            ("0", "Exit CyberShell", "Safely disconnect from terminal session"),
        ]
    else:
        options = [
            ("1", "Learning Interface", "Interactive Mission Lab campaign & directives"),
            ("2", "Hacker Codex", "Tactical command reference & keyword search"),
            ("3", "Operative Inventory", "Inspect hardware tokens, chips, and loot"),
            ("4", "Tactical Map", "Mainframe sector topology & status map"),
            ("5", "Security Lockpick", "Chmod octal permission hacking for bonus XP"),
            ("6", "Field Manual & Rules", "Review combat rules, tools, and controls"),
            ("7", "Toggle Mode", f"Switch mode (Currently: {mode_label})"),
            ("0", "Exit CyberShell", "Safely disconnect from terminal session"),
        ]

    menu_lines = [
        f"  {menu_title}",
        "",
    ]
    for num, label, summary in options:
        prefix = f"  {YELLOW}{BOLD}[{num}]{RESET}  {CYAN}{BOLD}{label:<23}{RESET}"
        menu_lines.append(f"{prefix} {WHITE}{summary}{RESET}")

    all_lines = (
        logo_lines
        + ["", status_line_1, status_line_2, border_double, ""]
        + about_lines
        + [border_single, ""]
        + menu_lines
        + ["", border_double]
    )
    return "\n".join(all_lines)


# =============================================================================
# DEDICATED SCREEN VIEWERS
# =============================================================================

def view_codex(codex: Codex, player: PlayerStats, width: int) -> None:
    """Display the Hacker Codex tactical command archive with search capability."""
    while True:
        sys.stdout.write("\033[H\033[J")
        header = draw_double_header(
            player.character_name,
            player.hp,
            player.max_hp,
            player.xp,
            "HACKER CODEX // TACTICAL ARCHIVE",
            width,
            styled=True,
        )
        print(header)
        print()
        print(f"  {YELLOW}{BOLD}[ HACKER CODEX // TACTICAL COMMAND ARCHIVE ]{RESET}")
        desc = (
            "The Hacker Codex is your tactical archive of essential Linux commands and system tools. "
            "Enter any command name or search keyword (e.g. 'read', 'permission', 'navigate') "
            "to decrypt its full manual entry, syntax flags, and operational examples."
        )
        for line in textwrap.wrap(desc, width=width - 4):
            print(f"  {WHITE}{line}{RESET}")
        print()
        print(f"  {CYAN}{BOLD}AVAILABLE COMMANDS:{RESET}")
        cmds = [entry["name"] for entry in codex.list_commands()]
        chunk_size = 4
        for i in range(0, len(cmds), chunk_size):
            chunk = cmds[i : i + chunk_size]
            formatted = "    ".join(f"{GREEN}{cmd:<8}{RESET}" for cmd in chunk)
            print(f"    {formatted}")
        print()
        print(f"  {DIM}{'─' * (width - 4)}{RESET}")
        try:
            term = input(
                f"  {YELLOW}Enter command or keyword (or press Enter / '0' to return to menu): {RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not term or term in ("0", "q", "quit", "exit", "back", "menu"):
            break

        entry_text = codex.display_command(term)
        if "Unknown command" not in entry_text:
            print()
            print(f"  {MAGENTA}{BOLD}=== DECRYPTION RESULT: {term.upper()} ==={RESET}")
            for e_line in entry_text.splitlines():
                print(f"  {WHITE}{e_line}{RESET}")
        else:
            term_lower = term.lower()
            matches = [
                entry for entry in codex.list_commands()
                if term_lower in entry["name"].lower()
                or term_lower in entry.get("description", "").lower()
                or term_lower in entry.get("category", "").lower()
            ]
            if matches:
                print()
                print(f"  {YELLOW}{BOLD}=== SEARCH RESULTS FOR '{term}' ({len(matches)} match{'es' if len(matches) > 1 else ''}) ==={RESET}")
                for m in matches:
                    print(f"    • {GREEN}{BOLD}{m['name']:<8}{RESET} : {WHITE}{m.get('description', '')}{RESET}")
            else:
                print(f"\n  {RED}No commands or keywords matching '{term}' found in Codex.{RESET}")

        try:
            input(f"\n  {YELLOW}Press Enter to return to command list...{RESET}")
        except (KeyboardInterrupt, EOFError):
            break


def view_inventory(player: PlayerStats, width: int) -> None:
    """Display the Operative Inventory and hardware tokens."""
    sys.stdout.write("\033[H\033[J")
    header = draw_double_header(
        player.character_name,
        player.hp,
        player.max_hp,
        player.xp,
        "OPERATIVE INVENTORY & LOOT",
        width,
        styled=True,
    )
    print(header)
    print()
    print(f"  {YELLOW}{BOLD}[ OPERATIVE HARDWARE TOKENS & CHIPS ]{RESET}")
    desc = (
        "Hardware tokens, cryptographic exploits, and system chips acquired by liberating mainframe sectors. "
        "These artifacts prove your security clearance across the network."
    )
    for line in textwrap.wrap(desc, width=width - 4):
        print(f"  {WHITE}{line}{RESET}")
    print()
    if not player.inventory:
        print(f"  {DIM}Your inventory is currently empty.{RESET}")
        print(f"  {CYAN}Complete sector objectives in the Learning Interface to earn loot items!{RESET}")
    else:
        for idx, itm in enumerate(player.inventory, start=1):
            rarity_col = MAGENTA if itm.rarity in ("epic", "legendary", "mythic") else GREEN
            print(f"  [{idx}] 🎁 {WHITE}{BOLD}{itm.name}{RESET} [{rarity_col}{itm.rarity.upper()}{RESET}] ({itm.category.upper()})")
            print(f"       {CYAN}{itm.description}{RESET}")
            print()
    print(f"  {DIM}{'─' * (width - 4)}{RESET}")
    try:
        input(f"  {YELLOW}Press Enter to return to Main Menu...{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass


def view_map(mainframe: MainframeMap, player: PlayerStats, all_quests: Dict[int, Quest], width: int) -> None:
    """Display the Tactical Mainframe Map and sector progression status."""
    sys.stdout.write("\033[H\033[J")
    mainframe.apply_progression(player)
    header = draw_double_header(
        player.character_name,
        player.hp,
        player.max_hp,
        player.xp,
        "TACTICAL MAINFRAME NETWORK MAP",
        width,
        styled=True,
    )
    print(header)
    print()
    print(f"  {YELLOW}{BOLD}[ MAINFRAME NETWORK TOPOLOGY ]{RESET}")
    desc = (
        "The network map charts the 6 key sectors of the corporate mainframe. "
        "Infiltrate each sector sequentially in the Learning Interface to purge rogue daemons."
    )
    for line in textwrap.wrap(desc, width=width - 4):
        print(f"  {WHITE}{line}{RESET}")
    print()
    for m_line in mainframe.render().splitlines():
        print(f"  {m_line}")
    print()
    print(f"  {YELLOW}{BOLD}SECTOR TELEMETRY STATUS:{RESET}")
    for sid in range(6):
        q_info = all_quests.get(sid)
        sec_name = q_info.sector_name if q_info else f"Sector {sid}"
        if sid == player.current_sector:
            status_str = f"{GREEN}🟢 CURRENT TARGET (ACTIVE INFILTRATION){RESET}"
        elif sid in player.completed_sectors:
            status_str = f"{BLUE}🔵 LIBERATED (PERIMETER SECURED){RESET}"
        else:
            status_str = f"{RED}🔒 LOCKED (DEFENSIVE SHIELDS ENGAGED){RESET}"
        print(f"    [{sid}] {WHITE}{sec_name:<24}{RESET} Status: {status_str}")
    print()
    print(f"  {DIM}{'─' * (width - 4)}{RESET}")
    try:
        input(f"  {YELLOW}Press Enter to return to Main Menu...{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass


def view_minigame(minigame: ChmodMinigame, player: PlayerStats, width: int) -> None:
    """Run the interactive Chmod Lockpicking Minigame for bonus XP."""
    minigame.set_player(player)
    while True:
        sys.stdout.write("\033[H\033[J")
        header = draw_double_header(
            player.character_name,
            player.hp,
            player.max_hp,
            player.xp,
            "SECURITY LOCKPICK // CHMOD PUZZLE",
            width,
            styled=True,
        )
        print(header)
        print()
        print(f"  {YELLOW}{BOLD}[ CHMOD PERMISSION LOCKPICK CHALLENGE ]{RESET}")
        desc = (
            "Security doors on the corporate mainframe are sealed with Unix permission locks. "
            "Convert the 9-character permission string into its 3-digit octal notation (e.g., rwxr-xr-x = 755) "
            "to breach the door and extract bonus operative XP."
        )
        for line in textwrap.wrap(desc, width=width - 4):
            print(f"  {WHITE}{line}{RESET}")
        print()
        puzzle = minigame.generate_puzzle()
        door_lines = minigame.render_door().splitlines()
        for d_line in door_lines:
            print(f"  {d_line}")
        print()
        try:
            guess = input(
                f"  {YELLOW}Enter 3-digit octal code for '{puzzle.permission}' (or 'q' to return to menu): {RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not guess or guess.lower() in ("q", "quit", "0", "exit", "back", "menu"):
            break

        result = minigame.validate_answer(guess)
        if result.correct:
            print(f"\n  {GREEN}{BOLD}{result.message}{RESET}")
            if result.xp_awarded > 0:
                print(f"  {GREEN}🎉 +{result.xp_awarded} XP awarded to {player.character_name}! Current XP: {player.xp}{RESET}")
            try:
                input(f"\n  {YELLOW}Press Enter for next security door...{RESET}")
            except (KeyboardInterrupt, EOFError):
                break
        else:
            print(f"\n  {RED}{BOLD}{result.message}{RESET}")
            try:
                input(f"\n  {YELLOW}Press Enter to try another lock...{RESET}")
            except (KeyboardInterrupt, EOFError):
                break


def view_field_manual(width: int) -> None:
    """Display the Field Manual, combat rules, and command guide."""
    sys.stdout.write("\033[H\033[J")
    header = draw_double_header(
        "OPERATIVE",
        100,
        100,
        0,
        "FIELD MANUAL & RULES",
        width,
        styled=True,
    )
    print(header)
    print()
    sections = [
        ("OPERATIONAL OVERVIEW", [
            "CyberShell RPG v2.0 is an interactive terminal learning adventure.",
            "Your objective is to navigate 6 compromised mainframe sectors, completing exactly 3 focused hands-on terminal directives per sector (18 total).",
            "Each directive includes a command syntax and purpose briefing directly on the learning screen to guide your progress.",
        ]),
        ("CADET MODE VS OPERATIVE MODE", [
            "Cadet Mode: Safe learning environment. Electrical backlash damage is waived (0 HP lost on typos or syntax errors), and progressive hints are completely free.",
            "Operative Mode: High-stakes challenge. Typos and syntax errors cause -15 HP electrical backlash. Progressive hints cost small amounts of HP.",
            "You can toggle modes anytime from the Main Menu or by typing 'cadet' or 'operative' in the console.",
        ]),
        ("BEGINNER ASSIST TOOLKIT", [
            "Typo Coach       - Automatically detects missing spaces (e.g. 'cd..', 'ls-la') and suggests corrections.",
            "tree [path]      - Displays a visual Unicode tree of directories and files.",
            "explain <cmd>    - Breaks down command syntax, options, and arguments in plain English.",
            "hint             - 3-tier progressive assistance: Concept clue -> Syntax pattern -> Exact command.",
            "Tab Completion   - Press Tab to auto-complete commands and virtual file paths.",
            "save             - Creates a checkpoint in ~/.cybershell_save.json to preserve your progress.",
        ]),
        ("ESSENTIAL LINUX COMMANDS", [
            "pwd            - Print working directory coordinates.",
            "ls, ls -la     - List files, directories, hidden assets, and permissions.",
            "cd <path>      - Navigate directory tree (use '..', '~', or absolute paths).",
            "cat <file>     - Read and inspect text or log files.",
            "touch <file>   - Create new empty files.",
            "mkdir <dir>    - Create new directory folders.",
            "chmod <mode>   - Modify file permissions using octal notation (e.g., 755).",
            "grep <pattern> - Search files for matching text patterns.",
            "Pipes (|)      - Chain command outputs into inputs (e.g., cat file | grep text).",
        ]),
        ("STATION NAVIGATION & SHORTCUTS", [
            "From the Learning Interface terminal console, you can jump between stations:",
            "  menu (or 0)  - Return to Main Opening Menu.",
            "  codex (or 2) - Open Hacker Codex tactical spellbook.",
            "  items (or 3) - View inventory and collected hardware tokens.",
            "  map (or 4)   - Open Tactical Map of mainframe sectors.",
            "  minigame     - Play the Chmod Lockpicking challenge.",
            "  help         - Display operative command manual.",
        ]),
    ]
    for sec_title, sec_lines in sections:
        print(f"  {YELLOW}{BOLD}[ {sec_title} ]{RESET}")
        for line in sec_lines:
            for w in textwrap.wrap(line, width=width - 6):
                print(f"    {WHITE}{w}{RESET}")
        print()
    print(f"  {DIM}{'─' * (width - 4)}{RESET}")
    try:
        input(f"  {YELLOW}Press Enter to return to Main Menu...{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass


def interactive_game_loop(
    character_name: str = "Byte",
    start_sector: int = 0,
    player: Optional[PlayerStats] = None,
    vfs: Optional[VirtualFileSystem] = None,
    interpreter: Optional[Interpreter] = None,
    evaluator: Optional[QuestEvaluator] = None,
    all_quests: Optional[Dict[int, Quest]] = None,
    app: Optional[RPGApp] = None,
    cadet_mode: bool = True,
) -> None:
    """Interactive Learning Interface game loop with uncluttered directives and beginner tools."""
    if player is None:
        player = PlayerStats(
            character_name=character_name,
            hp=100,
            max_hp=100,
            xp=0,
            current_sector=start_sector,
        )
    if vfs is None:
        vfs = VirtualFileSystem(default_user="operative")
    if interpreter is None:
        interpreter = Interpreter(vfs=vfs)
    if evaluator is None:
        evaluator = QuestEvaluator()
    if all_quests is None:
        all_quests = get_sector_quests()
    if app is None:
        app = RPGApp(
            character_name=player.character_name,
            hp=player.hp,
            max_hp=player.max_hp,
            xp=player.xp,
        )

    app.set_screen(RPGApp.SCREEN_LAB)
    setup_tab_completion(vfs)

    quest = all_quests.get(player.current_sector)
    if not quest:
        quest = all_quests[0]

    ticker_msg = "MISSION LAB ACTIVE // Complete directives below."
    init_w, _ = terminal_size()
    panel_content_w = max(20, ((init_w - 2) // 2) - 6)
    banner_bar = "═" * panel_content_w
    mode_text = "CADET (SAFE)" if cadet_mode else "OPERATIVE (HARD)"
    terminal_logs: List[str] = [
        f"{GREEN}╔{banner_bar}╗{RESET}",
        f"{GREEN}║{f'CYBERSHELL v{__version__} MISSION LAB':^{panel_content_w}}║{RESET}",
        f"{GREEN}╚{banner_bar}╝{RESET}",
        f"{CYAN}Operative '{player.character_name}' link established in Sector {player.current_sector}.{RESET}",
        f"{YELLOW}Difficulty Mode: {mode_text}{RESET}",
        f"{WHITE}Type 'help' for commands, 'explain' for syntax, or 'menu' to return.{RESET}",
        f"{DIM}{'─' * (panel_content_w + 2)}{RESET}",
    ]

    hint_tier = 1
    last_objective_id: Optional[str] = None

    while True:
        width, _ = terminal_size()
        app.hp = player.hp
        app.max_hp = player.max_hp
        app.xp = player.xp
        app.inventory = player.inventory

        # Clear screen and display layout
        sys.stdout.write("\033[H\033[J")
        header = draw_double_header(
            player.character_name,
            player.hp,
            player.max_hp,
            player.xp,
            f"SECTOR {player.current_sector}: {quest.sector_name.upper()}",
            width,
            styled=True,
        )

        left_width = (width - 2) // 2
        content_width = max(10, left_width - 4)

        # Active objective tracking & task number (1 of 3, 2 of 3, 3 of 3)
        active_obj = quest.current_objective
        if active_obj and active_obj in quest.objectives:
            task_num = quest.objectives.index(active_obj) + 1
        else:
            task_num = 3

        if active_obj and active_obj.id != last_objective_id:
            last_objective_id = active_obj.id
            hint_tier = 1

        mode_badge = (
            f"{GREEN}CADET (SAFE){RESET}"
            if cadet_mode
            else f"{RED}OPERATIVE (BACKLASH){RESET}"
        )

        # Left panel: UNCLUTTERED, focused only on active level and task
        intel_lines = [
            f"{CYAN}{BOLD}[ SECTOR {quest.sector_id}/5: {quest.sector_name.upper()} ]{RESET}",
            f"{WHITE}Handler:{RESET} {CYAN}{quest.npc_name.upper()}{RESET}  |  {WHITE}Mode:{RESET} {mode_badge}",
            f"{YELLOW}Sector Progress:{RESET} {WHITE}{BOLD}Task {task_num} of 3{RESET}",
            "",
            f"{GREEN}{BOLD}[ ACTIVE DIRECTIVE // TASK {task_num} OF 3 ]{RESET}",
        ]

        if active_obj:
            for d_line in wrap_text(
                f"🎯 {active_obj.description}", content_width, style=WHITE + BOLD
            ):
                intel_lines.append(d_line)
            intel_lines.append("")

            # In-Screen Command Syntax & Briefing Box (Requested explicitly)
            intel_lines.append(f"{YELLOW}{BOLD}[ COMMAND SYNTAX & BRIEFING ]{RESET}")
            cmd_name = active_obj.command if active_obj.command else "command"
            syntax_str = active_obj.syntax if active_obj.syntax else cmd_name
            expl_str = (
                active_obj.explanation
                if active_obj.explanation
                else "Execute to fulfill objective."
            )
            intel_lines.append(f"  {CYAN}Command:{RESET} {WHITE}{BOLD}{cmd_name}{RESET}")
            intel_lines.append(f"  {CYAN}Syntax:{RESET}  {YELLOW}{syntax_str}{RESET}")
            for e_line in wrap_text(f"Purpose: {expl_str}", content_width - 2, style=WHITE):
                intel_lines.append(f"  {e_line}")
            intel_lines.append("")

            # Radio transmission: only current task dialogue
            intel_lines.append(f"{CYAN}{BOLD}[ RADIO // {quest.npc_name.upper()} ]{RESET}")
            diag_idx = min(task_num - 1, max(0, len(quest.dialogue) - 1))
            task_diag = (
                quest.dialogue[diag_idx]
                if quest.dialogue
                else "Operative, proceed with the directive."
            )
            for t_line in wrap_text(f'"{task_diag}"', content_width, style=YELLOW):
                intel_lines.append(t_line)
        else:
            intel_lines.append(f"{GREEN}{BOLD}✓ ALL 3 SECTOR TASKS COMPLETED!{RESET}")
            intel_lines.append(f"{CYAN}Liberation sequence ready. Advance to next sector.{RESET}")

        intel_lines.append("")
        intel_lines.append(
            f"{DIM}Commands: [hint] [explain] [tree] [cadet] [operative] [save] [menu]{RESET}"
        )

        # Boss HUD if in Sector 5
        boss_banner = ""
        if player.current_sector == 5:
            siren = get_siren_banner(
                "CRITICAL THREAT: SENTINEL OVERLORD ACTIVE // CORE LOCKDOWN",
                width=width,
                styled=True,
            )
            boss_hp = 100 if (quest.current_objective and not quest.is_completed) else 0
            boss_bar = format_boss_hp_bar(boss_hp, 100, bar_width=18, styled=True)
            boss_banner = f"{siren}\n{boss_bar.center(width)}\n"

        cwd_short = vfs.get_cwd_path().replace(f"/home/{vfs.user}", "~")

        # Split panels with styled borders
        max_log_lines = max(16, len(intel_lines) - 2)
        console_display = list(terminal_logs[-max_log_lines:])
        console_display.append(f"{GREEN}operative@cybershell:{cwd_short}$ {RESET}\033[7m \033[0m")
        panels = draw_split_panels(
            f"{CYAN}{BOLD}MISSION INTEL & DIRECTIVE{RESET}",
            intel_lines,
            f"{GREEN}{BOLD}ACTIVE TERMINAL CONSOLE{RESET}",
            console_display,
            width,
            styled=True,
        )

        sys.stdout.write(header + "\n" + boss_banner + panels + "\n")
        sys.stdout.write(f"\033[1;97;44m [ {ticker_msg} ] \033[0m\n")

        # Health check
        if player.hp <= 0:
            print("\n" + f"{RED}{BOLD}💀 SYSTEM CRITICAL: ELECTRICAL BACKLASH OVERLOAD. OPERATIVE TERMINATED. 💀{RESET}".center(width + 15))
            print(f"{YELLOW}Rebooting operative mainframe link in sandbox safe mode...{RESET}\n")
            player.hp = 100
            try:
                input("Press Enter to reboot operative...")
            except (KeyboardInterrupt, EOFError):
                break
            continue

        try:
            prompt = f"\033[1;92moperative@cybershell\033[0m:\033[1;94m{cwd_short}\033[0m$ "
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            save_game(player, cadet_mode)
            print(f"\n{CYAN}Returning to CyberShell Main Menu...{RESET}")
            break

        if not user_input:
            continue

        input_lower = user_input.lower()

        # Return to main menu
        if input_lower in ("0", "menu", "main", "back", "title"):
            save_game(player, cadet_mode)
            break

        if input_lower in ("exit", "quit"):
            save_game(player, cadet_mode)
            break

        # In-game station viewers
        if input_lower in ("2", "codex"):
            view_codex(app.codex, player, width)
            continue

        if input_lower in ("3", "items", "inventory"):
            view_inventory(player, width)
            continue

        if input_lower in ("4", "map"):
            view_map(app.mainframe, player, all_quests, width)
            continue

        if input_lower in ("5", "minigame"):
            view_minigame(app.minigame, player, width)
            continue

        if input_lower == "clear":
            terminal_logs = [f"{DIM}(terminal console cleared){RESET}"]
            continue

        if input_lower == "save":
            saved = save_game(player, cadet_mode)
            if saved:
                terminal_logs.append(f"{GREEN}💾 Game progress saved to ~/.cybershell_save.json!{RESET}")
                ticker_msg = "CHECKPOINT SAVED // Progress preserved."
            else:
                terminal_logs.append(f"{RED}Failed to write save file.{RESET}")
            continue

        if input_lower == "cadet":
            cadet_mode = True
            save_game(player, cadet_mode)
            terminal_logs.append(
                f"{GREEN}{BOLD}🛡️ [CADET MODE ENGAGED] Backlash damage waived (0 HP). Free hints enabled.{RESET}"
            )
            ticker_msg = "CADET MODE ENGAGED // Safe learning environment active."
            continue

        if input_lower == "operative":
            cadet_mode = False
            save_game(player, cadet_mode)
            terminal_logs.append(
                f"{RED}{BOLD}⚡ [OPERATIVE MODE ENGAGED] High stakes enabled. Syntax errors cause -15 HP backlash.{RESET}"
            )
            ticker_msg = "OPERATIVE MODE ENGAGED // Full challenge active."
            continue

        if input_lower.startswith("tree"):
            terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ {user_input}{RESET}")
            parts = user_input.split(maxsplit=1)
            target_path = parts[1] if len(parts) > 1 else "."
            node = vfs.resolve_path(target_path)
            if node is None:
                terminal_logs.append(f"{RED}tree: {target_path}: No such file or directory{RESET}")
            elif not node.is_directory:
                terminal_logs.append(f"{WHITE}{node.name}{RESET}")
                terminal_logs.append(f"{DIM}0 directories, 1 file{RESET}")
            else:
                for tl in render_vfs_tree(node):
                    terminal_logs.append(tl)
            ticker_msg = "DIRECTORY TREE // Filesystem hierarchy rendered."
            continue

        if input_lower.startswith("explain"):
            terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ {user_input}{RESET}")
            for el in explain_command(user_input, active_obj):
                terminal_logs.append(el)
            ticker_msg = "COMMAND EXPLAINER // Breakdown displayed."
            continue

        if input_lower == "hint":
            terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ hint{RESET}")
            if not active_obj:
                terminal_logs.append(f"{GREEN}All sector directives complete! No hint needed.{RESET}")
            else:
                h_msg, cost = get_progressive_hint(active_obj, hint_tier, cadet_mode)
                if cost > 0:
                    dmg = player.take_damage(cost)
                    terminal_logs.append(f"{RED}⚡ Tactical Intel Decryption: -{dmg} HP{RESET}")
                terminal_logs.append(f"{YELLOW}{BOLD}{h_msg}{RESET}")
                hint_tier = min(3, hint_tier + 1)
            ticker_msg = "TACTICAL HINT // Guidance displayed above."
            continue

        if input_lower in ("help", "man"):
            terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ help{RESET}")
            terminal_logs.append(f"{YELLOW}{BOLD}--- CYBERSHELL OPERATIVE COMMAND GUIDE ---{RESET}")
            terminal_logs.append(f"  {WHITE}pwd{RESET}            : Print working directory coordinates.")
            terminal_logs.append(f"  {WHITE}ls -la{RESET}         : Scan directory contents, hidden files, and file permissions.")
            terminal_logs.append(f"  {WHITE}cd <path>{RESET}      : Navigate the mainframe directory tree.")
            terminal_logs.append(f"  {WHITE}cat <file>{RESET}     : Read and display file contents.")
            terminal_logs.append(f"  {WHITE}touch <file>{RESET}   : Create a new empty file or update timestamp.")
            terminal_logs.append(f"  {WHITE}mkdir <dir>{RESET}    : Construct a new directory folder.")
            terminal_logs.append(f"  {WHITE}chmod <mode>{RESET}   : Modify file permissions using octal notation (e.g. 755).")
            terminal_logs.append(f"  {WHITE}grep <pattern>{RESET} : Search files for matching text patterns.")
            terminal_logs.append(f"{CYAN}{BOLD}--- BEGINNER ASSIST TOOLS ---{RESET}")
            terminal_logs.append(f"  {WHITE}tree [path]{RESET}    : Render a visual tree of directories and files.")
            terminal_logs.append(f"  {WHITE}explain [cmd]{RESET}  : Educational breakdown of command syntax and arguments.")
            terminal_logs.append(f"  {WHITE}hint{RESET}           : 3-tier progressive hint (Concept -> Syntax -> Exact answer).")
            terminal_logs.append(f"  {WHITE}cadet{RESET}          : Enable Cadet mode (backlash damage waived).")
            terminal_logs.append(f"  {WHITE}operative{RESET}      : Enable Operative mode (full -15 HP backlash challenge).")
            terminal_logs.append(f"  {WHITE}save{RESET}           : Save progress checkpoint to ~/.cybershell_save.json.")
            terminal_logs.append(f"  {WHITE}clear{RESET}          : Clear previous log entries from the terminal screen.")
            terminal_logs.append(f"{CYAN}{BOLD}--- TACTICAL SHORTCUTS ---{RESET}")
            terminal_logs.append(f"  {WHITE}menu (or 0){RESET}    : Return to Main Directory menu.")
            terminal_logs.append(f"  {WHITE}codex (or 2){RESET}   : Open Hacker Codex tactical spellbook.")
            terminal_logs.append(f"  {WHITE}items (or 3){RESET}   : View collected loot and hardware chips.")
            terminal_logs.append(f"  {WHITE}map (or 4){RESET}     : View ASCII network map of all sectors.")
            terminal_logs.append(f"  {WHITE}minigame (or 5){RESET}: Play Chmod Lockpicking puzzle for bonus XP.")
            ticker_msg = "COMMAND GUIDE // Review available commands above."
            continue

        # Typo check before execution
        typo = check_typo_or_syntax(user_input)
        if typo:
            sugg, expl = typo
            if cadet_mode:
                terminal_logs.append(f"{YELLOW}💡 [TYPO COACH] You typed '{user_input}'. {expl}{RESET}")
                terminal_logs.append(f"{CYAN}   Did you mean '{sugg}'? (Backlash waived in Cadet Mode){RESET}")
            else:
                terminal_logs.append(f"{YELLOW}💡 [TYPO COACH] Detected typo '{user_input}'. {expl}{RESET}")
                terminal_logs.append(f"{CYAN}   Did you mean '{sugg}'?{RESET}")

        # Execute command in VFS
        terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ {user_input}{RESET}")
        result = interpreter.execute(user_input)

        if result.stdout:
            if user_input.split()[0] == "ls":
                for out_line in colorize_ls_output(result.stdout):
                    terminal_logs.append(out_line)
            else:
                for out_line in result.stdout.splitlines():
                    terminal_logs.append(f"{WHITE}{out_line}{RESET}")

        if result.stderr:
            for err_line in result.stderr.splitlines():
                terminal_logs.append(f"{RED}{err_line}{RESET}")

        # Combat backlash
        if result.has_backlash:
            if cadet_mode:
                terminal_logs.append(
                    f"{YELLOW}⚡ [CADET SHIELD] Backlash absorbed (0 HP lost). Review command syntax above or type 'hint'.{RESET}"
                )
                ticker_msg = "⚡ SYNTAX ERROR ABSORBED // Cadet mode protected you."
            else:
                dmg = player.take_damage(result.backlash_damage)
                terminal_logs.append(
                    f"{RED}{BOLD}⚡ ELECTRICAL BACKLASH! -{dmg} HP (Syntax Shock through mainframe wires){RESET}"
                )
                terminal_logs.append(f"{YELLOW}💡 Tip: Type 'explain' or 'help' to review valid Linux syntax.{RESET}")
                ticker_msg = f"⚡ ELECTRICAL BACKLASH! -{dmg} HP // Check command syntax."
        else:
            ticker_msg = f"Command '{user_input.split()[0]}' executed successfully."

        # Objective evaluation
        old_level = player.level
        is_completed, newly_completed = evaluator.check_quest_progress(
            quest, vfs, player, last_command=user_input
        )
        if not result.stderr and result.exit_code == 0 and not newly_completed and not result.stdout:
            first_cmd = user_input.strip().split()[0] if user_input.strip() else ""
            if first_cmd in ("touch", "mkdir", "cd", "chmod", "cp", "mv", "rm"):
                terminal_logs.append(f"{DIM}✓ Command '{first_cmd}' executed successfully.{RESET}")
        if newly_completed:
            hint_tier = 1
            total_reward = 0
            for item in newly_completed:
                if isinstance(item, str):
                    matched_obj = next((o for o in quest.objectives if o.id == item), None)
                    desc = matched_obj.description if matched_obj else item
                    reward = matched_obj.xp_reward if matched_obj else 50
                else:
                    desc = item.description
                    reward = item.xp_reward
                total_reward += reward
                terminal_logs.append(f"{GREEN}{BOLD}🎯 DIRECTIVE ACCOMPLISHED! +{reward} XP: {desc}{RESET}")
            ticker_msg = f"🎯 OBJECTIVE ACCOMPLISHED! +{total_reward} XP"
            save_game(player, cadet_mode)

            if is_completed:
                player.completed_sectors.add(quest.sector_id)
                terminal_logs.append(f"{MAGENTA}{BOLD}🏆 SECTOR {quest.sector_id} ({quest.sector_name}) FULLY LIBERATED!{RESET}")
                if quest.reward_item:
                    terminal_logs.append(f"{YELLOW}🎁 LOOT ACQUIRED: {quest.reward_item.name} - {quest.reward_item.description}{RESET}")
                    ticker_msg = f"🏆 SECTOR {quest.sector_id} LIBERATED! Loot: {quest.reward_item.name} (+{quest.reward_xp} XP)"
                next_sector = player.current_sector + 1
                if next_sector in all_quests:
                    player.current_sector = next_sector
                    quest = all_quests[next_sector]
                    save_game(player, cadet_mode)
                    terminal_logs.append(f"{CYAN}{BOLD}🚀 ADVANCING TO SECTOR {next_sector}: {quest.sector_name}!{RESET}")
                    terminal_logs.append(f"{YELLOW}Handler {quest.npc_name} is establishing contact...{RESET}")
                else:
                    save_game(player, cadet_mode)
                    terminal_logs.append(f"{MAGENTA}{BOLD}👑 VICTORY! ALL 6 SECTORS LIBERATED! MAINFRAME FREED FROM ROGUE DAEMONS!{RESET}")
                    ticker_msg = "👑 VICTORY! ALL SECTORS LIBERATED! MAINFRAME SECURED!"
            elif quest.is_completed and quest.reward_item:
                terminal_logs.append(f"{YELLOW}🎁 LOOT ACQUIRED: {quest.reward_item.name} - {quest.reward_item.description}{RESET}")
                ticker_msg = f"🎁 LOOT ACQUIRED: {quest.reward_item.name}!"

        if player.level > old_level:
            terminal_logs.append(f"{MAGENTA}{BOLD}🌟 PROMOTION! You leveled up to Level {player.level}! New Rank: {player.rank}{RESET}")
            ticker_msg += f" 🌟 LEVEL UP! Rank: {player.rank}"


# =============================================================================
# MAIN MENU CONTROLLER LOOP
# =============================================================================

def main_menu_loop(character_name: str = "Byte", start_sector: int = 0) -> None:
    """Main menu loop presenting the opening screen and navigation options."""
    saved_data = load_saved_game()
    cadet_mode = True
    if saved_data is not None:
        player, cadet_mode = saved_data
    else:
        player = PlayerStats(
            character_name=character_name,
            hp=100,
            max_hp=100,
            xp=0,
            current_sector=start_sector,
        )

    vfs = VirtualFileSystem(default_user="operative")
    interpreter = Interpreter(vfs=vfs)
    evaluator = QuestEvaluator()
    all_quests = get_sector_quests()

    app = RPGApp(
        character_name=player.character_name,
        hp=player.hp,
        max_hp=player.max_hp,
        xp=player.xp,
    )

    while True:
        has_save = os.path.isfile(SAVE_FILE_PATH)
        width, _ = terminal_size()
        sys.stdout.write("\033[H\033[J")
        print(render_opening_screen(player, width, cadet_mode=cadet_mode, has_save=has_save))

        max_option = 8 if has_save else 7
        try:
            choice = input(f"\n{YELLOW}Select station [0-{max_option}] (default: 1): {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Disconnecting from CyberShell session. Safe travels, operative.{RESET}\n")
            break

        if not choice:
            choice = "1"

        choice_lower = choice.lower()
        if choice_lower in ("0", "exit", "quit", "q"):
            print(f"\n{CYAN}Disconnecting from CyberShell mainframe session. Safe travels, operative.{RESET}\n")
            break

        if has_save:
            if choice_lower in ("1", "continue", "resume", "c"):
                interactive_game_loop(
                    character_name=player.character_name,
                    start_sector=player.current_sector,
                    player=player,
                    vfs=vfs,
                    interpreter=interpreter,
                    evaluator=evaluator,
                    all_quests=all_quests,
                    app=app,
                    cadet_mode=cadet_mode,
                )
            elif choice_lower in ("2", "new", "reset"):
                delete_saved_game()
                player = PlayerStats(
                    character_name=character_name,
                    hp=100,
                    max_hp=100,
                    xp=0,
                    current_sector=0,
                )
                vfs = VirtualFileSystem(default_user="operative")
                interpreter = Interpreter(vfs=vfs)
                all_quests = get_sector_quests()
                interactive_game_loop(
                    character_name=player.character_name,
                    start_sector=0,
                    player=player,
                    vfs=vfs,
                    interpreter=interpreter,
                    evaluator=evaluator,
                    all_quests=all_quests,
                    app=app,
                    cadet_mode=cadet_mode,
                )
            elif choice_lower in ("3", "codex"):
                view_codex(app.codex, player, width)
            elif choice_lower in ("4", "items", "inventory"):
                view_inventory(player, width)
            elif choice_lower in ("5", "map"):
                view_map(app.mainframe, player, all_quests, width)
            elif choice_lower in ("6", "minigame", "lockpick"):
                view_minigame(app.minigame, player, width)
            elif choice_lower in ("7", "manual", "help", "rules"):
                view_field_manual(width)
            elif choice_lower in ("8", "mode", "toggle", "t"):
                cadet_mode = not cadet_mode
                save_game(player, cadet_mode)
            else:
                print(f"\n{RED}Unrecognized station option '{choice}'. Please select [0-{max_option}].{RESET}")
                try:
                    input(f"{YELLOW}Press Enter to continue...{RESET}")
                except (KeyboardInterrupt, EOFError):
                    break
        else:
            if choice_lower in ("1", "lab", "learn", "learning", "start"):
                interactive_game_loop(
                    character_name=player.character_name,
                    start_sector=player.current_sector,
                    player=player,
                    vfs=vfs,
                    interpreter=interpreter,
                    evaluator=evaluator,
                    all_quests=all_quests,
                    app=app,
                    cadet_mode=cadet_mode,
                )
            elif choice_lower in ("2", "codex"):
                view_codex(app.codex, player, width)
            elif choice_lower in ("3", "items", "inventory"):
                view_inventory(player, width)
            elif choice_lower in ("4", "map"):
                view_map(app.mainframe, player, all_quests, width)
            elif choice_lower in ("5", "minigame", "lockpick"):
                view_minigame(app.minigame, player, width)
            elif choice_lower in ("6", "manual", "help", "rules"):
                view_field_manual(width)
            elif choice_lower in ("7", "mode", "toggle", "t"):
                cadet_mode = not cadet_mode
                save_game(player, cadet_mode)
            else:
                print(f"\n{RED}Unrecognized station option '{choice}'. Please select [0-{max_option}].{RESET}")
                try:
                    input(f"{YELLOW}Press Enter to continue...{RESET}")
                except (KeyboardInterrupt, EOFError):
                    break


def run_demo(character_name: str = "Byte") -> None:
    """Showcase CyberShell fixed-frame UI rendering across screens without dumping all at once."""
    width, _ = terminal_size()
    app = RPGApp(character_name=character_name, hp=100, max_hp=100, xp=45)
    player = PlayerStats(character_name=character_name, hp=100, max_hp=100, xp=45)

    screens = [
        ("TITLE & OPENING SCREEN", lambda: render_opening_screen(player, width, cadet_mode=True, has_save=False)),
        ("MISSION LAB SCREEN", lambda: app.render_lab(width)),
        ("HACKER CODEX SCREEN", lambda: app.render_codex(width)),
        ("TACTICAL MAP SCREEN", lambda: app.render_map(width)),
    ]

    for title, render_fn in screens:
        sys.stdout.write("\033[H\033[J")
        print("=" * width)
        print(f"--- {title} ---".center(width))
        print(render_fn())
        if sys.stdin.isatty():
            try:
                input(f"\n{YELLOW}Press Enter to view next screen (or Ctrl+C to exit demo)...{RESET}")
            except (KeyboardInterrupt, EOFError):
                break


def main() -> int:
    """Main program entrypoint."""
    args = parse_args()

    if args.smoke_test:
        return run_smoke_test()

    if args.demo:
        run_demo(args.name)
        return 0

    main_menu_loop(args.name, args.sector)
    return 0


if __name__ == "__main__":
    sys.exit(main())
