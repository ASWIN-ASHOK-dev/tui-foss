#!/usr/bin/env python3
"""CyberShell RPG v2.0 - Main Executable Launcher.

Author: Amy (Project Lead & Master Integrator)
Role: CLI launcher, argument parser, environment bootstrapper,
      and main game loop controller.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple

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
from cybershell.engine.vfs import VirtualFileSystem
from cybershell.engine.interpreter import Interpreter
from cybershell.game.evaluator import QuestEvaluator
import textwrap

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
# DEDICATED OPENING SCREEN & NAVIGATION
# =============================================================================

def render_opening_screen(player: PlayerStats, width: int = 80) -> str:
    """Render the primary opening screen displaying the name, description, and navigation options."""
    width = max(60, width)
    inner_w = max(40, width - 4)

    # 1. ASCII Title Logo & Header
    logo_raw = get_logo(styled=True)
    logo_lines = [pad_to_width(line, width, align="center") for line in logo_raw.strip("\n").splitlines()]

    # 2. Operative status line
    hp_pct = max(0, min(10, int((player.hp / max(1, player.max_hp)) * 10)))
    hp_bar = f"{GREEN}{'█' * hp_pct}{RED}{'░' * (10 - hp_pct)}{RESET}"
    status_text = (
        f"{CYAN}Operative:{RESET} {WHITE}{BOLD}{player.character_name}{RESET}  "
        f"{YELLOW}Rank:{RESET} {player.rank} (Lvl {player.level})  "
        f"{RED}HP:{RESET} [{hp_bar}] {player.hp}/{player.max_hp}  "
        f"{MAGENTA}XP:{RESET} {player.xp}"
    )
    status_line = pad_to_width(status_text, width, align="center")

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
        "Beware: electrical backlash damages your operative (-15 HP) on syntax errors! "
        "Think tactically, inspect manuals, and hone your terminal command craft."
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
    options = [
        ("1", "Learning Interface", "Interactive Mission Lab campaign & directives"),
        ("2", "Hacker Codex", "Tactical command reference & decryptions"),
        ("3", "Operative Inventory", "Inspect hardware tokens, chips, and loot"),
        ("4", "Tactical Map", "Mainframe sector topology & status map"),
        ("5", "Security Lockpick", "Chmod octal permission hacking for bonus XP"),
        ("6", "Field Manual & Rules", "Review combat rules, damage, and controls"),
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
        + ["", status_line, border_double, ""]
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
    """Display the Hacker Codex tactical command archive."""
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
            "Enter any command name below to decrypt its full manual entry, syntax flags, and operational examples."
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
                f"  {YELLOW}Enter command to decrypt (or press Enter / '0' to return to menu): {RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not term or term in ("0", "q", "quit", "exit", "back", "menu"):
            break

        entry_text = codex.display_command(term)
        print()
        print(f"  {MAGENTA}{BOLD}=== DECRYPTION RESULT: {term.upper()} ==={RESET}")
        for e_line in entry_text.splitlines():
            print(f"  {WHITE}{e_line}{RESET}")
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
            "Your objective is to navigate 6 compromised mainframe sectors, complete hands-on terminal directives, and liberate core subsystems from rogue security daemons.",
        ]),
        ("ELECTRICAL BACKLASH DAMAGE (-15 HP)", [
            "Executing invalid commands or typos sends electrical shock through your terminal connection (-15 HP).",
            "If your HP drops to 0, your connection crashes and reboots in safe mode. Think before pressing Enter!",
            "Requesting objective hints incurs a minor penalty of -5 HP.",
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
) -> None:
    """Interactive Learning Interface game loop with split panels, narrative intel, and terminal console."""
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

    quest = all_quests.get(player.current_sector)
    if not quest:
        quest = all_quests[0]

    ticker_msg = "LEARNING INTERFACE // Mission Directives Active"
    init_w, _ = terminal_size()
    panel_content_w = max(20, ((init_w - 2) // 2) - 6)
    banner_bar = "═" * panel_content_w
    terminal_logs: List[str] = [
        f"{GREEN}╔{banner_bar}╗{RESET}",
        f"{GREEN}║{f'CYBERSHELL v{__version__} MISSION LAB':^{panel_content_w}}║{RESET}",
        f"{GREEN}╚{banner_bar}╝{RESET}",
        f"{CYAN}Operative '{player.character_name}' link established in Sector {player.current_sector}.{RESET}",
        f"{YELLOW}Warning: Typos and syntax errors cause -15 HP backlash!{RESET}",
        f"{WHITE}Type 'help' for commands, or 'menu' (or '0') to return to Main Menu.{RESET}",
        f"{DIM}{'─' * (panel_content_w + 2)}{RESET}",
    ]

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

        # 1. Handler Portrait (styled cyberpunk ASCII art)
        portrait = get_portrait(quest.npc_name, styled=True)

        intel_lines = []
        for p_line in portrait:
            intel_lines.append(p_line)

        # Handler Header
        intel_lines.append(f"{CYAN}{BOLD}HANDLER:{RESET} {WHITE}{BOLD}{quest.npc_name.upper()}{RESET}  [{GREEN}ACTIVE LINK{RESET}]")
        intel_lines.append(f"{CYAN}Sector:{RESET} {quest.sector_id}/5 ({quest.sector_name})")
        intel_lines.append(f"{MAGENTA}Rank:{RESET} {player.rank} (Level {player.level})")
        intel_lines.append("")

        # 2. Mission Briefing (Lore in complete sentences)
        intel_lines.append(f"{YELLOW}{BOLD}[ MISSION BRIEFING ]{RESET}")
        for l_line in wrap_text(quest.lore, content_width, style=CYAN):
            intel_lines.append(l_line)
        intel_lines.append("")

        # 3. Handler Transmission (Dialogue in complete sentences)
        intel_lines.append(f"{YELLOW}{BOLD}[ SECURE TRANSMISSION // {quest.npc_name.upper()} ]{RESET}")
        for d_sent in quest.dialogue:
            for d_line in wrap_text(f'"{d_sent}"', content_width, style=YELLOW):
                intel_lines.append(d_line)
        intel_lines.append("")

        # 4. Active Directive (Objectives in complete sentences)
        intel_lines.append(f"{GREEN}{BOLD}[ ACTIVE DIRECTIVE ]{RESET}")
        if quest.current_objective:
            active_obj = quest.current_objective
            for o_line in wrap_text(f"🎯 {active_obj.description}", content_width, style=WHITE + BOLD):
                intel_lines.append(o_line)
            for h_line in wrap_text(f"💡 Hint: {active_obj.hint}", content_width, style=DIM):
                intel_lines.append(h_line)
        else:
            intel_lines.append(f"{GREEN}✓ All Sector Objectives Liberated! Advancing...{RESET}")
        intel_lines.append("")

        # 5. Operative Inventory
        intel_lines.append(f"{BLUE}{BOLD}[ OPERATIVE INVENTORY ]{RESET}")
        if player.inventory:
            for item in player.inventory:
                rarity_col = MAGENTA if item.rarity in ("epic", "legendary", "mythic") else GREEN
                for item_line in wrap_text(f"🎁 {item.name} [{item.rarity.upper()}]", content_width, style=WHITE):
                    intel_lines.append(f"  {item_line}")
        else:
            for empty_line in wrap_text("No hardware tokens acquired yet. Complete objectives to earn loot!", content_width, style=DIM):
                intel_lines.append(f"  {empty_line}")
        intel_lines.append("")

        # 6. Shortcuts
        intel_lines.append(f"{DIM}Shortcuts: [menu] [help] [codex]{RESET}")
        intel_lines.append(f"{DIM}           [map]  [items] [minigame]{RESET}")

        # Boss HUD if in Sector 5
        boss_banner = ""
        if player.current_sector == 5:
            siren = get_siren_banner("CRITICAL THREAT: SENTINEL OVERLORD ACTIVE // CORE LOCKDOWN", width=width, styled=True)
            boss_hp = 100 if (quest.current_objective and not quest.is_completed) else 0
            boss_bar = format_boss_hp_bar(boss_hp, 100, bar_width=18, styled=True)
            boss_banner = f"{siren}\n{boss_bar.center(width)}\n"

        # Split panels with styled borders
        max_log_lines = max(18, len(intel_lines))
        panels = draw_split_panels(
            f"{CYAN}{BOLD}MISSION INTEL & FIELD BRIEFING{RESET}",
            intel_lines,
            f"{GREEN}{BOLD}ACTIVE TERMINAL CONSOLE{RESET}",
            terminal_logs[-max_log_lines:],
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
            cwd_short = vfs.get_cwd_path().replace(f"/home/{vfs.user}", "~")
            prompt = f"\033[1;92moperative@cybershell\033[0m:\033[1;94m{cwd_short}\033[0m$ "
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Returning to CyberShell Main Menu...{RESET}")
            break

        if not user_input:
            continue

        # Return to main menu
        if user_input.lower() in ("0", "menu", "main", "back", "title"):
            break

        if user_input.lower() in ("exit", "quit"):
            break

        # In-game station viewers
        if user_input in ("2", "codex"):
            view_codex(app.codex, player, width)
            continue

        if user_input in ("3", "items", "inventory"):
            view_inventory(player, width)
            continue

        if user_input in ("4", "map"):
            view_map(app.mainframe, player, all_quests, width)
            continue

        if user_input in ("5", "minigame"):
            view_minigame(app.minigame, player, width)
            continue

        if user_input == "clear":
            terminal_logs = [f"{DIM}(terminal console cleared){RESET}"]
            continue

        if user_input.lower() in ("help", "man"):
            terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ help{RESET}")
            terminal_logs.append(f"{YELLOW}{BOLD}--- CYBERSHELL OPERATIVE COMMAND GUIDE ---{RESET}")
            terminal_logs.append(f"  {WHITE}pwd{RESET}            : Print your current directory path to confirm coordinates.")
            terminal_logs.append(f"  {WHITE}ls -la{RESET}         : Scan directory contents, hidden files, and file permissions.")
            terminal_logs.append(f"  {WHITE}cd <path>{RESET}      : Navigate the mainframe directory tree.")
            terminal_logs.append(f"  {WHITE}cat <file>{RESET}     : Read and display file contents (e.g. logs, keys).")
            terminal_logs.append(f"  {WHITE}touch <file>{RESET}   : Create a new empty telemetry or log file.")
            terminal_logs.append(f"  {WHITE}mkdir <dir>{RESET}    : Construct a new directory folder.")
            terminal_logs.append(f"  {WHITE}chmod <mode>{RESET}   : Modify file permissions using octal notation (e.g. 755).")
            terminal_logs.append(f"  {WHITE}clear{RESET}          : Clear previous log entries from the terminal screen.")
            terminal_logs.append(f"{CYAN}{BOLD}--- TACTICAL SHORTCUTS ---{RESET}")
            terminal_logs.append(f"  {WHITE}menu (or 0){RESET}    : Return to the Main Opening Menu.")
            terminal_logs.append(f"  {WHITE}codex (or 2){RESET}   : Open the Hacker Codex tactical spellbook.")
            terminal_logs.append(f"  {WHITE}map (or 4){RESET}     : View the ASCII network map of all sectors.")
            terminal_logs.append(f"  {WHITE}items (or 3){RESET}   : View collected loot and hardware chips.")
            terminal_logs.append(f"  {WHITE}minigame (or 5){RESET}: Play the Chmod Lockpicking puzzle for bonus XP.")
            ticker_msg = "COMMAND MANUAL DISPLAYED // Review available commands above."
            continue

        # Execute command in VFS
        terminal_logs.append(f"{GREEN}operative@cybershell:{cwd_short}$ {user_input}{RESET}")
        result = interpreter.execute(user_input)

        if result.stdout:
            for out_line in result.stdout.splitlines():
                terminal_logs.append(f"{WHITE}{out_line}{RESET}")

        if result.stderr:
            for err_line in result.stderr.splitlines():
                terminal_logs.append(f"{RED}{err_line}{RESET}")

        # Combat backlash
        if result.has_backlash:
            dmg = player.take_damage(result.backlash_damage)
            terminal_logs.append(f"{RED}{BOLD}⚡ ELECTRICAL BACKLASH! -{dmg} HP (Syntax Shock through mainframe wires){RESET}")
            terminal_logs.append(f"{YELLOW}💡 Tip: Type 'help' to review valid Linux syntax before running commands.{RESET}")
            ticker_msg = f"⚡ ELECTRICAL BACKLASH! -{dmg} HP // Check command syntax."
        else:
            ticker_msg = f"Command '{user_input.split()[0]}' executed successfully."

        # Objective evaluation
        old_level = player.level
        is_completed, newly_completed = evaluator.check_quest_progress(quest, vfs, player)
        if newly_completed:
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
            if is_completed:
                terminal_logs.append(f"{MAGENTA}{BOLD}🏆 SECTOR {quest.sector_id} ({quest.sector_name}) FULLY LIBERATED!{RESET}")
                if quest.reward_item:
                    terminal_logs.append(f"{YELLOW}🎁 LOOT ACQUIRED: {quest.reward_item.name} - {quest.reward_item.description}{RESET}")
                    ticker_msg = f"🏆 SECTOR {quest.sector_id} LIBERATED! Loot: {quest.reward_item.name} (+{quest.reward_xp} XP)"
                next_sector = player.current_sector + 1
                if next_sector in all_quests:
                    player.current_sector = next_sector
                    quest = all_quests[next_sector]
                    terminal_logs.append(f"{CYAN}{BOLD}🚀 ADVANCING TO SECTOR {next_sector}: {quest.sector_name}!{RESET}")
                    terminal_logs.append(f"{YELLOW}Handler {quest.npc_name} is establishing contact...{RESET}")
                else:
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
        width, _ = terminal_size()
        sys.stdout.write("\033[H\033[J")
        print(render_opening_screen(player, width))

        try:
            choice = input(f"\n{YELLOW}Select station [0-6] (default: 1): {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Disconnecting from CyberShell session. Safe travels, operative.{RESET}\n")
            break

        if not choice:
            choice = "1"

        choice_lower = choice.lower()
        if choice_lower in ("0", "exit", "quit", "q"):
            print(f"\n{CYAN}Disconnecting from CyberShell mainframe session. Safe travels, operative.{RESET}\n")
            break
        elif choice_lower in ("1", "lab", "learn", "learning"):
            interactive_game_loop(
                character_name=player.character_name,
                start_sector=player.current_sector,
                player=player,
                vfs=vfs,
                interpreter=interpreter,
                evaluator=evaluator,
                all_quests=all_quests,
                app=app,
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
        else:
            print(f"\n{RED}Unrecognized station option '{choice}'. Please select [0-6].{RESET}")
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
        ("TITLE & OPENING SCREEN", lambda: render_opening_screen(player, width)),
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
