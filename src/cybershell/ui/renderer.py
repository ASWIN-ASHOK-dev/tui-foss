"""Byte's Linux Adventure - TUI Renderer.

Provides friendly terminal-safe utilities, rounded cards, and clean HUD elements.
"""

from __future__ import annotations

import re
import shutil
import textwrap
from typing import Iterable, List, Optional, Tuple

ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Rounded box characters for soft, friendly cards
PANEL_TOP_LEFT = "╭"
PANEL_TOP_RIGHT = "╮"
PANEL_BOTTOM_LEFT = "╰"
PANEL_BOTTOM_RIGHT = "╯"
PANEL_HORIZONTAL = "─"
PANEL_VERTICAL = "│"
PANEL_DIVIDER_LEFT = "├"
PANEL_DIVIDER_RIGHT = "┤"

# Kept for compatibility
TOP_LEFT = "╭"
TOP_RIGHT = "╮"
BOTTOM_LEFT = "╰"
BOTTOM_RIGHT = "╯"
HORIZONTAL = "─"
VERTICAL = "│"


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return ANSI_ESCAPE_RE.sub("", str(text))


def visual_len(text: str) -> int:
    """Return the visible terminal width of text, ignoring ANSI codes."""
    return len(strip_ansi(text))


def truncate_styled(text: str, max_width: int, suffix: str = "…") -> str:
    """Truncate styled text to a visible terminal width while preserving ANSI sequences."""
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


def horizontal_line(width: int, character: str = PANEL_HORIZONTAL) -> str:
    """Create a fixed-width horizontal line."""
    return character * max(0, width)


def draw_compact_hud(
    character_name: str = "Byte",
    level_num: int = 1,
    sector_name: str = "Look Around",
    xp: int = 0,
    streak: int = 0,
    objective_desc: str = "",
    hp: int = 100,
    max_hp: int = 100,
    width: int = 80,
    styled: bool = True,
    total_levels: int = 15,
) -> str:
    """Render the friendly, minimalist rounded card HUD."""
    card_width = min(max(40, width - 4), 74)
    inner_width = card_width - 2
    content_width = inner_width - 2

    title_left = f"🌱 {character_name}'s Adventure" if character_name else "🌱 Linux Adventure"
    title_right = f"Level {level_num:02d}/{total_levels:02d}"

    space_l1 = max(1, content_width - visual_len(title_left) - visual_len(title_right))
    if styled:
        l1_content = f"\033[1;92m{title_left}\033[0m" + (" " * space_l1) + f"\033[1;93m{title_right}\033[0m"
    else:
        l1_content = title_left + (" " * space_l1) + title_right
    l1_padded = pad_to_width(l1_content, content_width)

    # Line 2: Level name on left, XP / streak on right
    name_clean = sector_name.title()
    xp_clean = f"⭐ {xp} XP"
    if streak > 0:
        xp_clean += f" • 🔥 {streak}"
    space_l2 = max(1, content_width - visual_len(name_clean) - visual_len(xp_clean))
    if styled:
        l2_content = f"\033[1;97m{name_clean}\033[0m" + (" " * space_l2) + f"\033[1;93m{xp_clean}\033[0m"
    else:
        l2_content = name_clean + (" " * space_l2) + xp_clean
    l2_padded = pad_to_width(l2_content, content_width)

    # Line 3: Objective inside the card
    obj_str = objective_desc.strip()
    if not obj_str.startswith("🎯"):
        obj_str = f"🎯 {obj_str}"
    if visual_len(obj_str) > content_width:
        obj_str = truncate_styled(obj_str, content_width)
    if styled:
        l3_content = f"\033[1;92m{obj_str}\033[0m"
    else:
        l3_content = obj_str
    l3_padded = pad_to_width(l3_content, content_width)

    b_col = "\033[92m" if styled else ""
    b_rst = "\033[0m" if styled else ""

    box_lines = [
        f"{b_col}{PANEL_TOP_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_TOP_RIGHT}{b_rst}",
        f"{b_col}{PANEL_VERTICAL}{b_rst} {l1_padded} {b_col}{PANEL_VERTICAL}{b_rst}",
        f"{b_col}{PANEL_VERTICAL}{b_rst} {l2_padded} {b_col}{PANEL_VERTICAL}{b_rst}",
        f"{b_col}{PANEL_VERTICAL}{b_rst} {l3_padded} {b_col}{PANEL_VERTICAL}{b_rst}",
        f"{b_col}{PANEL_BOTTOM_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_BOTTOM_RIGHT}{b_rst}",
    ]

    return "\n".join(box_lines)


