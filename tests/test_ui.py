"""Unit Test Suite for CyberShell UI & Visual FX.

Authors: Poornendhu & Gautham
Covers:
- Gautham: ASCII title logos, NPC character portraits, boss HP bar, siren banner,
  terminal buffer widget, command history, combat ticker, and victory/defeat screens.
- Poornendhu: Double header, split panels, screen routing, and layout clipping.
Compatible with standard library unittest and pytest.
"""

from __future__ import annotations

import os
import sys
import unittest

# Ensure src/ is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cybershell.contracts import UIProtocol
from cybershell.ui.ascii_art import (
    AVATARS,
    CYBER_LOGO,
    CYBER_LOGO_BLOCK,
    CYBER_LOGO_COMPACT,
    DEFEAT_BANNER,
    PORTRAITS,
    VICTORY_BANNER,
    format_boss_hp_bar,
    get_avatar_badge,
    get_defeat_banner,
    get_logo,
    get_portrait,
    get_siren_banner,
    get_victory_banner,
    strip_ansi,
    visual_len,
)
from cybershell.ui.renderer import (
    draw_double_header,
    draw_panel,
    draw_split_panels,
    pad_to_width,
    truncate_styled,
)
from cybershell.ui.rpg_app import CombatTicker, RPGApp, TerminalBuffer


class TestASCIIArt(unittest.TestCase):
    """Test ASCII logo, character portraits, and visual banners."""

    def test_cyber_logo_dimensions_and_content(self) -> None:
        """Verify CYBER_LOGO fits standard 80-col terminal frames and has content."""
        lines = CYBER_LOGO.strip("\n").splitlines()
        self.assertGreater(len(lines), 3)
        for line in lines:
            self.assertLessEqual(visual_len(line), 80, f"Logo line exceeded 80 chars: {line}")

        # Check unstyled and styled get_logo()
        plain = get_logo(styled=False)
        self.assertIn("____", plain)
        self.assertEqual(strip_ansi(plain), plain)

        styled = get_logo(styled=True)
        self.assertIn("\033[", styled)
        self.assertEqual(strip_ansi(styled), plain)

        # Check wide block logo
        wide_plain = get_logo(styled=False, wide=True)
        self.assertIn("██████", wide_plain)

        # Check compact logo
        self.assertIn("CYBERSHELL", CYBER_LOGO_COMPACT)

    def test_all_npc_portraits_exist_and_are_uniform(self) -> None:
        """Verify all story NPCs have complete portraits with uniform line lengths."""
        required_npcs = ["byte", "cipher", "glitch", "aegis", "sentinel", "boss"]
        for npc in required_npcs:
            portrait = get_portrait(npc, styled=False)
            self.assertGreaterEqual(len(portrait), 5, f"Portrait for {npc} has fewer than 5 lines")

            # Check that line widths within each portrait are consistent (prevent jitter)
            widths = [visual_len(line) for line in portrait]
            first_width = widths[0]
            for idx, w in enumerate(widths):
                self.assertEqual(
                    w,
                    first_width,
                    f"Line {idx} of {npc} portrait width ({w}) != first line width ({first_width})",
                )

        # Verify fallback for unknown NPC defaults to Byte
        unknown = get_portrait("unknown_drone_xyz")
        byte_portrait = get_portrait("byte")
        self.assertEqual(unknown, byte_portrait)

        # Verify styled portraits preserve text and add ANSI codes
        styled_cipher = get_portrait("cipher", styled=True)
        plain_cipher = get_portrait("cipher", styled=False)
        self.assertEqual(len(styled_cipher), len(plain_cipher))
        for s_line, p_line in zip(styled_cipher, plain_cipher):
            self.assertEqual(strip_ansi(s_line), p_line)

    def test_avatar_badges(self) -> None:
        """Verify compact single-line avatars for quick dialogue attribution."""
        self.assertEqual(get_avatar_badge("byte"), "▲_▲")
        self.assertEqual(get_avatar_badge("cipher"), "(⌐■_■)")
        self.assertEqual(get_avatar_badge("glitch"), "§_Ø")
        self.assertEqual(get_avatar_badge("aegis"), "[■_■]")
        self.assertEqual(get_avatar_badge("sentinel"), "[▼_▼]")
        self.assertEqual(get_avatar_badge("boss"), "[▼_▼]")
        self.assertEqual(get_avatar_badge("non_existent"), "▲_▲")

    def test_boss_hp_bar_formatting(self) -> None:
        """Verify Boss HP gauge calculations across damage states."""
        # 100% Full Health
        full_bar = format_boss_hp_bar(100, 100, bar_width=10, styled=False)
        self.assertIn("BOSS: [██████████] 100% (100/100 HP)", full_bar)

        # 50% Health
        half_bar = format_boss_hp_bar(50, 100, bar_width=10, styled=False)
        self.assertIn("BOSS: [█████░░░░░]  50% (50/100 HP)", half_bar)

        # 0% Health
        dead_bar = format_boss_hp_bar(0, 100, bar_width=10, styled=False)
        self.assertIn("BOSS: [░░░░░░░░░░]   0% (0/100 HP)", dead_bar)

        # Clamping
        over_bar = format_boss_hp_bar(150, 100, bar_width=10, styled=False)
        self.assertIn("100%", over_bar)

        neg_bar = format_boss_hp_bar(-20, 100, bar_width=10, styled=False)
        self.assertIn("0%", neg_bar)

        # Styled output
        styled_bar = format_boss_hp_bar(20, 100, bar_width=10, styled=True)
        self.assertIn("\033[", styled_bar)
        self.assertEqual(strip_ansi(styled_bar), format_boss_hp_bar(20, 100, bar_width=10, styled=False))

    def test_siren_banner_rendering(self) -> None:
        """Verify siren banner formats within target width."""
        banner = get_siren_banner("SECTOR 5 LOCKDOWN", width=60, styled=False)
        self.assertIn("SECTOR 5 LOCKDOWN", banner)
        self.assertIn("ALERT", banner)
        lines = banner.splitlines()
        for line in lines:
            self.assertLessEqual(visual_len(line), 60)

    def test_victory_and_defeat_banners(self) -> None:
        """Verify victory and defeat banner formatting."""
        victory = get_victory_banner(styled=False)
        self.assertIn("MAINFRAME LIBERATED", victory)
        self.assertEqual(victory, VICTORY_BANNER)

        defeat = get_defeat_banner(styled=False)
        self.assertIn("OPERATIVE TERMINATED", defeat)
        self.assertEqual(defeat, DEFEAT_BANNER)

        # Styled banners preserve clean text
        self.assertEqual(strip_ansi(get_victory_banner(styled=True)), VICTORY_BANNER)
        self.assertEqual(strip_ansi(get_defeat_banner(styled=True)), DEFEAT_BANNER)


