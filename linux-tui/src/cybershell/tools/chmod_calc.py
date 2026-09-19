"""Chmod Permission Calculator & Decrypter for CyberShell RPG v2.0.

Author: Akash (Hacker Codex & Chmod Minigame)
Role: Shared conversion logic between octal and symbolic Linux permission
      formats, plus human-readable security analysis. Reused by the
      chmod security minigame so the same rules power both tools.

The heavy lifting (9-bit <-> octal <-> symbolic bit mapping) is delegated
to ``cybershell.engine.node`` so there is no duplicated conversion logic;
this module layers strict, game-friendly validation and security reporting
on top of that shared machinery.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Union

from cybershell.engine.node import format_octal, format_symbolic, parse_permissions

# ---------------------------------------------------------------------------
# Validation errors & constants
# ---------------------------------------------------------------------------

TRIAD_ORDER: Tuple[str, str, str] = ("r", "w", "x")
TRIAD_LABELS: Tuple[str, str, str] = ("Owner", "Group", "Others")
SYMBOLIC_MASK: str = "rwxrwxrwx"
_OCTAL_PATTERN = re.compile(r"^[0-7]{3}$")
_TYPE_PREFIXES = frozenset(("-", "d", "l", "b", "c", "s", "p"))


class ChmodError(ValueError):
    """Raised when a permission value is invalid, malformed, or unsupported."""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _coerce_octal(value: Union[str, int]) -> str:
    """Convert a raw octal input (``'755'`` or ``755``) into a digit string."""
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:03d}"
    if isinstance(value, bool):
        raise ChmodError(f"Invalid octal permission {value!r}: expected digits")
    return str(value).strip()


def validate_octal(value: Union[str, int]) -> str:
    """Validate an octal permission and return a canonical 3-digit string.

    Accepts ``'755'`` and ``755``. Rejects non-numeric input, values whose
    digits are outside octal range (8/9), and anything that is not exactly
    three digits long.
    """
    raw = _coerce_octal(value)
    if not raw:
        raise ChmodError("Permission  is empty: expected 3 octal digits")
    if not raw.isdecimal():
        raise ChmodError(
            f"Invalid octal permission {raw!r}: must be numeric (e.g. '755')"
        )
    if _OCTAL_PATTERN.match(raw) is None:
        if len(raw) != 3:
            raise ChmodError(
                f"Invalid octal permission {raw!r}: expected exactly 3 digits, got {len(raw)}"
            )
        raise ChmodError(
            f"Invalid octal permission {raw!r}: digits 8 and 9 are not valid octal"
        )
    return raw


def validate_symbolic(value: str) -> str:
    """Validate a symbolic permission and return a canonical 9-char string.

    Accepts the plain ``'rwxr-xr-x'`` form and the ``ls -l`` style
    ``'-rwxr-xr-x'`` / ``'drwxr-xr-x'`` form (a leading type indicator is
    allowed). Rejects incorrect lengths, unknown characters, and symbolic
    strings where a letter appears out of its canonical rwx position.
    """
    raw = str(value).strip()
    if not raw:
        raise ChmodError("Permission is empty: expected 9 symbolic characters")

    if len(raw) == 10 and raw[0] in _TYPE_PREFIXES:
        raw = raw[1:]

    if len(raw) != 9:
        raise ChmodError(
            f"Invalid symbolic permission {value!r}: expected exactly 9 "
            f"characters (owner/group/others triads), got {len(raw)}"
        )

    for index, char in enumerate(raw):
        if char not in "rwx-":
            raise ChmodError(
                f"Malformed symbolic permission {value!r}: unsupported character "
                f"{char!r} at position {index + 1}"
            )
        if char != "-" and char != SYMBOLIC_MASK[index]:
            raise ChmodError(
                f"Malformed symbolic permission {value!r}: {char!r} is out of "
                f"order at position {index + 1} (expected r/w/x slot)"
            )
    return raw


# ---------------------------------------------------------------------------
# Core conversions (reusing cybershell.engine.node bit mapping)
# ---------------------------------------------------------------------------

def parse_octal(value: Union[str, int]) -> int:
    """Parse an octal permission into a 9-bit integer mode (e.g. 0o755)."""
    return parse_permissions(validate_octal(value))


def parse_symbolic(value: str) -> int:
    """Parse a symbolic permission into a 9-bit integer mode (e.g. 0o755)."""
    return parse_permissions(validate_symbolic(value))


def parse_permission(value: Union[str, int]) -> int:
    """Parse either an octal (``'755'``) or symbolic (``'rwxr-xr-x'``) mode."""
    if isinstance(value, int) and not isinstance(value, bool):
        return parse_octal(value)
    raw = str(value).strip()
    if not raw:
        raise ChmodError("Permission is empty: expected a mode such as '755'")
    if raw[0].isdecimal():
        return parse_octal(raw)
    return parse_symbolic(raw)


def octal_to_symbolic(value: Union[str, int]) -> str:
    """Convert an octal mode (``'755'``) into a 9-char symbolic string."""
    mode = parse_octal(value)
    return format_symbolic(mode)[1:]


def symbolic_to_octal(value: str) -> str:
    """Convert a symbolic mode (``'rwxr-xr-x'``) into a 3-digit octal string."""
    mode = parse_symbolic(value)
    return format_octal(mode)


# ---------------------------------------------------------------------------
# Triplet decomposition & security reporting
# ---------------------------------------------------------------------------

def get_triplets(value: Union[str, int]) -> Tuple[str, str, str]:
    """Split a permission into owner/group/others symbolic triplets."""
    symbolic = octal_to_symbolic(value)
    return symbolic[0:3], symbolic[3:6], symbolic[6:9]


def describe_triad(triad: str, label: str = "") -> str:
    """Human-readable description of a single permission triad."""
    kind = f"{label} " if label else ""
    capabilities = [
        token for token, char in zip(("read", "write", "execute"), triad) if char != "-"
    ]
    if not capabilities:
        return f"{kind}has no access permissions."
    if len(capabilities) == 1:
        return f"{kind}can {capabilities[0]}."
    if len(capabilities) == 2:
        return f"{kind}can {capabilities[0]} and {capabilities[1]}."
    return f"{kind}can {capabilities[0]}, {capabilities[1]} and {capabilities[2]}."


def security_info(value: Union[str, int]) -> Dict[str, object]:
    """Return structured security analysis for a permission value."""
    octal = validate_octal(value)
    symbolic = octal_to_symbolic(octal)
    owner, group, others = get_triplets(octal)
    return {
        "octal": octal,
        "symbolic": symbolic,
        "triplets": {
            "owner": owner,
            "group": group,
            "others": others,
        },
        "capabilities": {
            label: describe_triad(triad, label)
            for label, triad in zip(TRIAD_LABELS, (owner, group, others))
        },
    }


def security_report(value: Union[str, int]) -> str:
    """Render a formatted security breakdown for a permission value.

    Returns something like::

        755
        Owner:  rwx
        Group:  r-x
        Others: r-x

        Security:
        Owner can read/write/execute.
        Group can read/execute.
        Others can read/execute.
    """
    info = security_info(value)
    triplets = info["triplets"]
    capabilities = info["capabilities"]

    lines: List[str] = [info["octal"]]
    triples = (triplets["owner"], triplets["group"], triplets["others"])
    for label, triad in zip(TRIAD_LABELS, triples):
        lines.append(f"{label}:  {triad}")

    lines.append("")
    lines.append("Security:")
    lines.append(capabilities["Owner"])
    lines.append(capabilities["Group"])
    lines.append(capabilities["Others"])
    return "\n".join(lines)
