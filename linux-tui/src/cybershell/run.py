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
from cybershell.game.quests import get_sector_quests
from cybershell.ui.renderer import draw_double_header, draw_split_panels, terminal_size
from cybershell.ui.rpg_app import RPGApp


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
    """Main interactive terminal loop for CyberShell RPG."""
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

    ticker_msg = "SYSTEM ONLINE. Welcome to CyberShell v2.0."
    terminal_logs: list[str] = [
        "operative@cybershell:~$ System initialized.",
        "operative@cybershell:~$ Type 'help' for available commands.",
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
            f"SECTOR {player.current_sector}: {quest.sector_name}",
            width,
        )

        obj_desc = quest.current_objective.description if quest.current_objective else "All Sector Objectives Completed!"
        intel_lines = [
            f"NPC: [{quest.npc_name}]",
            f"Sector: {quest.sector_id} ({quest.sector_name})",
            f"Rank: {player.rank} (Lvl {player.level})",
            "",
            "--- ACTIVE OBJECTIVE ---",
            obj_desc,
            "",
            f"Inventory: {len(player.inventory)} items",
            "Screen [0]Title [1]Lab [2]Codex [3]Items [4]Map [5]Minigame",
        ]

        panels = draw_split_panels(
            "MISSION INTEL",
            intel_lines,
            "TERMINAL BUFFER",
            terminal_logs[-12:],
            width,
        )

        sys.stdout.write(header + "\n" + panels + "\n")
        sys.stdout.write(f"[{ticker_msg}]\n")

        # Health check
        if player.hp <= 0:
            print("\n" + "💀 SYSTEM CRITICAL: ELECTRICAL BACKLASH OVERLOAD. OPERATIVE TERMINATED. 💀".center(width))
            print("Restarting in sandbox mode...\n")
            player.hp = 100
            input("Press Enter to reboot operative...")
            continue

        try:
            cwd_short = vfs.get_cwd_path().replace(f"/home/{vfs.user}", "~")
            prompt = f"operative@cybershell:{cwd_short}$ "
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nDisconnecting from CyberShell session. Safe travels, operative.")
            break

        if not user_input:
            continue

        # Screen routing commands
        if user_input == "0" or user_input == "title":
            app.set_screen(RPGApp.SCREEN_TITLE)
            print(app.render())
            input("\nPress Enter to return to Mission Lab...")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue
        if user_input == "2" or user_input == "codex":
            app.set_screen(RPGApp.SCREEN_CODEX)
            print(app.render())
            term = input(
                "\nEnter a command name to decrypt (blank returns to Mission Lab): "
            ).strip()
            if term:
                print(app.codex.display_command(term))
                input("\nPress Enter to return to Mission Lab...")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue
        if user_input == "3" or user_input == "inventory":
            app.set_screen(RPGApp.SCREEN_INVENTORY)
            print(app.render())
            input("\nPress Enter to return to Mission Lab...")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue
        if user_input == "4" or user_input == "map":
            app.set_screen(RPGApp.SCREEN_MAP)
            app.mainframe.apply_progression(player)
            print(app.render())
            input("\nPress Enter to return to Mission Lab...")
            app.set_screen(RPGApp.SCREEN_LAB)
            continue
        if user_input == "5" or user_input == "minigame":
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
                            f"Enter the octal code for pattern '{puzzle.permission}' "
                            "(or 'q' to return): "
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
                        print(result.message)
                        if result.xp_awarded > 0:
                            ticker_msg = (
                                f"🔓 DOOR #{puzzle.door_number:02d} BREACHED: "
                                f"+{result.xp_awarded} XP"
                            )
                            print(f"+{result.xp_awarded} XP granted!")
                        else:
                            ticker_msg = f"🔓 DOOR #{puzzle.door_number:02d} already breached."
                        break
                    print(result.message)
            app.xp = player.xp
            app.set_screen(RPGApp.SCREEN_LAB)
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Disconnecting from CyberShell mainframe...")
            break

        if user_input == "clear":
            terminal_logs = []
            continue

        if user_input == "help":
            terminal_logs.append("operative@cybershell:~$ help")
            terminal_logs.append("Commands: pwd, cd, ls, cat, echo, touch, mkdir, chmod, clear, exit")
            terminal_logs.append("Screens: [0]Title, [1]Lab, [2]Codex, [3]Inventory, [4]Map, [5]Minigame")
            ticker_msg = "COMMAND MANUAL DISPLAYED"
            continue

        # Execute command in VFS
        terminal_logs.append(f"{prompt}{user_input}")
        result = interpreter.execute(user_input)

        if result.stdout:
            for out_line in result.stdout.splitlines():
                terminal_logs.append(out_line)

        if result.stderr:
            for err_line in result.stderr.splitlines():
                terminal_logs.append(f"\033[31m{err_line}\033[0m")

        # Combat backlash
        if result.has_backlash:
            dmg = player.take_damage(result.backlash_damage)
            ticker_msg = f"⚡ ELECTRICAL BACKLASH! -{dmg} HP (Syntax Shock)"
        else:
            ticker_msg = f"Command '{user_input.split()[0]}' executed."

        # Objective evaluation
        old_level = player.level
        is_completed, newly_completed = evaluator.check_quest_progress(quest, vfs, player)
        if newly_completed:
            ticker_msg = f"🎯 {len(newly_completed)} OBJECTIVE(S) ACCOMPLISHED!"
            if is_completed:
                ticker_msg += " | QUEST COMPLETE!"
                if quest.reward_item:
                    ticker_msg += f" 🎁 LOOT ACQUIRED: {quest.reward_item.name}!"
                next_sector = player.current_sector + 1
                if next_sector in all_quests:
                    player.current_sector = next_sector
                    quest = all_quests[next_sector]
                    ticker_msg += f" 🚀 ADVANCING TO SECTOR {next_sector}: {quest.sector_name}!"
                else:
                    ticker_msg += " 🏆 ALL SECTORS LIBERATED! MAINFRAME SECURED!"
            elif quest.is_completed and quest.reward_item:
                ticker_msg += f" 🎁 LOOT ACQUIRED: {quest.reward_item.name}!"
        
        if player.level > old_level:
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
