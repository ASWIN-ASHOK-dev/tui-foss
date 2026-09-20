"""CyberShell RPG v2.0 - Visual FX & ASCII Art Assets.

Author: Gautham (Visual FX, ASCII Art & Terminal Box Specialist)
Status: Active

This module contains cyberpunk ASCII art, animated cyber logos, character
portraits for all story NPCs, Boss battle HUD components, siren banners,
and victory/defeat terminal screens.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# =============================================================================
# ANSI Color Sequences & Styling Helpers
# =============================================================================

RESET: str = "\033[0m"
BOLD: str = "\033[1m"
DIM: str = "\033[2m"

# Neon Cyberpunk Color Palette
CYAN: str = "\033[96m"
MAGENTA: str = "\033[95m"
GREEN: str = "\033[92m"
YELLOW: str = "\033[93m"
RED: str = "\033[91m"
BLUE: str = "\033[94m"
WHITE: str = "\033[97m"

ANSI_REGEX = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences to obtain raw character text."""
    return ANSI_REGEX.sub("", str(text))


def visual_len(text: str) -> int:
    """Calculate the visible terminal display length of a styled string."""
    return len(strip_ansi(text))


# =============================================================================
# Cyberpunk Title Logo (Day 1)
# =============================================================================

# Fits cleanly within standard 80-column terminals (width: 50 characters)
CYBER_LOGO: str = r"""   ____      _               ____  _          _ _ 
  / ___|   _| |__   ___ _ __/ ___|| |__   ___| | |
 | |  | | | | '_ \ / _ \ '__\___ \| '_ \ / _ \ | |
 | |__| |_| | |_) |  __/ |   ___) | | | |  __/ | |
  \____\__, |_.__/ \___|_|  |____/|_| |_|\___|_|_|
       |___/                                      """

# Compact single/two-line alternative
CYBER_LOGO_COMPACT: str = r"""[ ⚡ CYBERSHELL RPG v2.0 // TERMINAL CYBER ADVENTURE ⚡ ]"""

# Large block cyberpunk banner for wide terminals (width: 66 characters)
CYBER_LOGO_BLOCK: str = """  ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗  ██╗███████╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║██╔════╝
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗███████║█████╗  
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══██║██╔══╝  
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║██║  ██║███████╗
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝"""


def get_logo(styled: bool = False, wide: bool = False) -> str:
    """Return the CyberShell RPG logo, optionally formatted with neon styling."""
    raw = CYBER_LOGO_BLOCK if wide else CYBER_LOGO
    if not styled:
        return raw

    styled_lines = []
    colors = [CYAN, CYAN, MAGENTA, MAGENTA, CYAN, CYAN]
    lines = raw.strip("\n").splitlines()
    for idx, line in enumerate(lines):
        color = colors[idx % len(colors)]
        styled_lines.append(f"{BOLD}{color}{line}{RESET}")
    return "\n".join(styled_lines)


# =============================================================================
# NPC Character Portraits & Badges (Day 2)
# =============================================================================

# Compact 1-line operative / NPC badges for quick dialogue attribution
AVATARS: Dict[str, str] = {
    "byte": "▲_▲",
    "cipher": "(⌐■_■)",
    "glitch": "§_Ø",
    "aegis": "[■_■]",
    "sentinel": "[▼_▼]",
    "boss": "[▼_▼]",
    "overlord": "[▼_▼]",
}

# Detailed ASCII portraits formatted to consistent 18-column width
PORTRAIT_BYTE: List[str] = [
    r"   .---==---.    ",
    r"  /  /|  |\  \   ",
    r" |  (▲ _ ▲)  |   ",
    r"  \  \____/  /   ",
    r"   '---==---'    ",
    r"  <BYTE: DRONE>  ",
]

PORTRAIT_CIPHER: List[str] = [
    r"   .----------.  ",
    r"  /   ______   \ ",
    r" |   (⌐■ _ ■)   |",
    r" |    \ -- /    |",
    r"  \   /____\   / ",
    r"   '----------'  ",
    r" <CIPHER: HACKER>",
]

PORTRAIT_GLITCH: List[str] = [
    r"   .░▒▓▒░░▒▓▒.   ",
    r"  /  ╳ _ ╳ ?  \  ",
    r" |  ▓( §_Ø )░  | ",
    r" |   ▒~#~#~▒   | ",
    r"  \  ░▒▓▒░░▒  /  ",
    r"   '░▒▓▒░░▒▓''   ",
    r" <GLITCH: ROGUE> ",
]

PORTRAIT_AEGIS: List[str] = [
    r"   .╔══════╗.    ",
    r"  / ║  /\  ║ \   ",
    r" |  ║[■  ■]║  |  ",
    r" |  ║ |==| ║  |  ",
    r"  \ ╚══════╝ /   ",
    r"   '--------'    ",
    r" <AEGIS: DAEMON> ",
]

PORTRAIT_SENTINEL_BOSS: List[str] = [
    r"  <[ OVERLORD ]>    ",
    r" /════════════════\ ",
    r"|   ☠  [▼_▼]  ☠    |",
    r"|   |/\|▓▓▓|/\|    |",
    r" \════════════════/ ",
    r"  \   |      |   /  ",
    r" <SENTINEL  DAEMON> ",
]

