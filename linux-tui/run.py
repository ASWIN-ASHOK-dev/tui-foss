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

# Ensure src/ is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

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
    suite = unittest.defaultTestLoader.discover("tests", pattern="test_integration.py")
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


def execute_vfs_command(vfs: VirtualFileSystem, cmd_line: str) -> CommandResult:
    """Execute basic shell commands directly against the VFS."""
    line = cmd_line.strip()
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
            new_path = vfs.cd(target)
            return CommandResult(stdout="", exit_code=0, metadata={"cwd": new_path})
        except Exception as err:
            return CommandResult(stderr=f"cd: {err}\n", exit_code=1)

    if binary == "ls":
        show_hidden = "-a" in args or "-la" in args or "-al" in args
        long_format = "-l" in args or "-la" in args or "-al" in args
        target = "."
        for arg in args:
            if not arg.startswith("-"):
                target = arg
                break
        try:
            nodes = vfs.list_dir(target, show_hidden=show_hidden)
            lines = []
            for node in nodes:
                if long_format:
                    from cybershell.engine.node import format_symbolic
                    mode_str = format_symbolic(node.permissions, node.is_directory)
                    size = node.size if node.is_file else 4096
                    lines.append(f"{mode_str}  {node.owner}  {size:>6}  {node.name}")
                else:
                    lines.append(node.name)
            output = "\n".join(lines) + ("\n" if lines else "")
            return CommandResult(stdout=output, exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"ls: {err}\n", exit_code=1)

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
            return CommandResult(stderr=f"touch: {err}\n", exit_code=1)

    if binary == "mkdir":
        if not args:
            return CommandResult(stderr="mkdir: missing operand\n", exit_code=1)
        try:
            if "-p" in args:
                target = [a for a in args if a != "-p"][0]
                vfs.mkdir_p(target)
            else:
                vfs.mkdir(args[0])
            return CommandResult(stdout="", exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"mkdir: {err}\n", exit_code=1)

    if binary == "cat":
        if not args:
            return CommandResult(stderr="cat: missing file operand\n", exit_code=1)
        try:
            content = vfs.read_file(args[0])
            return CommandResult(stdout=content + ("\n" if not content.endswith("\n") else ""), exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"cat: {err}\n", exit_code=1)

    if binary == "chmod":
        if len(args) < 2:
            return CommandResult(stderr="chmod: missing operand\n", exit_code=1)
        try:
            vfs.chmod(args[1], args[0])
            return CommandResult(stdout="", exit_code=0)
        except Exception as err:
            return CommandResult(stderr=f"chmod: {err}\n", exit_code=1)

    # Unknown command -> Electrical backlash damage!
    return CommandResult(
        stdout="",
        stderr=f"cybershell: command not found: {binary}\n",
        exit_code=127,
        backlash_damage=DEFAULT_BACKLASH_DAMAGE,
    )


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
    app = RPGApp(
        character_name=player.character_name,
        hp=player.hp,
        max_hp=player.max_hp,
        xp=player.xp,
    )
    app.set_screen(RPGApp.SCREEN_LAB)

    # Initial Sector 0 Quest Setup
    quest = Quest(
        id=f"quest_sector_{start_sector}",
        sector_id=start_sector,
        sector_name="Quarantine Zone",
        npc_name="Byte",
        lore="The corporate mainframe is locked down. Recover your coordinates.",
        dialogue=[
            "Operative! Welcome back to the grid.",
            "Type 'pwd' to check sector coordinates, or 'ls -la' to scan for security keys.",
        ],
        objectives=[
            Objective(
                id="obj_0_1",
                description="Determine mainframe position with 'pwd'",
                hint="Type 'pwd'",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
            Objective(
                id="obj_0_2",
                description="List quarantine contents with 'ls -la'",
                hint="Type 'ls -la'",
                predicate_type="file_exists",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
        ],
        reward_item=Item(
            id="item_quarantine_chip",
            name="Quarantine Keychip",
            description="Grants clearance to Sector 1 File Vault.",
            category="hardware",
            rarity="rare",
        ),
        reward_xp=100,
    )

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
        result = execute_vfs_command(vfs, user_input)

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
        curr_obj = quest.current_objective
        if curr_obj and not curr_obj.completed:
            if curr_obj.id == "obj_0_1" and user_input.strip() == "pwd":
                curr_obj.completed = True
                leveled = player.gain_xp(curr_obj.xp_reward)
                ticker_msg = f"🎯 OBJECTIVE ACQUIRED: +{curr_obj.xp_reward} XP!"
                if leveled:
                    ticker_msg += f" 🌟 LEVEL UP! Rank: {player.rank}"

            elif curr_obj.id == "obj_0_2" and "ls" in user_input.split()[0]:
                curr_obj.completed = True
                leveled = player.gain_xp(curr_obj.xp_reward)
                ticker_msg = f"🎯 OBJECTIVE ACQUIRED: +{curr_obj.xp_reward} XP!"
                if leveled:
                    ticker_msg += f" 🌟 LEVEL UP! Rank: {player.rank}"

                if quest.is_completed and quest.reward_item:
                    player.add_item(quest.reward_item)
                    ticker_msg += f" 🎁 LOOT ACQUIRED: {quest.reward_item.name}!"


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
