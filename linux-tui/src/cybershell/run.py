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
from typing import List

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
    get_portrait,
    get_siren_banner,
)
from cybershell.ui.renderer import draw_double_header, draw_split_panels, terminal_size
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


def run_demo(character_name: str) -> None:
    """Showcase CyberShell fixed-frame UI rendering across screens."""
    width, _ = terminal_size()
    app = RPGApp(character_name=character_name, hp=100, max_hp=100, xp=45)

    print("=" * width)
    print("--- [0] TITLE SCREEN ---".center(width))
    app.set_screen(RPGApp.SCREEN_TITLE)
    print(app.render())

    print("\n" + "=" * width)
    print("--- [1] MISSION LAB SCREEN ---".center(width))
    app.set_screen(RPGApp.SCREEN_LAB)
    print(app.render())

    print("\n" + "=" * width)
    print("--- [2] CODEX SCREEN ---".center(width))
    app.set_screen(RPGApp.SCREEN_CODEX)
    print(app.render())

    print("\n" + "=" * width)
    print("--- [4] MAP SCREEN ---".center(width))
    app.set_screen(RPGApp.SCREEN_MAP)
    print(app.render())


def interactive_game_loop(character_name: str, start_sector: int) -> None:
    """Main interactive terminal loop for CyberShell RPG with rich colors and complete sentences."""
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
    app = RPGApp(
        character_name=player.character_name,
        hp=player.hp,
        max_hp=player.max_hp,
        xp=player.xp,
    )
    app.set_screen(RPGApp.SCREEN_LAB)

    # Initial Sector Quest Setup
    all_quests = get_sector_quests()
    quest = all_quests.get(start_sector)
    if not quest:
        quest = all_quests[0]

    ticker_msg = "CYBERSHELL v2.0 ONLINE // Security Breach Protocols Activated"
    init_w, _ = terminal_size()
    panel_content_w = max(20, ((init_w - 2) // 2) - 6)
    banner_bar = "═" * panel_content_w
    terminal_logs: List[str] = [
        f"{GREEN}╔{banner_bar}╗{RESET}",
        f"{GREEN}║{f'CYBERSHELL v{__version__} SHELL':^{panel_content_w}}║{RESET}",
        f"{GREEN}╚{banner_bar}╝{RESET}",
        f"{CYAN}Operative '{player.character_name}' online in Sector 0.{RESET}",
        f"{YELLOW}Warning: Typos cause -15 HP backlash!{RESET}",
        f"{WHITE}Type 'help' for full guide or 'codex' for tactics.{RESET}",
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
        intel_lines.append(f"{DIM}Shortcuts: [help] [codex]{RESET}")
        intel_lines.append(f"{DIM}           [map] [items]{RESET}")
        intel_lines.append(f"{DIM}           [minigame] [exit]{RESET}")

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
            input("Press Enter to reboot operative...")
            continue

        try:
            cwd_short = vfs.get_cwd_path().replace(f"/home/{vfs.user}", "~")
            prompt = f"\033[1;92moperative@cybershell\033[0m:\033[1;94m{cwd_short}\033[0m$ "
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Disconnecting from CyberShell session. Safe travels, operative.{RESET}")
            break

        if not user_input:
            continue

        # Screen routing commands
        if user_input in ("0", "title"):
            app.set_screen(RPGApp.SCREEN_TITLE)
            print(app.render())
            input(f"\n{YELLOW}Press Enter to return to Mission Lab...{RESET}")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue

        if user_input in ("2", "codex"):
            app.set_screen(RPGApp.SCREEN_CODEX)
            print("\n" + "=" * width)
            print(f"{MAGENTA}{BOLD}--- HACKER CODEX // TACTICAL COMMAND ARCHIVE ---{RESET}".center(width + 15))
            print(app.render())
            term = input(
                f"\n{YELLOW}Enter a command name to decrypt (or press Enter to return): {RESET}"
            ).strip()
            if term:
                print(app.codex.display_command(term))
                input(f"\n{YELLOW}Press Enter to return to Mission Lab...{RESET}")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue

        if user_input in ("3", "items", "inventory"):
            print("\n" + "=" * width)
            print(f"{CYAN}{BOLD}--- OPERATIVE INVENTORY & HARDWARE TOKENS ---{RESET}".center(width + 15))
            if not player.inventory:
                print(f"\n  {DIM}Your inventory is currently empty. Complete sector objectives to earn loot!{RESET}\n")
            else:
                print()
                for itm in player.inventory:
                    rarity_col = MAGENTA if itm.rarity in ("epic", "legendary", "mythic") else GREEN
                    print(f"  🎁 {WHITE}{BOLD}{itm.name}{RESET} [{rarity_col}{itm.rarity.upper()}{RESET}] ({itm.category.upper()})")
                    print(f"     {CYAN}{itm.description}{RESET}\n")
            input(f"\n{YELLOW}Press Enter to return to Mission Lab...{RESET}")
            continue

        if user_input in ("4", "map"):
            app.set_screen(RPGApp.SCREEN_MAP)
            app.mainframe.apply_progression(player)
            print("\n" + "=" * width)
            print(f"{CYAN}{BOLD}--- TACTICAL MAINFRAME NETWORK MAP ---{RESET}".center(width + 15))
            print(app.render())
            print(f"\n{YELLOW}{BOLD}SECTOR NETWORK TELEMETRY:{RESET}")
            for sid in range(6):
                q_info = all_quests.get(sid)
                if sid == player.current_sector:
                    status_str = f"{GREEN}🟢 CURRENT TARGET (ACTIVE INFILTRATION){RESET}"
                elif sid in player.completed_sectors:
                    status_str = f"{BLUE}🔵 LIBERATED (PERIMETER SECURED){RESET}"
                else:
                    status_str = f"{RED}🔒 LOCKED (DEFENSIVE SHIELDS ENGAGED){RESET}"
                print(f"  [{sid}] {WHITE}{q_info.sector_name:<20}{RESET} Status: {status_str}")
            input(f"\n{YELLOW}Press Enter to return to Mission Lab...{RESET}")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue

        if user_input in ("5", "minigame"):
            app.minigame.set_player(player)
            app.set_screen(RPGApp.SCREEN_MINIGAME)
            breach_session = True
            while breach_session:
                puzzle = app.minigame.generate_puzzle()
                app.xp = player.xp
                print(app.render())
                while True:
                    try:
                        guess = input(
                            f"\n{YELLOW}Enter octal code for pattern '{puzzle.permission}' "
                            f"(or 'q' to return): {RESET}"
                        ).strip()
                    except (KeyboardInterrupt, EOFError):
                        guess = "q"
                    if not guess:
                        continue
                    if guess.lower() in ("q", "quit", "back", "exit"):
                        breach_session = False
                        break
                    result = app.minigame.validate_answer(guess)
                    if result.correct:
                        print(f"\n{GREEN}{BOLD}{result.message}{RESET}")
                        if result.xp_awarded > 0:
                            ticker_msg = (
                                f"🔓 DOOR #{puzzle.door_number:02d} BREACHED: "
                                f"+{result.xp_awarded} XP"
                            )
                            print(f"{GREEN}🎉 +{result.xp_awarded} XP granted to operative!{RESET}")
                        else:
                            ticker_msg = f"🔓 DOOR #{puzzle.door_number:02d} already breached."
                        input(f"\n{YELLOW}Press Enter for next security door...{RESET}")
                        break
                    print(f"\n{RED}{result.message}{RESET}")
            app.xp = player.xp
            app.set_screen(RPGApp.SCREEN_LAB)
            continue

        if user_input.lower() in ("exit", "quit"):
            print(f"\n{CYAN}Disconnecting from CyberShell mainframe. Safe travels, operative.{RESET}")
            break

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
            terminal_logs.append(f"  {WHITE}codex (or 2){RESET}   : Open the Hacker Codex tactical spellbook.")
            terminal_logs.append(f"  {WHITE}map (or 4){RESET}     : View the ASCII network map of all sectors.")
            terminal_logs.append(f"  {WHITE}items (or 3){RESET}   : View collected loot and hardware chips.")
            terminal_logs.append(f"  {WHITE}minigame (or 5){RESET}: Play the Chmod Lockpicking puzzle for bonus XP.")
            terminal_logs.append(f"  {WHITE}exit (or quit){RESET} : Safely terminate the connection.")
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
            for obj in newly_completed:
                terminal_logs.append(f"{GREEN}{BOLD}🎯 DIRECTIVE ACCOMPLISHED! +{obj.xp_reward} XP: {obj.description}{RESET}")
            ticker_msg = f"🎯 OBJECTIVE ACCOMPLISHED! +{sum(o.xp_reward for o in newly_completed)} XP"
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


def main() -> int:
    """Main program entrypoint."""
    args = parse_args()

    if args.smoke_test:
        return run_smoke_test()

    if args.demo:
        run_demo(args.name)
        return 0

    interactive_game_loop(args.name, args.sector)
    return 0


if __name__ == "__main__":
    sys.exit(main())