def draw_question_card(
    question_num: int = 1,
    total_questions: int = 1,
    question_text: str = "",
    options: Optional[List[str]] = None,
    scenario: str = "",
    width: int = 80,
    styled: bool = True,
) -> str:
    """Render a friendly 4-option challenge card without spoonfeeding the command."""
    if not question_text and not options:
        return ""

    card_width = min(max(40, width - 4), 74)
    inner_width = card_width - 2

    b_col = "\033[92m" if styled else ""
    b_rst = "\033[0m" if styled else ""
    top = f"{b_col}{PANEL_TOP_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_TOP_RIGHT}{b_rst}"
    bot = f"{b_col}{PANEL_BOTTOM_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_BOTTOM_RIGHT}{b_rst}"

    header_text = f"❓ QUESTION {question_num}/{total_questions} • YOUR TASK"
    if styled:
        h_styled = f"\033[1;93m{header_text}\033[0m"
        pad = max(0, inner_width - 2 - visual_len(h_styled))
        h_line = f"{h_styled}{' ' * pad}"
    else:
        h_line = f"{header_text:<{inner_width - 2}}"

    lines = [top]
    lines.append(f"{b_col}{PANEL_VERTICAL}{b_rst} {h_line} {b_col}{PANEL_VERTICAL}{b_rst}")

    if scenario:
        for s_line in textwrap.wrap(f"🌱 {scenario}", width=inner_width - 4):
            if styled:
                s_styled = f"\033[96m{s_line}\033[0m"
                pad = max(0, inner_width - 4 - visual_len(s_styled))
                content = f"  {s_styled}{' ' * pad}  "
            else:
                content = f"  {s_line:<{inner_width - 4}}  "
            lines.append(f"{b_col}{PANEL_VERTICAL}{b_rst}{content}{b_col}{PANEL_VERTICAL}{b_rst}")

    if question_text:
        for q_line in textwrap.wrap(question_text, width=inner_width - 4):
            if styled:
                q_styled = f"\033[1;97m{q_line}\033[0m"
                pad = max(0, inner_width - 4 - visual_len(q_styled))
                content = f"  {q_styled}{' ' * pad}  "
            else:
                content = f"  {q_line:<{inner_width - 4}}  "
            lines.append(f"{b_col}{PANEL_VERTICAL}{b_rst}{content}{b_col}{PANEL_VERTICAL}{b_rst}")

    letters = ["A", "B", "C", "D"]
    for idx, opt in enumerate((options or [])[:4]):
        letter = letters[idx] if idx < len(letters) else str(idx + 1)
        prefix = f"[{letter}] "
        avail_w = inner_width - 4 - len(prefix)
        wrapped = textwrap.wrap(opt, width=avail_w) or [""]
        for w_idx, part in enumerate(wrapped):
            if w_idx == 0:
                if styled:
                    p_styled = f"\033[1;93m[{letter}]\033[0m \033[97m{part}\033[0m"
                    pad = max(0, inner_width - 4 - visual_len(p_styled))
                    content = f"  {p_styled}{' ' * pad}  "
                else:
                    content = f"  {prefix}{part:<{avail_w}}  "
            else:
                indent = " " * len(prefix)
                if styled:
                    p_styled = f"\033[97m{part}\033[0m"
                    pad = max(0, inner_width - 4 - len(indent) - visual_len(p_styled))
                    content = f"  {indent}{p_styled}{' ' * pad}  "
                else:
                    content = f"  {indent}{part:<{avail_w}}  "
            lines.append(f"{b_col}{PANEL_VERTICAL}{b_rst}{content}{b_col}{PANEL_VERTICAL}{b_rst}")

    tip = "💡 Type the command or option letter [A, B, C, D] to execute!"
    for t_line in textwrap.wrap(tip, width=inner_width - 4):
        if styled:
            t_styled = f"\033[2;93m{t_line}\033[0m"
            pad = max(0, inner_width - 4 - visual_len(t_styled))
            content = f"  {t_styled}{' ' * pad}  "
        else:
            content = f"  {t_line:<{inner_width - 4}}  "
        lines.append(f"{b_col}{PANEL_VERTICAL}{b_rst}{content}{b_col}{PANEL_VERTICAL}{b_rst}")

    lines.append(bot)
    return "\n".join(lines)