PORTRAITS: Dict[str, List[str]] = {
    "byte": PORTRAIT_BYTE,
    "cipher": PORTRAIT_CIPHER,
    "glitch": PORTRAIT_GLITCH,
    "aegis": PORTRAIT_AEGIS,
    "sentinel": PORTRAIT_SENTINEL_BOSS,
    "boss": PORTRAIT_SENTINEL_BOSS,
    "overlord": PORTRAIT_SENTINEL_BOSS,
    "sentinel boss": PORTRAIT_SENTINEL_BOSS,
}


def get_portrait(npc_name: str, styled: bool = False) -> List[str]:
    """Retrieve the multi-line ASCII portrait for a specified NPC.

    Fallback is Byte (Drone) if name is unrecognized.
    """
    key = str(npc_name).strip().lower()
    raw_lines = PORTRAITS.get(key, PORTRAIT_BYTE)

    if not styled:
        return list(raw_lines)

    # Apply neon cyberpunk accent colors
    accent = CYAN
    if "cipher" in key:
        accent = GREEN
    elif "glitch" in key:
        accent = YELLOW
    elif "aegis" in key:
        accent = BLUE
    elif "boss" in key or "sentinel" in key or "overlord" in key:
        accent = RED

    return [f"{accent}{line}{RESET}" for line in raw_lines]


def get_avatar_badge(npc_name: str) -> str:
    """Return the compact ASCII badge for an NPC (e.g. '▲_▲' or '(⌐■_■)')."""
    key = str(npc_name).strip().lower()
    return AVATARS.get(key, "▲_▲")


# =============================================================================
# Boss Battle HUD & Siren Warning (Day 5)
# =============================================================================

def format_boss_hp_bar(
    hp: int,
    max_hp: int = 100,
    bar_width: int = 16,
    styled: bool = False,
) -> str:
    """Render a dynamic graphic health bar for the Sector 5 Boss."""
    hp_clamped = max(0, min(hp, max_hp))
    max_hp_safe = max(1, max_hp)
    pct = int((hp_clamped / max_hp_safe) * 100)

    filled = round(bar_width * hp_clamped / max_hp_safe)
    unfilled = bar_width - filled
    bar = "█" * filled + "░" * unfilled

    text = f"BOSS: [{bar}] {pct:>3}% ({hp_clamped}/{max_hp_safe} HP)"

    if not styled:
        return text

    # Critical = Red, Vulnerable = Yellow, Healthy = Magenta
    if pct <= 25:
        color = RED
    elif pct <= 50:
        color = YELLOW
    else:
        color = MAGENTA

    return f"{BOLD}{color}{text}{RESET}"


def get_siren_banner(
    text: str = "WARNING: ROGUE OVERLORD DETECTED - SECTOR 5 LOCKDOWN",
    width: int = 76,
    styled: bool = False,
) -> str:
    """Render a high-voltage cyber siren warning banner."""
    width = max(30, width)
    tag = "[!] ALERT [!]"
    inner_len = width - 4
    centered_text = text.center(inner_len)
    bar = "=" * inner_len

    if not styled:
        return (
            f"+-{bar}-+\n"
            f"| {tag.center(inner_len)} |\n"
            f"| {centered_text} |\n"
            f"+-{bar}-+"
        )

    return (
        f"{BOLD}{RED}+-{bar}-+{RESET}\n"
        f"{BOLD}{YELLOW}| {tag.center(inner_len)} |{RESET}\n"
        f"{BOLD}{RED}| {centered_text} |{RESET}\n"
        f"{BOLD}{RED}+-{bar}-+{RESET}"
    )


# =============================================================================
# Victory & Defeat Banners (Day 7)
# =============================================================================

VICTORY_BANNER: str = """╔══════════════════════════════════════════════════════════════════╗
║   ██████╗  ██████╗  ██████╗ ████████╗    ██╗   ██╗██╗███╗   ██╗  ║
║   ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██║   ██║██║████╗  ██║  ║
║   ██████╔╝██║   ██║██║   ██║   ██║       ██║   ██║██║██╔██╗ ██║  ║
║   ██╔══██╗██║   ██║██║   ██║   ██║       ╚██╗ ██╔╝██║██║╚██╗██║  ║
║   ██║  ██║╚██████╔╝╚██████╔╝   ██║        ╚████╔╝ ██║██║ ╚████║  ║
║   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚═╝  ╚═══╝  ║
║                                                                  ║
║             ★ MAINFRAME LIBERATED — MISSION COMPLETE ★           ║
╚══════════════════════════════════════════════════════════════════╝"""

DEFEAT_BANNER: str = """╔══════════════════════════════════════════════════════════════════╗
║   ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗          ║
║   ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║          ║
║   ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║          ║
║   ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║          ║
║   ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║          ║
║   ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝          ║
║                                                                  ║
║            💀 CRITICAL FAILURE: OPERATIVE TERMINATED 💀           ║
╚══════════════════════════════════════════════════════════════════╝"""


def get_victory_banner(styled: bool = False) -> str:
    """Return the victory banner celebrating sector liberation."""
    if not styled:
        return VICTORY_BANNER
    return f"{BOLD}{GREEN}{VICTORY_BANNER}{RESET}"


def get_defeat_banner(styled: bool = False) -> str:
    """Return the defeat banner signaling operative termination."""
    if not styled:
        return DEFEAT_BANNER
    return f"{BOLD}{RED}{DEFEAT_BANNER}{RESET}"
