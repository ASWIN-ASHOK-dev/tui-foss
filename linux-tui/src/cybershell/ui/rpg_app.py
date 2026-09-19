"""CyberShell RPG application UI.

Handles screen routing, fixed-frame layout, terminal input buffer,
combat log ticker, and boss HUD elements.

Authors:
- Poornendhu: Cyber-TUI Lead & Frame Renderer (layout core, screen transitions)
- Gautham: Visual FX, ASCII Art & Terminal Box Specialist (terminal buffer, combat ticker, boss HUD)
- Akash: Hacker Codex & Security Minigame Specialist (screen views)
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

from cybershell.tools.chmod_minigame import ChmodMinigame
from cybershell.tools.codex import Codex
from cybershell.tools.map import MainframeMap, default_mainframe_map

from .ascii_art import (
    CYBER_LOGO,
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
# Terminal Input Buffer Widget (Gautham - Day 3)
# =============================================================================

class TerminalBuffer:
    """Manages shell command history and scrolling terminal log lines."""

    def __init__(
        self,
        prompt: str = "operative@cybershell:~$ ",
        max_lines: int = 100,
    ) -> None:
        self.prompt = prompt
        self.max_lines = max_lines
        self.logs: List[str] = [
            "operative@cybershell:~$ System initialized.",
            "operative@cybershell:~$ Type 'help' for available commands.",
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
# Combat Log Ticker (Gautham - Day 4)
# =============================================================================

class CombatTicker:
    """Real-time bottom broadcast strip for combat feedback and loot drops."""

    def __init__(self) -> None:
        self.active_message: str = "SYSTEM ONLINE. Welcome to CyberShell v2.0."
        self.history: List[str] = [self.active_message]

    def log(self, message: str, category: str = "info") -> None:
        """Push an alert message to the broadcast ticker."""
        prefix = ""
        cat = category.lower()
        if cat == "backlash":
            prefix = "⚡ "
        elif cat == "crit":
            prefix = "💥 "
        elif cat == "loot":
            prefix = "🎁 "
        elif cat in ("xp", "level"):
            prefix = "🌟 "
        elif cat == "objective":
            prefix = "🎯 "
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


# =============================================================================
# RPGApp Screen Controller (Poornendhu, Gautham & Akash)
# =============================================================================

class RPGApp:
    """Main UI controller for CyberShell.

    Implements UIProtocol (Amy) with double-pane layout (Poornendhu),
    terminal widgets, combat ticker, boss HUD (Gautham), and tactical tools (Akash).
    """

    SCREEN_TITLE = 0
    SCREEN_LAB = 1
    SCREEN_CODEX = 2
    SCREEN_INVENTORY = 3
    SCREEN_MAP = 4
    SCREEN_MINIGAME = 5

    SCREEN_NAMES = {
        SCREEN_TITLE: "TITLE",
        SCREEN_LAB: "MISSION LAB",
        SCREEN_CODEX: "CODEX",
        SCREEN_INVENTORY: "INVENTORY",
        SCREEN_MAP: "MAP",
        SCREEN_MINIGAME: "MINIGAME",
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
        self.current_screen = self.SCREEN_TITLE

        # Gautham's visual components
        self.terminal_buffer = TerminalBuffer()
        self.ticker = CombatTicker()

        # Boss encounter state (Day 5)
        self.boss_name: str = "SENTINEL OVERLORD"
        self.boss_hp: int = 100
        self.boss_max_hp: int = 100
        self.is_boss_active: bool = False

        # Integrated tactical tools (Akash: Codex / Map / Chmod Minigame)
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
        """Update operative health and progression stats (UIProtocol)."""
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp

    def log_ticker(self, message: str, category: str = "info") -> None:
        """Push an alert message to the combat ticker (UIProtocol)."""
        self.ticker.log(message, category=category)

    def set_boss_encounter(
        self,
        active: bool,
        name: str = "SENTINEL OVERLORD",
        hp: int = 100,
        max_hp: int = 100,
    ) -> None:
        """Toggle Sector 5 Boss battle encounter HUD."""
        self.is_boss_active = active
        self.boss_name = name
        self.boss_hp = hp
        self.boss_max_hp = max_hp

    def update_boss_hp(self, hp: int) -> None:
        """Update current Boss HP."""
        self.boss_hp = max(0, hp)

    def render_boss_hud(self, width: int = 80, styled: bool = False) -> str:
        """Render Sector 5 Boss siren warning and dynamic HP bar."""
        siren = get_siren_banner(
            f"WARNING: {self.boss_name} DETECTED - SECTOR 5 LOCKDOWN",
            width=width,
            styled=styled,
        )
        bar = format_boss_hp_bar(
            self.boss_hp, self.boss_max_hp, bar_width=18, styled=styled
        )
        return f"{siren}\n{bar.center(width)}"

    def render_title(self, width: int) -> str:
        """Render the title screen with cyberpunk logo and menu options."""
        logo_lines = [line.center(width) for line in CYBER_LOGO.strip("\n").splitlines()]
        menu_lines = [
            "",
            "CYBERSHELL RPG".center(width),
            "A TERMINAL-BASED CYBER ADVENTURE".center(width),
            "",
            "[1] ENTER MISSION LAB".center(width),
            "[2] CODEX".center(width),
            "[3] INVENTORY".center(width),
            "[4] MAP".center(width),
            "[5] MINIGAME".center(width),
            "",
            "Press a number to navigate.".center(width),
        ]
        return "\n".join(logo_lines + menu_lines)

    def render_lab(
        self,
        width: int,
        npc_name: Optional[str] = None,
        intel_lines: Optional[List[str]] = None,
        terminal_lines: Optional[List[str]] = None,
    ) -> str:
        """Render the Mission Lab screen with split panels and combat ticker."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "MISSION LAB",
            width,
        )

        # Build Mission Intel panel lines
        if intel_lines is not None:
            left_content = list(intel_lines)
        else:
            npc = npc_name or self.character_name
            portrait = get_portrait(npc, styled=False)
            left_content = [
                f"NPC: [{npc.upper()}]",
                "Status: ACTIVE",
            ] + portrait + [
                "Objective: Find the encrypted file",
                "Progress: 0/3",
            ]

        # Build Terminal panel lines
        if terminal_lines is not None:
            right_content = list(terminal_lines)
        else:
            right_content = self.terminal_buffer.get_visible_logs(max(6, len(left_content)))

        panels = draw_split_panels(
            "MISSION INTEL",
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

    def render_simple_screen(self, title: str, width: int) -> str:
        """Render a temporary placeholder screen."""
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
            "This screen is ready for module integration.".center(width),
        ]

        return header + "\n" + "\n".join(body)

    def render_victory(self, width: int = 80) -> str:
        """Render victory celebration screen."""
        return get_victory_banner(styled=False).center(width)

    def render_defeat(self, width: int = 80) -> str:
        """Render defeat/game over screen."""
        return get_defeat_banner(styled=False).center(width)

    def render_codex(self, width: int) -> str:
        """Render the Hacker Codex screen listing all known commands."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "HACKER CODEX",
            width,
        )

        content = ["[ SPELLBOOK // TACTICAL COMMAND ARCHIVE ]", ""]
        for entry in self.codex.list_commands():
            content.append(f"  {entry['name']:<9} {entry['description']}")
        content.append("")
        content.append("Type a command name such as 'chmod' to decrypt its entry.")

        panel_lines = draw_panel("HACKER CODEX", content, width - 4)
        return header + "\n" + "\n".join(panel_lines)

    def render_map(self, width: int) -> str:
        """Render the Tactical Mainframe Map screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "TACTICAL MAINFRAME MAP",
            width,
        )
        return header + "\n" + self.mainframe.render()

    def render_minigame(self, width: int) -> str:
        """Render the Chmod Security Minigame door."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "CHMOD SECURITY MINIGAME",
            width,
        )
        if self.minigame.active_puzzle is None:
            self.minigame.generate_puzzle()
        door = self.minigame.render_door()
        return header + "\n" + door

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
            return self.render_simple_screen("INVENTORY", width)

        if self.current_screen == self.SCREEN_MAP:
            return self.render_map(width)

        if self.current_screen == self.SCREEN_MINIGAME:
            return self.render_minigame(width)

        return ""


def create_app() -> RPGApp:
    """Create a default CyberShell application."""
    return RPGApp()


if __name__ == "__main__":
    app = create_app()
    print(app.render())