def draw_field_manual_card(
    page: int = 1,
    width: int = 80,
    styled: bool = True,
) -> str:
    """Render a compact, self-contained Field Manual & Rules card (strictly <= 16 lines).

    Designed to fit completely on standard 80x24 terminal screens with zero scrolling.
    Page 1: Rules & Core Philosophy (14 lines)
    Page 2: Handy Command Quick Reference (15 lines)
    """
    card_width = min(max(40, width - 4), 74)
    inner_width = card_width - 2

    b_col = "\033[92m" if styled else ""
    b_rst = "\033[0m" if styled else ""
    top = f"{b_col}{PANEL_TOP_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_TOP_RIGHT}{b_rst}"
    bot = f"{b_col}{PANEL_BOTTOM_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_BOTTOM_RIGHT}{b_rst}"
    div = f"{b_col}{PANEL_DIVIDER_LEFT}{PANEL_HORIZONTAL * inner_width}{PANEL_DIVIDER_RIGHT}{b_rst}"

    def row(s_text: str, p_text: str) -> str:
        if styled:
            trunc = truncate_styled(s_text, inner_width)
            pad = max(0, inner_width - visual_len(trunc))
            return f"{b_col}{PANEL_VERTICAL}{b_rst}{trunc}{' ' * pad}{b_col}{PANEL_VERTICAL}{b_rst}"
        else:
            trunc = truncate_styled(p_text, inner_width)
            pad = max(0, inner_width - visual_len(trunc))
            return f"{PANEL_VERTICAL}{trunc}{' ' * pad}{PANEL_VERTICAL}"

    lines = [top]
    if page == 1:
        h1_p = r"  (\__/)    📖 FIELD MANUAL & RULES  [Page 1/2]"
        h1_s = r"  \033[92m(\__/)\033[0m    \033[1;93m📖 FIELD MANUAL & RULES\033[0m  \033[2m[Page 1/2]\033[0m"
        h2_p = "  (・ω・)   Welcome to Byte's Linux Adventure!"
        h2_s = "  \033[92m(・ω・)\033[0m   \033[1;97mWelcome to Byte's Linux Adventure!\033[0m"
        h3_p = "  / >🌱     Learn real skills safely with zero penalties!"
        h3_s = "  \033[92m/ >🌱\033[0m     \033[96mLearn real skills safely with zero penalties!\033[0m"
        lines.extend([row(h1_s, h1_p), row(h2_s, h2_p), row(h3_s, h3_p), div])

        rules = [
            ("  🌱 1. 15 Levels   : Bite-sized journey from 'pwd' to pipes.",
             "  \033[92m🌱 1. 15 Levels\033[0m   : \033[97mA bite-sized journey from 'pwd' to pipes.\033[0m"),
            ("  🌱 2. Real Shell  : Type commands (pwd, ls, cd) or options (A-D).",
             "  \033[92m🌱 2. Real Shell\033[0m  : \033[97mType commands (pwd, ls, cd) or options (A-D).\033[0m"),
            ("  🌱 3. 100% Safe   : Mistakes deal ZERO damage! Explore freely.",
             "  \033[92m🌱 3. 100% Safe\033[0m   : \033[97mMistakes deal \033[1;92mZERO damage\033[0m\033[97m! Explore freely.\033[0m"),
            ("  🌱 4. Easy Hints  : Type '?' or 'hint' anytime for guidance.",
             "  \033[92m🌱 4. Easy Hints\033[0m  : \033[97mType \033[1;93m'?'\033[0m\033[97m or \033[1;93m'hint'\033[0m\033[97m anytime for guidance.\033[0m"),
            ("  🌱 5. Progress Map: Type 'map' to see your level journey.",
             "  \033[92m🌱 5. Progress Map\033[0m: \033[97mType \033[1;93m'map'\033[0m\033[97m to see your level journey.\033[0m"),
            ("  🌱 6. Main Menu   : Type 'menu' or press ESC to safely exit.",
             "  \033[92m🌱 6. Main Menu\033[0m   : \033[97mType \033[1;93m'menu'\033[0m\033[97m or press \033[1;93mESC\033[0m\033[97m to safely exit.\033[0m"),
        ]
        for p, s in rules:
            lines.append(row(s, p))

        lines.append(div)
        tip_p = "  💡 Tip: Zero penalties. Relax, experiment, and have fun!"
        tip_s = "  \033[2;93m💡 Tip: Zero penalties. Relax, experiment, and have fun!\033[0m"
        lines.append(row(tip_s, tip_p))
    else:
        h1_p = r"  (\__/)    📖 FIELD MANUAL & RULES  [Page 2/2]"
        h1_s = r"  \033[92m(\\__/)\033[0m    \033[1;93m📖 FIELD MANUAL & RULES\033[0m  \033[2m[Page 2/2]\033[0m"
        h2_p = "  (・ω・)   Handy Linux Command Reference"
        h2_s = "  \033[92m(・ω・)\033[0m   \033[1;97mHandy Linux Command Reference\033[0m"
        h3_p = "  / >🌱     Essential tools for exploring the terminal:"
        h3_s = "  \033[92m/ >🌱\033[0m     \033[96mEssential tools for exploring the terminal:\033[0m"
        lines.extend([row(h1_s, h1_p), row(h2_s, h2_p), row(h3_s, h3_p), div])

        cmds = [
            ("  📂 pwd, ls, ls -a : View current folder & list files.",
             "  \033[1;93m📂 pwd, ls, ls -a\033[0m : \033[97mView current folder & list files.\033[0m"),
            ("  📁 cd <folder>    : Move between directories ('cd ..' moves up).",
             "  \033[1;93m📁 cd <folder>\033[0m    : \033[97mMove between directories ('cd ..' moves up).\033[0m"),
            ("  📄 cat, grep      : Read file contents and search for words.",
             "  \033[1;93m📄 cat, grep\033[0m      : \033[97mRead file contents and search for words.\033[0m"),
            ("  🔒 chmod <perm>   : Change file permissions (e.g. 755 or +x).",
             "  \033[1;93m🔒 chmod <perm>\033[0m   : \033[97mChange file permissions (e.g. 755 or +x).\033[0m"),
            ("  📊 wc, sort, uniq : Count lines/words and sort text output.",
             "  \033[1;93m📊 wc, sort, uniq\033[0m : \033[97mCount lines/words and sort text output.\033[0m"),
            ("  🔄 | (pipe), >, >>: Chain commands and redirect output.",
             "  \033[1;93m🔄 | (pipe), >, >>\033[0m: \033[97mChain commands and redirect output.\033[0m"),
            ("  🗺️  map, codex, ?  : View progress map, command codex, or hints.",
             "  \033[1;93m🗺️  map, codex, ?\033[0m  : \033[97mView progress map, command codex, or hints.\033[0m"),
        ]
        for p, s in cmds:
            lines.append(row(s, p))

        lines.append(div)
        tip_p = "  💡 Tip: All commands run in a safe virtual file system."
        tip_s = "  \033[2;93m💡 Tip: All commands run in a safe virtual file system.\033[0m"
        lines.append(row(tip_s, tip_p))

    lines.append(bot)
    return "\n".join(lines)


