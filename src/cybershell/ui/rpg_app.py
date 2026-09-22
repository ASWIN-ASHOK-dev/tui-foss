"""Byte's Linux Adventure - Interactive TUI Application & Screens.

Handles screen routing, fixed-frame layout, terminal input buffer,
friendly activity ticker, and interactive screens.
"""

from __future__ import annotations

import sys
from typing import List, Optional

# Ensure Windows terminals handle UTF-8 box characters and ASCII art cleanly
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from cybershell.contracts import UIProtocol
from cybershell.tools.chmod_minigame import ChmodMinigame
from cybershell.tools.codex import Codex
from cybershell.tools.map import MainframeMap, default_mainframe_map

from .ascii_art import (
    ADVENTURE_LOGO,
    CYBER_LOGO,
    FIELD_MANUAL_HEADER,
    format_boss_hp_bar,
    get_defeat_banner,
    get_portrait,
    get_siren_banner,
    get_victory_banner,
    visual_len,
)
from .renderer import (
    draw_double_header,
    draw_panel,
    draw_split_panels,
    terminal_size,
)


# =============================================================================
# Terminal Input Buffer Widget
# =============================================================================

class TerminalBuffer:
    """Manages shell command history and scrolling terminal log lines."""

    def __init__(
        self,
        prompt: str = "byte@adventure:~$ ",
        max_lines: int = 100,
    ) -> None:
        self.prompt = prompt
        self.max_lines = max_lines
        self.logs: List[str] = [
            f"{self.prompt}Welcome to Byte's Linux Adventure! 🌱",
            f"{self.prompt}Type 'help' or '?' for tips, or type 'pwd' to begin.",
        ]
        self.history: List[str] = []
        self.history_index: int = -1

    def add_log(self, line: str) -> None:
        """Append a single output or command line to the buffer."""
        self.logs.append(line)
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[-self.max_lines :]

    def add_logs(self, lines: List[str]) -> None:
        """Append multiple lines to the buffer."""
        for line in lines:
            self.add_log(line)

    def add_command(self, cmd: str) -> None:
        """Record executed command to history and log buffer."""
        clean = cmd.strip()
        if clean:
            self.history.append(clean)
            self.history_index = len(self.history)
            self.add_log(f"{self.prompt}{clean}")

    def clear(self) -> None:
        """Clear all visible log lines."""
        self.logs.clear()

    def get_visible_logs(self, count: int = 12) -> List[str]:
        """Return the most recent slice of logs for panel rendering."""
        if not self.logs:
            return ["(terminal ready)"]
        return self.logs[-count:]

    def history_prev(self) -> Optional[str]:
        """Navigate backward in command history."""
        if not self.history:
            return None
        if self.history_index > 0:
            self.history_index -= 1
        elif self.history_index == -1:
            self.history_index = len(self.history) - 1
        return self.history[self.history_index]

    def history_next(self) -> Optional[str]:
        """Navigate forward in command history."""
        if not self.history or self.history_index == -1:
            return None
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.history[self.history_index]
        self.history_index = len(self.history)
        return ""


# =============================================================================
# Activity Ticker
# =============================================================================

class CombatTicker:
    """Friendly bottom activity banner for updates, hints, and badges."""

    def __init__(self) -> None:
        self.active_message: str = "🌱 Welcome to Byte's Linux Adventure!"
        self.history: List[str] = [self.active_message]

    def log(self, message: str, category: str = "info") -> None:
        """Push an alert or friendly message to the activity ticker."""
        prefix = ""
        cat = category.lower()
        if cat in ("badge", "star", "reward"):
            prefix = "⭐ "
        elif cat == "loot":
            prefix = "🎁 "
        elif cat in ("xp", "level", "levelup"):
            prefix = "🌟 "
        elif cat == "objective":
            prefix = "🎯 "
        elif cat == "hint":
            prefix = "💡 "
        elif cat == "backlash":
            prefix = "⚡ "
        elif cat == "crit":
            prefix = "💥 "
        elif cat == "siren":
            prefix = "🚨 "

        full_msg = f"{prefix}{message}".strip()
        self.active_message = full_msg
        self.history.append(full_msg)

    def render(self, width: int = 80, styled: bool = False) -> str:
        """Render the bottom ticker strip formatted within given terminal width."""
        width = max(20, width)
        inner_width = width - 4
        msg = self.active_message
        if visual_len(msg) > inner_width:
            msg = msg[: max(0, inner_width - 1)] + "…"
        return f"[ {msg} ]".center(width)


# Backward-compatible alias
ActivityTicker = CombatTicker


# =============================================================================
# RPGApp Screen Controller
# =============================================================================

