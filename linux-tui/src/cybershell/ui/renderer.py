"""
CyberShell TUI renderer.

Provides terminal-safe utilities and fixed-frame rendering helpers.
"""

from __future__ import annotations

import re
import shutil
from typing import Iterable, List, Tuple

ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Unicode box-drawing characters used by the CyberShell UI.
TOP_LEFT = "╔"
TOP_RIGHT = "╗"
BOTTOM_LEFT = "╚"
BOTTOM_RIGHT = "╝"
HORIZONTAL = "═"
VERTICAL = "║"

PANEL_TOP_LEFT = "╭"
PANEL_TOP_RIGHT = "╮"
PANEL_BOTTOM_LEFT = "╰"
PANEL_BOTTOM_RIGHT = "╯"
PANEL_HORIZONTAL = "─"
PANEL_VERTICAL = "│"


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return ANSI_ESCAPE_RE.sub("", str(text))


def visual_len(text: str) -> int:
    """Return the visible terminal width of text, ignoring ANSI codes."""
    return len(strip_ansi(text))


def truncate_styled(text: str, max_width: int, suffix: str = "…") -> str:
    """
    Truncate styled text to a visible terminal width.

    ANSI escape sequences are preserved while calculating width.
    """
    if max_width <= 0:
        return ""

    if visual_len(text) <= max_width:
        return text

    suffix_width = visual_len(suffix)

    if suffix_width >= max_width:
        return suffix[:max_width]

    target_width = max_width - suffix_width
    result = []
    visible_width = 0
    index = 0

    while index < len(text) and visible_width < target_width:
        match = ANSI_ESCAPE_RE.match(text, index)

        if match:
            result.append(match.group())
            index = match.end()
            continue

        result.append(text[index])
        visible_width += 1
        index += 1

    return "".join(result) + suffix


def terminal_size(default_width: int = 80, default_height: int = 24) -> Tuple[int, int]:
    """Return the current terminal size with safe fallbacks."""
    size = shutil.get_terminal_size((default_width, default_height))
    return size.columns, size.lines


def pad_to_width(text: str, width: int, align: str = "left") -> str:
    """Pad visible text to exactly the requested terminal width."""
    text = str(text)

    if width <= 0:
        return ""

    if visual_len(text) > width:
        text = truncate_styled(text, width)

    padding = width - visual_len(text)

    if align == "right":
        return " " * padding + text

    if align == "center":
        left = padding // 2
        right = padding - left
        return " " * left + text + " " * right

    return text + " " * padding


def horizontal_line(width: int, character: str = HORIZONTAL) -> str:
    """Create a fixed-width horizontal line."""
    return character * max(0, width)


def draw_double_header(
    character_name: str,
    hp: int,
    max_hp: int,
    xp: int,
    sector_title: str,
    width: int = 80,
    styled: bool = False,
) -> str:
    """
    Render the CyberShell top HUD using a double border.

    The returned string contains exactly four terminal lines.
    """
    width = max(20, width)

    inner_width = width - 2

    hp = max(0, hp)
    max_hp = max(1, max_hp)
    hp_percent = min(100, int((hp / max_hp) * 100))

    hp_bar_width = 10
    hp_filled = round(hp_bar_width * hp_percent / 100)
    hp_bar = "█" * hp_filled + "░" * (hp_bar_width - hp_filled)

    if styled:
        if hp_percent > 50:
            hp_color = "\033[92m"  # Bright Green
        elif hp_percent > 20:
            hp_color = "\033[93m"  # Bright Yellow
        else:
            hp_color = "\033[91m"  # Bright Red

        line_one = (
            f"\033[1;96mOPERATIVE:\033[0m \033[1;97m{character_name}\033[0m"
            f"    \033[1;97mHP:\033[0m [{hp_color}{hp_bar}\033[0m] \033[1;97m{hp_percent:>3}%\033[0m"
            f"    \033[1;95mXP:\033[0m \033[1;97m{xp}\033[0m"
        )
        line_two = f"\033[1;93m{sector_title}\033[0m"
        b_col = "\033[96m"
        b_rst = "\033[0m"
    else:
        line_one = (
            f"OPERATIVE: {character_name}"
            f"    HP: [{hp_bar}] {hp_percent:>3}%"
            f"    XP: {xp}"
        )
        line_two = sector_title
        b_col = ""
        b_rst = ""

    line_one = pad_to_width(line_one, inner_width)
    line_two = pad_to_width(line_two, inner_width, "center")

    return "\n".join(
        [
            b_col + TOP_LEFT + horizontal_line(inner_width) + TOP_RIGHT + b_rst,
            b_col + VERTICAL + b_rst + line_one + b_col + VERTICAL + b_rst,
            b_col + VERTICAL + b_rst + line_two + b_col + VERTICAL + b_rst,
            b_col + BOTTOM_LEFT + horizontal_line(inner_width) + BOTTOM_RIGHT + b_rst,
        ]
    )


def draw_panel(
    title: str,
    content: Iterable[str],
    width: int,
    styled: bool = False,
    border_color: str = "",
) -> List[str]:
    """Render one rounded-border panel."""
    width = max(8, width)
    inner_width = width - 2
    content_width = inner_width - 2

    b_col = border_color if styled else ""
    b_rst = "\033[0m" if styled and b_col else ""

    lines = [
        b_col + PANEL_TOP_LEFT + PANEL_HORIZONTAL * (width - 2) + PANEL_TOP_RIGHT + b_rst
    ]

    title_text = truncate_styled(f" {title} ", content_width)

    lines.append(
        b_col + PANEL_VERTICAL + b_rst
        + " "
        + pad_to_width(title_text, content_width)
        + " "
        + b_col + PANEL_VERTICAL + b_rst
    )

    for item in content:
        item = truncate_styled(str(item), content_width)

        lines.append(
            b_col + PANEL_VERTICAL + b_rst
            + " "
            + pad_to_width(item, content_width)
            + " "
            + b_col + PANEL_VERTICAL + b_rst
        )

    lines.append(
        b_col + PANEL_BOTTOM_LEFT + PANEL_HORIZONTAL * (width - 2) + PANEL_BOTTOM_RIGHT + b_rst
    )

    return lines


def draw_split_panels(
    left_title: str,
    left_content: Iterable[str],
    right_title: str,
    right_content: Iterable[str],
    width: int = 80,
    gap: int = 2,
    styled: bool = False,
) -> str:
    """
    Render Mission Intel and Terminal as side-by-side panels.
    """
    width = max(30, width)
    gap = max(1, gap)

    available = width - gap
    left_width = available // 2
    right_width = available - left_width

    left_border = "\033[96m" if styled else ""
    right_border = "\033[92m" if styled else ""

    left_items = list(left_content)
    right_items = list(right_content)
    target_height = max(len(left_items), len(right_items))

    # Pad inner content so both panels have matching side borders and bottom borders
    left_items += [""] * (target_height - len(left_items))
    right_items += [""] * (target_height - len(right_items))

    left = draw_panel(left_title, left_items, left_width, styled=styled, border_color=left_border)
    right = draw_panel(right_title, right_items, right_width, styled=styled, border_color=right_border)

    height = max(len(left), len(right))

    left += [" " * left_width] * (height - len(left))
    right += [" " * right_width] * (height - len(right))

    return "\n".join(
        left_line + (" " * gap) + right_line
        for left_line, right_line in zip(left, right)
    )