class TestTerminalBufferWidget(unittest.TestCase):
    """Test Gautham's terminal input widget and scrolling log buffer."""

    def setUp(self) -> None:
        self.buffer = TerminalBuffer(prompt="operative@cybershell:~$ ", max_lines=10)

    def test_initial_buffer_state(self) -> None:
        self.assertGreater(len(self.buffer.logs), 0)
        visible = self.buffer.get_visible_logs(5)
        self.assertLessEqual(len(visible), 5)
        self.assertEqual(self.buffer.prompt, "operative@cybershell:~$ ")

    def test_scrolling_buffer_capacity(self) -> None:
        """Buffer must cap total lines at max_lines and retain newest entries."""
        for i in range(25):
            self.buffer.add_log(f"log line {i}")

        self.assertEqual(len(self.buffer.logs), 10)
        self.assertEqual(self.buffer.logs[-1], "log line 24")
        self.assertEqual(self.buffer.logs[0], "log line 15")

    def test_add_command_and_history_navigation(self) -> None:
        """Commands must be logged and navigable via history."""
        self.buffer.add_command("pwd")
        self.buffer.add_command("ls -la")
        self.buffer.add_command("cat flag.txt")

        self.assertEqual(self.buffer.history, ["pwd", "ls -la", "cat flag.txt"])
        self.assertIn("operative@cybershell:~$ pwd", self.buffer.logs)

        # History previous (backward)
        self.assertEqual(self.buffer.history_prev(), "cat flag.txt")
        self.assertEqual(self.buffer.history_prev(), "ls -la")
        self.assertEqual(self.buffer.history_prev(), "pwd")
        # Clamped at oldest
        self.assertEqual(self.buffer.history_prev(), "pwd")

        # History next (forward)
        self.assertEqual(self.buffer.history_next(), "ls -la")
        self.assertEqual(self.buffer.history_next(), "cat flag.txt")
        self.assertEqual(self.buffer.history_next(), "")

    def test_clear_buffer(self) -> None:
        self.buffer.clear()
        self.assertEqual(len(self.buffer.logs), 0)
        visible = self.buffer.get_visible_logs(5)
        self.assertEqual(visible, ["(terminal ready)"])


