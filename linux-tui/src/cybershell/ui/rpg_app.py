"""
CyberShell RPG application UI.

Handles screen routing and fixed-frame layout.
Game logic and terminal command processing are kept separate
so other team members can integrate their modules later.
"""

from cybershell.tools.chmod_minigame import ChmodMinigame
from cybershell.tools.codex import Codex
from cybershell.tools.map import MainframeMap, default_mainframe_map

from .renderer import (
    draw_double_header,
    draw_panel,
    draw_split_panels,
    terminal_size,
)


class RPGApp:
    """Main UI controller for CyberShell."""

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
    ):
        self.character_name = character_name
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp
        self.current_screen = self.SCREEN_TITLE

        # Integrated tactical tools (Akash: Codex / Map / Chmod Minigame).
        self.codex = Codex()
        self.mainframe: MainframeMap = default_mainframe_map()
        self.minigame = ChmodMinigame(difficulty="easy")

    def set_screen(self, screen: int) -> None:
        """Change the active screen."""
        if screen not in self.SCREEN_NAMES:
            raise ValueError(f"Unknown screen: {screen}")

        self.current_screen = screen

    def get_screen_name(self) -> str:
        """Return the name of the active screen."""
        return self.SCREEN_NAMES[self.current_screen]

    def render_title(self, width: int) -> str:
        """Render the title screen."""
        lines = [
            "CYBERSHELL RPG",
            "",
            "A TERMINAL-BASED CYBER ADVENTURE",
            "",
            "[1] ENTER MISSION LAB",
            "[2] CODEX",
            "[3] INVENTORY",
            "[4] MAP",
            "[5] MINIGAME",
            "",
            "Press a number to navigate.",
        ]

        return "\n".join(line.center(width) for line in lines)

    def render_lab(self, width: int) -> str:
        """Render the Mission Lab screen."""
        header = draw_double_header(
            self.character_name,
            self.hp,
            self.max_hp,
            self.xp,
            "MISSION LAB",
            width,
        )

        panels = draw_split_panels(
            "MISSION INTEL",
            [
                "Objective: Find the encrypted file",
                "Progress: 0/3",
                "Status: ACTIVE",
            ],
            "TERMINAL",
            [
                "operative@cybershell:~$",
                "Waiting for command...",
            ],
            width,
        )

        return header + "\n" + panels

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
