"""Chmod Security Minigame - lockpicking door puzzle for CyberShell RPG v2.0.

Author: Akash (Hacker Codex & Chmod Minigame)
Role: An interactive "security door" puzzle where the player is shown a
      symbolic permission pattern and must punch in the correct octal code.
      Permission math is delegated to ``chmod_calc``; XP is awarded through
      the shared ``PlayerStats`` progression system exactly once per door.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union

from cybershell.contracts import PlayerStats
from cybershell.tools.chmod_calc import ChmodError, octal_to_symbolic, validate_octal

# Difficulty levels
EASY: str = "easy"
MEDIUM: str = "medium"
HARD: str = "hard"
DIFFICULTIES: Tuple[str, str, str] = (EASY, MEDIUM, HARD)

# XP awarded for solving a door at each difficulty (medium matches the +50
# XP example shown in the mission brief).
XP_REWARDS: Dict[str, int] = {EASY: 25, MEDIUM: 50, HARD: 100}

# Curated octal pools for the lower difficulties.
EASY_CODES: Tuple[str, ...] = ("755", "644", "700", "600")
MEDIUM_CODES: Tuple[str, ...] = ("754", "764", "740", "664")

DOOR_WIDTH = 42


@dataclass
class Puzzle:
    """A single generated security door puzzle."""

    permission: str
    answer: str
    difficulty: str
    door_number: int

    def is_guess_correct(self, guess: Union[str, int]) -> bool:
        """Compare a guessed octal code against the correct answer."""
        try:
            return validate_octal(guess) == self.answer
        except ChmodError:
            return False


@dataclass
class MinigameResult:
    """Outcome of the player attempting to solve a door."""

    door_number: int
    correct: bool
    xp_awarded: int
    message: str
    revealed_answer: Optional[str] = None


class ChmodMinigame:
    """Security door lockpicking game driven by chmod permission puzzles."""

    def __init__(
        self,
        difficulty: str = EASY,
        rng: Optional[random.Random] = None,
        xp_rewards: Optional[Dict[str, int]] = None,
    ) -> None:
        self.set_difficulty(difficulty)
        self._rng = rng if rng is not None else random.Random()
        self._xp_rewards: Dict[str, int] = dict(
            xp_rewards if xp_rewards is not None else XP_REWARDS
        )
        self.player: Optional[PlayerStats] = None
        self.active_puzzle: Optional[Puzzle] = None
        self._door_counter: int = 0
        self._solved_doors: set = set()
        self._total_xp_earned: int = 0
        self.last_result: Optional[MinigameResult] = None

    # -- configuration ------------------------------------------------------

    def set_difficulty(self, difficulty: str) -> None:
        """Switch difficulty level (easy / medium / hard)."""
        level = str(difficulty).strip().lower()
        if level not in DIFFICULTIES:
            raise ValueError(
                f"Unknown difficulty {difficulty!r}: expected one of {', '.join(DIFFICULTIES)}"
            )
        self.difficulty: str = level

    def set_player(self, player: Optional[PlayerStats]) -> None:
        """Bind a player so successful solves award XP."""
        self.player = player

    def reward_for(self, difficulty: Optional[str] = None) -> int:
        """Return the XP reward configured for a difficulty level."""
        return self._xp_rewards.get(difficulty or self.difficulty, 0)

    @property
    def doors_solved(self) -> int:
        """Number of unique doors solved so far."""
        return len(self._solved_doors)

    @property
    def xp_earned(self) -> int:
        """Total XP awarded by this minigame instance."""
        return self._total_xp_earned

    # -- puzzle generation --------------------------------------------------

    def _pick_code(self) -> str:
        """Choose a correct permission code for the current difficulty."""
        if self.difficulty == EASY:
            return self._rng.choice(EASY_CODES)
        if self.difficulty == MEDIUM:
            return self._rng.choice(MEDIUM_CODES)
        return "".join(str(self._rng.randint(0, 7)) for _ in range(3))

    def generate_puzzle(self) -> Puzzle:
        """Generate a fresh door puzzle and make it the active one."""
        self._door_counter += 1
        code = self._pick_code()
        puzzle = Puzzle(
            permission=octal_to_symbolic(code),
            answer=code,
            difficulty=self.difficulty,
            door_number=self._door_counter,
        )
        self.active_puzzle = puzzle
        self.last_result = None
        return puzzle

    # -- validation & XP ----------------------------------------------------

    def validate_answer(self, guess: Union[str, int]) -> MinigameResult:
        """Check a guess against the active door.

        Malformed input yields a failure result with zero XP (never a crash).
        Successful solves award XP exactly once per door via the bound
        :class:`PlayerStats` progression system.
        """
        puzzle = self.active_puzzle
        if puzzle is None:
            return MinigameResult(
                door_number=0,
                correct=False,
                xp_awarded=0,
                message="No active security door. Generate a puzzle first.",
            )

        try:
            code = validate_octal(guess)
        except ChmodError as err:
            return MinigameResult(
                door_number=puzzle.door_number,
                correct=False,
                xp_awarded=0,
                message=f"ACCESS DENIED: {err}",
            )

        correct = code == puzzle.answer
        if not correct:
            return MinigameResult(
                door_number=puzzle.door_number,
                correct=False,
                xp_awarded=0,
                message=f"ACCESS DENIED: {code!r} does not match the lock pattern.",
                revealed_answer=puzzle.answer,
            )

        already_solved = puzzle.door_number in self._solved_doors
        reward = 0
        if already_solved:
            message = (
                f"Door #{puzzle.door_number:02d} already breached — no additional XP."
            )
        else:
            self._solved_doors.add(puzzle.door_number)
            reward = self._xp_rewards.get(puzzle.difficulty, 0)
            self._total_xp_earned += reward
            if self.player is not None and reward > 0:
                self.player.gain_xp(reward)
            message = f"DOOR #{puzzle.door_number:02d} EXFILTRATED: correct code {code}."

        result = MinigameResult(
            door_number=puzzle.door_number,
            correct=True,
            xp_awarded=reward,
            message=message,
            revealed_answer=puzzle.answer,
        )
        self.last_result = result
        return result

    # -- display ------------------------------------------------------------

    def render_door(self, puzzle: Optional[Puzzle] = None) -> str:
        """Render the active (or a provided) security door as ASCII art."""
        if puzzle is None:
            puzzle = self.active_puzzle
        if puzzle is None:
            return "[ SECURITY DOOR ] Generate a puzzle to begin the breach."

        width = DOOR_WIDTH
        inner = width - 2  # space available between the two border characters

        def door_line(text: str, centered: bool = False) -> str:
            body = text.center(inner) if centered else text.ljust(inner)
            return "║" + body + "║"

        edge = "╔" + "═" * inner + "╗"
        divider = "╠" + "═" * inner + "╣"

        lines = [
            edge,
            door_line(f"SECURITY DOOR #{puzzle.door_number:02d}", centered=True),
            divider,
            door_line(f" Permission pattern: {puzzle.permission}"),
            door_line(" " * inner),
            door_line(" Enter security code: ___"),
            "╚" + "═" * inner + "╝",
        ]
        return "\n".join(lines)


__all__ = [
    "EASY",
    "MEDIUM",
    "HARD",
    "DIFFICULTIES",
    "XP_REWARDS",
    "EASY_CODES",
    "MEDIUM_CODES",
    "DOOR_WIDTH",
    "Puzzle",
    "MinigameResult",
    "ChmodMinigame",
]