def draw_control_footer(
    screen_type: str = "terminal",
    width: int = 80,
    styled: bool = True,
) -> str:
    """Render a context-sensitive footer showing available controls."""
    if screen_type == "terminal":
        text = "ENTER Run    ↑↓ History    ESC Menu    ? Help"
    elif screen_type == "menu":
        text = "↑↓ Select    ENTER Choose    ESC Back"
    else:
        text = "ENTER Continue    ESC Back"

    if styled:
        return f"\033[2m{text}\033[0m"
    return text


def draw_double_header(
    character_name: str,
    hp: int,
    max_hp: int,
    xp: int,
    sector_title: str,
    width: int = 80,
    styled: bool = False,
) -> str:
    """Render a clean rounded header card for information and tool screens."""
    width = max(24, width)
    inner_width = width - 2

    title_left = "🌱 BYTE'S LINUX ADVENTURE"
    title_right = f"⭐ {xp} XP"
    space = max(1, inner_width - visual_len(title_left) - visual_len(title_right))

    if styled:
        line_one = f"\033[1;92m{title_left}\033[0m" + (" " * space) + f"\033[1;93m{title_right}\033[0m"
        line_two = f"\033[1;97m{sector_title}\033[0m"
        b_col = "\033[92m"
        b_rst = "\033[0m"
    else:
        line_one = title_left + (" " * space) + title_right
        line_two = sector_title
        b_col = ""
        b_rst = ""

    line_one = pad_to_width(line_one, inner_width)
    line_two = pad_to_width(line_two, inner_width, "center")

    return "\n".join(
        [
            b_col + PANEL_TOP_LEFT + horizontal_line(inner_width) + PANEL_TOP_RIGHT + b_rst,
            b_col + PANEL_VERTICAL + b_rst + line_one + b_col + PANEL_VERTICAL + b_rst,
            b_col + PANEL_VERTICAL + b_rst + line_two + b_col + PANEL_VERTICAL + b_rst,
            b_col + PANEL_BOTTOM_LEFT + horizontal_line(inner_width) + PANEL_BOTTOM_RIGHT + b_rst,
        ]
    )


def draw_panel(
    title: str,
    content: Iterable[str],
    width: int,
    styled: bool = False,
    border_color: str = "",
) -> List[str]:
    """Render a rounded-border panel card."""
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
    """Render side-by-side rounded panels."""
    width = max(30, width)
    gap = max(1, gap)

    available = width - gap
    left_width = available // 2
    right_width = available - left_width

    left_border = "\033[93m" if styled else ""
    right_border = "\033[92m" if styled else ""

    left_items = list(left_content)
    right_items = list(right_content)
    target_height = max(len(left_items), len(right_items))

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