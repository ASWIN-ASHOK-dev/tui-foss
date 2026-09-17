"""
CyberShell TUI renderer.

Provides terminal-safe utilities and fixed-frame rendering helpers.
"""

import re
import shutil
from typing import Iterable

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


def terminal_size(default_width: int = 80, default_height: int = 24) -> tuple[int, int]:
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
) -> str:
    """
    Render the CyberShell top HUD using a double border.

    The returned string contains exactly three terminal lines.
    """
    width = max(20, width)

    inner_width = width - 2

    hp = max(0, hp)
    max_hp = max(1, max_hp)
    hp_percent = min(100, int((hp / max_hp) * 100))

    hp_bar_width = 10
    hp_filled = round(hp_bar_width * hp_percent / 100)
    hp_bar = "█" * hp_filled + "░" * (hp_bar_width - hp_filled)

    line_one = (
        f"OPERATIVE: {character_name}"
        f"    HP: [{hp_bar}] {hp_percent:>3}%"
        f"    XP: {xp}"
    )

    line_two = sector_title

    line_one = pad_to_width(line_one, inner_width)
    line_two = pad_to_width(line_two, inner_width, "center")

    return "\n".join(
        [
            TOP_LEFT + horizontal_line(inner_width) + TOP_RIGHT,
            VERTICAL + line_one + VERTICAL,
            VERTICAL + line_two + VERTICAL,
            BOTTOM_LEFT + horizontal_line(inner_width) + BOTTOM_RIGHT,
        ]
    )


def draw_panel(title: str, content: Iterable[str], width: int) -> list[str]:
    """Render one rounded-border panel."""
    width = max(8, width)
    inner_width = width - 2
    content_width = inner_width - 2

    lines = [
        PANEL_TOP_LEFT
        + PANEL_HORIZONTAL * (width - 2)
        + PANEL_TOP_RIGHT
    ]

    title_text = truncate_styled(f" {title} ", content_width)

    lines.append(
        PANEL_VERTICAL
        + " "
        + pad_to_width(title_text, content_width)
        + " "
        + PANEL_VERTICAL
    )

    for item in content:
        item = truncate_styled(str(item), content_width)

        lines.append(
            PANEL_VERTICAL
            + " "
            + pad_to_width(item, content_width)
            + " "
            + PANEL_VERTICAL
        )

    lines.append(
        PANEL_BOTTOM_LEFT
        + PANEL_HORIZONTAL * (width - 2)
        + PANEL_BOTTOM_RIGHT
    )

    return lines

def draw_split_panels(
    left_title: str,
    left_content: Iterable[str],
    right_title: str,
    right_content: Iterable[str],
    width: int = 80,
    gap: int = 2,
) -> str:
    """
    Render Mission Intel and Terminal as side-by-side panels.
    """
    width = max(30, width)
    gap = max(1, gap)

    available = width - gap
    left_width = available // 2
    right_width = available - left_width

    left = draw_panel(left_title, left_content, left_width)
    right = draw_panel(right_title, right_content, right_width)

    height = max(len(left), len(right))

    left += [" " * left_width] * (height - len(left))
    right += [" " * right_width] * (height - len(right))

    return "\n".join(
        left_line + (" " * gap) + right_line
        for left_line, right_line in zip(left, right)
    )