class TestCombatLogTicker(unittest.TestCase):
    """Test Gautham's bottom broadcast strip and combat feedback."""

    def setUp(self) -> None:
        self.ticker = CombatTicker()

    def test_ticker_initial_state(self) -> None:
        self.assertIn("SYSTEM ONLINE", self.ticker.active_message)

    def test_ticker_categories_and_formatting(self) -> None:
        # Electrical Backlash
        self.ticker.log("ELECTRICAL BACKLASH! -15 HP", category="backlash")
        self.assertEqual(self.ticker.active_message, "⚡ ELECTRICAL BACKLASH! -15 HP")

        # Critical Hit
        self.ticker.log("CRITICAL HIT! Firewall breached", category="crit")
        self.assertEqual(self.ticker.active_message, "💥 CRITICAL HIT! Firewall breached")

        # Loot Acquired
        self.ticker.log("Quarantine Keychip acquired", category="loot")
        self.assertEqual(self.ticker.active_message, "🎁 Quarantine Keychip acquired")

        # Level Up / XP
        self.ticker.log("LEVEL UP! Rank: Junior Operative", category="level")
        self.assertEqual(self.ticker.active_message, "🌟 LEVEL UP! Rank: Junior Operative")

        # Objective
        self.ticker.log("OBJECTIVE ACQUIRED: +50 XP", category="objective")
        self.assertEqual(self.ticker.active_message, "🎯 OBJECTIVE ACQUIRED: +50 XP")

        # Siren Alert
        self.ticker.log("DAEMON INCOMING", category="siren")
        self.assertEqual(self.ticker.active_message, "🚨 DAEMON INCOMING")

    def test_ticker_render_width_containment(self) -> None:
        """Rendered ticker must strictly fit terminal width without line breaking."""
        self.ticker.log("CRITICAL HIT! Mainframe core compromised", category="crit")
        rendered = self.ticker.render(width=80)
        self.assertLessEqual(visual_len(rendered), 80)
        self.assertIn("CRITICAL HIT", rendered)

        # Narrow terminal truncation
        narrow_rendered = self.ticker.render(width=30)
        self.assertLessEqual(visual_len(narrow_rendered), 30)
        self.assertIn("…", narrow_rendered)


class TestRPGAppGauthamIntegration(unittest.TestCase):
    """Test RPGApp with Gautham's components and UIProtocol compliance."""

    def setUp(self) -> None:
        self.app = RPGApp(character_name="Byte", hp=100, max_hp=100, xp=50)

    def test_ui_protocol_conformance(self) -> None:
        """Verify RPGApp satisfies Amy's frozen UIProtocol."""
        self.assertTrue(
            isinstance(self.app, UIProtocol),
            "RPGApp does not satisfy UIProtocol from contracts.py",
        )

    def test_update_stats(self) -> None:
        self.app.update_stats(hp=85, max_hp=110, xp=150)
        self.assertEqual(self.app.hp, 85)
        self.assertEqual(self.app.max_hp, 110)
        self.assertEqual(self.app.xp, 150)

    def test_log_ticker(self) -> None:
        self.app.log_ticker("SECURITY ALARM TRIGGERED", category="siren")
        self.assertIn("SECURITY ALARM TRIGGERED", self.app.ticker.active_message)
        self.assertIn("🚨", self.app.ticker.active_message)

    def test_boss_hud_toggle_and_render(self) -> None:
        """Verify Boss HUD renders when active in Sector 5."""
        self.assertFalse(self.app.is_boss_active)
        self.app.set_boss_encounter(True, name="SENTINEL OVERLORD", hp=75, max_hp=100)
        self.assertTrue(self.app.is_boss_active)

        boss_hud = self.app.render_boss_hud(width=80)
        self.assertIn("SENTINEL OVERLORD", boss_hud)
        self.assertIn("75%", boss_hud)

        # Update Boss HP
        self.app.update_boss_hp(25)
        self.assertEqual(self.app.boss_hp, 25)
        updated_hud = self.app.render_boss_hud(width=80)
        self.assertIn("25%", updated_hud)

        # Render lab with Boss active
        lab_with_boss = self.app.render_lab(80)
        self.assertIn("SENTINEL OVERLORD", lab_with_boss)
        self.assertIn("MISSION INTEL", lab_with_boss)
        self.assertIn("TERMINAL", lab_with_boss)

    def test_title_screen_contains_logo_and_navigation(self) -> None:
        title = self.app.render_title(80)
        self.assertIn("CYBERSHELL RPG", title)
        self.assertIn("____", title)
        self.assertIn("[1] ENTER MISSION LAB", title)

    def test_zero_layout_clipping_at_80_columns(self) -> None:
        """Strict check: every line rendered at 80 cols must NOT exceed 80 chars."""
        # Title screen
        for line in self.app.render_title(80).splitlines():
            self.assertLessEqual(visual_len(line), 80, f"Title line clipped: {line}")

        # Mission Lab
        for line in self.app.render_lab(80).splitlines():
            self.assertLessEqual(visual_len(line), 80, f"Lab line clipped: {line}")

        # Boss HUD
        for line in self.app.render_boss_hud(80).splitlines():
            self.assertLessEqual(visual_len(line), 80, f"Boss HUD line clipped: {line}")

    def test_victory_and_defeat_screens(self) -> None:
        victory = self.app.render_victory(80)
        self.assertIn("MAINFRAME LIBERATED", victory)

        defeat = self.app.render_defeat(80)
        self.assertIn("OPERATIVE TERMINATED", defeat)


if __name__ == "__main__":
    unittest.main()