class RPGApp:
    """Main UI controller for Byte's Linux Adventure.

    Implements UIProtocol with dual-pane layout, terminal buffer,
    friendly activity ticker, and learning tools.
    """

    SCREEN_TITLE = 0
    SCREEN_LAB = 1
    SCREEN_CODEX = 2
    SCREEN_INVENTORY = 3
    SCREEN_MAP = 4
    SCREEN_MINIGAME = 5
    SCREEN_MANUAL = 6

    SCREEN_NAMES = {
        SCREEN_TITLE: "TITLE",
        SCREEN_LAB: "ADVENTURE PLAYGROUND",
        SCREEN_CODEX: "COMMAND GUIDE",
        SCREEN_INVENTORY: "BACKPACK",
        SCREEN_MAP: "ADVENTURE MAP",
        SCREEN_MINIGAME: "PERMISSIONS PUZZLE",
        SCREEN_MANUAL: "FIELD MANUAL & RULES",
    }

    def __init__(
        self,
        character_name: str = "Byte",
        hp: int = 100,
        max_hp: int = 100,
        xp: int = 0,
    ) -> None:
        self.character_name = character_name
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp
        self.inventory: List[Any] = []
        self.current_screen = self.SCREEN_TITLE

        # Visual components
        self.terminal_buffer = TerminalBuffer()
        self.ticker = CombatTicker()

        # Backward compatibility for boss/encounter state
        self.boss_name: str = "SENTINEL OVERLORD"
        self.boss_hp: int = 100
        self.boss_max_hp: int = 100
        self.is_boss_active: bool = False

        # Tools
        self.codex = Codex()
        self.mainframe: MainframeMap = default_mainframe_map()
        self.minigame = ChmodMinigame(difficulty="easy")

    def set_screen(self, screen: int) -> None:
        """Change the active screen view."""
        if screen not in self.SCREEN_NAMES:
            raise ValueError(f"Unknown screen: {screen}")
        self.current_screen = screen

    def get_screen_name(self) -> str:
        """Return the uppercase name of the active screen."""
        return self.SCREEN_NAMES[self.current_screen]

    def update_stats(self, hp: int, max_hp: int, xp: int) -> None:
        """Update player health and progression stats (UIProtocol)."""
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp

    def log_ticker(self, message: str, category: str = "info") -> None:
        """Push a message to the activity ticker (UIProtocol)."""
        self.ticker.log(message, category=category)

    def set_boss_encounter(
        self,
        active: bool,
        name: str = "SENTINEL OVERLORD",
        hp: int = 100,
        max_hp: int = 100,
    ) -> None:
        """Toggle boss encounter state (kept for backward compatibility)."""
        self.is_boss_active = active
        self.boss_name = name
        self.boss_hp = hp
        self.boss_max_hp = max_hp

    def update_boss_hp(self, hp: int) -> None:
        """Update boss HP (kept for backward compatibility)."""
        self.boss_hp = max(0, hp)

    def render_boss_hud(self, width: int = 80, styled: bool = False) -> str:
        """Render challenge reminder banner without clipping."""
        width = max(20, width)
        siren = get_siren_banner(
            f"CHALLENGE: {self.boss_name}",
            width=width,
            styled=styled,
        )
        bar = format_boss_hp_bar(
            self.boss_hp, self.boss_max_hp, bar_width=18, styled=styled
        )
        return f"{siren}\n{bar.center(width)}"

    def render_title(self, width: int = 80) -> str:
        """Render the title screen with friendly logo and menu options."""
        width = max(40, width)
        logo_lines = [line.center(width) for line in ADVENTURE_LOGO.strip("\n").splitlines()]
        menu_lines = [
            "",
            "🌱 BYTE'S LINUX ADVENTURE 🌱".center(width),
            "A friendly, playful terminal journey through Linux".center(width),
            "",
            "[1] START ADVENTURE".center(width),
            "[2] COMMAND GUIDE".center(width),
            "[3] BACKPACK & ITEMS".center(width),
            "[4] ADVENTURE MAP (15 LEVELS)".center(width),
            "[5] PERMISSIONS PUZZLE".center(width),
            "[6] FIELD MANUAL & RULES".center(width),
            "[0] EXIT".center(width),
            "",
            "Press a number to explore. [Esc] Return to menu".center(width),
        ]
        return "\n".join(logo_lines + menu_lines)

    def render_lab(
        self,
        width: int = 80,
        npc_name: Optional[str] = None,
        intel_lines: Optional[List[str]] = None,
        terminal_lines: Optional[List[str]] = None,
    ) -> str:
        """Render the Adventure Playground screen with split panels and activity ticker."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "ADVENTURE PLAYGROUND",
            width,
        )

        if intel_lines is not None:
            left_content = list(intel_lines)
        else:
            npc = npc_name or self.character_name
            portrait = get_portrait(npc, styled=False)
            left_content = [
                f"GUIDE: [{npc.upper()}]",
                "Status: EXPLORING 🌱",
            ] + portrait + [
                "Objective: Type 'pwd' to look around",
                "Progress: 0/15 Levels",
            ]

        if terminal_lines is not None:
            right_content = list(terminal_lines)
        else:
            right_content = self.terminal_buffer.get_visible_logs(max(6, len(left_content)))

        panels = draw_split_panels(
            "GUIDE & OBJECTIVE",
            left_content,
            "TERMINAL",
            right_content,
            width,
        )

        ticker = self.ticker.render(width)

        components = [header]
        if self.is_boss_active:
            components.append(self.render_boss_hud(width))
        components.append(panels)
        components.append(ticker)

        return "\n".join(components)

    def render_simple_screen(self, title: str, width: int = 80) -> str:
        """Render a placeholder screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            title,
            width,
        )

        body = [
            "",
            title.center(width),
            "",
            "This screen is ready for exploration.".center(width),
        ]

        return header + "\n" + "\n".join(body)

    def render_victory(self, width: int = 80) -> str:
        """Render adventure complete celebration screen."""
        return get_victory_banner(styled=False).center(width)

    def render_defeat(self, width: int = 80) -> str:
        """Render encouragement / retry screen."""
        return get_defeat_banner(styled=False).center(width)

    def render_codex(self, width: int = 80) -> str:
        """Render the Command Guide screen listing all known commands."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "COMMAND GUIDE // CODEX",
            width,
        )

        content = ["[ 🌱 LINUX COMMAND DIRECTORY // CODEX ]", ""]
        for entry in self.codex.list_commands():
            content.append(f"  {entry['name']:<9} {entry['description']}")
        content.append("")
        content.append("Type 'man <command>' or 'lookup <command>' in the terminal for details!")

        panel_lines = draw_panel("COMMAND GUIDE", content, width - 4)
        return header + "\n" + "\n".join(panel_lines)

    def render_map(self, width: int = 80) -> str:
        """Render the Adventure Map screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "ADVENTURE MAP (15 LEVELS)",
            width,
        )
        return header + "\n" + self.mainframe.render()

    def render_minigame(self, width: int = 80) -> str:
        """Render the Permissions Minigame screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "PERMISSIONS PUZZLE // MINIGAME",
            width,
        )
        if self.minigame.active_puzzle is None:
            self.minigame.generate_puzzle()
        door = self.minigame.render_door()
        return header + "\n" + door

    def render_inventory(self, width: int = 80) -> str:
        """Render the Backpack and collected goodies screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "BACKPACK & ITEMS",
            width,
        )

        content = ["[ 🎒 COLLECTED GOODIES & BADGES ]", ""]
        if not self.inventory:
            content.append("  Your backpack is currently empty.")
            content.append("  Complete levels and discover secrets to collect goodies! 🌱")
        else:
            for item in self.inventory:
                name = item.name if hasattr(item, 'name') else str(item)
                desc = item.description if hasattr(item, 'description') else ""
                rarity = getattr(item, 'rarity', 'common').upper()
                content.append(f"  [{rarity}] {name}")
                if desc:
                    content.append(f"      - {desc}")
                content.append("")
        content.append("")
        content.append("Press Enter or Esc to return.")

        panel_lines = draw_panel("BACKPACK", content, width - 4)
        return header + "\n" + "\n".join(panel_lines)

    def render_manual(self, width: int = 80) -> str:
        """Render the Field Manual & Rules screen."""
        lines = [
            FIELD_MANUAL_HEADER,
            "Welcome to Byte's Linux Adventure! 🌱",
            "",
            "• Exactly 15 bite-sized levels teaching real Linux skills.",
            "• Each level has 1-2 friendly goals.",
            "• Type Linux commands at the prompt (e.g. 'pwd', 'ls', 'cat').",
            "• Mistakes deal ZERO damage! Explore freely and learn.",
            "• Need a hint? Type '?' or 'hint' anytime.",
            "• Want to see all levels? Type 'map'.",
            "",
            "Press Enter to return to the adventure!",
        ]
        panel = draw_panel("FIELD MANUAL & RULES", lines, width - 4)
        return "\n".join(panel)

    def render(self) -> str:
        """Render the currently active screen."""
        width, _ = terminal_size()

        if self.current_screen == self.SCREEN_TITLE:
            return self.render_title(width)

        if self.current_screen == self.SCREEN_LAB:
            return self.render_lab(width)

        if self.current_screen == self.SCREEN_CODEX:
            return self.render_codex(width)

        if self.current_screen == self.SCREEN_INVENTORY:
            return self.render_inventory(width)

        if self.current_screen == self.SCREEN_MAP:
            return self.render_map(width)

        if self.current_screen == self.SCREEN_MINIGAME:
            return self.render_minigame(width)

        if self.current_screen == self.SCREEN_MANUAL:
            return self.render_manual(width)

        return ""


def create_app() -> RPGApp:
    """Create a default Linux Adventure application instance."""
    return RPGApp()


if __name__ == "__main__":
    app = create_app()
    print(app.render())
