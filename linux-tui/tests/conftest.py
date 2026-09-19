"""Shared Test Fixtures and Mocks for CyberShell RPG v2.0.

Author: Amy (Project Lead & Master Integrator)
Role: Day 3 Deliverable - Provides shared mock fixtures (MockEngine, MockGameState)
      so UI (Poornendhu/Gautham) and Quest/Game teams (Neha/Aswin) can write
      and execute automated tests without being blocked by the execution engine.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

# Ensure 'src' is on sys.path for test discovery across all runners
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cybershell.contracts import (  # noqa: E402
    DEFAULT_BACKLASH_DAMAGE,
    DEFAULT_MAX_HP,
    CommandResult,
    EngineProtocol,
    Item,
    Objective,
    PlayerStats,
    Quest,
)

# Try importing pytest (optional: conftest works with or without pytest runner)
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    pytest = None  # type: ignore


# =============================================================================
# Mock Execution Engine
# =============================================================================

class MockEngine:
    """Mock implementation conforming to EngineProtocol."""

    def __init__(self, initial_cwd: str = "/home/operative") -> None:
        self.cwd: str = initial_cwd
        self.history: List[str] = []
        self.custom_responses: Dict[str, CommandResult] = {}
        self.simulate_backlash: bool = True
        self.sector_resets: int = 0

    def register_response(self, command: str, result: CommandResult) -> None:
        """Register a canned CommandResult for a specific command."""
        self.custom_responses[command.strip()] = result

    def execute(self, command_line: str) -> CommandResult:
        """Simulate shell command execution with backlash simulation."""
        cmd = command_line.strip()
        self.history.append(cmd)

        # Check explicit registered mocks
        if cmd in self.custom_responses:
            return self.custom_responses[cmd]

        if not cmd:
            return CommandResult(stdout="", stderr="", exit_code=0)

        parts = cmd.split()
        binary = parts[0]

        # Basic built-in simulations
        if binary == "pwd":
            return CommandResult(stdout=f"{self.cwd}\n", exit_code=0)

        if binary == "cd":
            target = parts[1] if len(parts) > 1 else "/home/operative"
            if target == "..":
                self.cwd = "/home" if self.cwd == "/home/operative" else "/"
            elif target.startswith("/"):
                self.cwd = target
            else:
                self.cwd = f"{self.cwd.rstrip('/')}/{target}"
            return CommandResult(stdout="", exit_code=0)

        if binary == "echo":
            content = " ".join(parts[1:]).strip("'\"")
            return CommandResult(stdout=f"{content}\n", exit_code=0)

        if binary in ("ls", "touch", "mkdir", "cat", "chmod"):
            return CommandResult(stdout=f"[mock {binary} executed successfully]\n", exit_code=0)

        # Syntax error / unknown command simulation triggering electrical backlash
        damage = DEFAULT_BACKLASH_DAMAGE if self.simulate_backlash else 0
        return CommandResult(
            stdout="",
            stderr=f"cybershell: command not found: {binary}\n",
            exit_code=127,
            backlash_damage=damage,
        )

    def get_cwd(self) -> str:
        """Return simulated working directory."""
        return self.cwd

    def reset_sector(self, sector_dict: Optional[Dict[str, Any]] = None) -> None:
        """Reset mock filesystem state."""
        self.cwd = "/home/operative"
        self.sector_resets += 1


# Verify MockEngine conforms to EngineProtocol at class level
assert isinstance(MockEngine(), EngineProtocol)


# =============================================================================
# Mock Game State Factories
# =============================================================================

class MockGameState:
    """Helper factory generating mock objects for tests."""

    @staticmethod
    def create_player(
        name: str = "Byte",
        hp: int = DEFAULT_MAX_HP,
        xp: int = 0,
        level: int = 1,
    ) -> PlayerStats:
        """Create a configured PlayerStats instance."""
        return PlayerStats(
            character_name=name,
            hp=hp,
            max_hp=DEFAULT_MAX_HP,
            xp=xp,
            level=level,
        )

    @staticmethod
    def create_item(
        item_id: str = "item_quarantine_chip",
        name: str = "Quarantine Keychip",
        desc: str = "Decrypts Sector 0 security gates.",
        category: str = "hardware",
        rarity: str = "rare",
    ) -> Item:
        """Create a configured Item instance."""
        return Item(
            id=item_id,
            name=name,
            description=desc,
            category=category,
            rarity=rarity,
            properties={"decrypt_power": 10},
        )

    @staticmethod
    def create_objective(
        obj_id: str = "obj_0_1",
        description: str = "Locate mainframe coordinates with 'pwd'.",
        predicate_type: str = "cwd_equals",
        predicate_target: str = "/home/operative",
        xp_reward: int = 50,
    ) -> Objective:
        """Create a configured Objective instance."""
        return Objective(
            id=obj_id,
            description=description,
            hint="Try typing 'pwd'.",
            predicate_type=predicate_type,
            predicate_target=predicate_target,
            predicate_expected=True,
            completed=False,
            xp_reward=xp_reward,
        )

    @staticmethod
    def create_quest(sector_id: int = 0) -> Quest:
        """Create a sample Quest instance for Sector 0."""
        obj1 = MockGameState.create_objective("obj_0_1", "Run pwd to get coordinates")
        obj2 = MockGameState.create_objective("obj_0_2", "Inspect directory with ls -la")
        chip = MockGameState.create_item()

        return Quest(
            id=f"quest_sector_{sector_id}",
            sector_id=sector_id,
            sector_name="Quarantine Zone",
            npc_name="Byte",
            lore="You wake up in an isolated sandbox with memory corruption.",
            dialogue=[
                "Operative! Mainframe lockdown detected.",
                "Verify your location coordinates immediately.",
            ],
            objectives=[obj1, obj2],
            reward_item=chip,
            reward_xp=100,
            completed=False,
        )


# =============================================================================
# Pytest Fixtures (if pytest is available)
# =============================================================================

if HAS_PYTEST:
    @pytest.fixture
    def mock_engine() -> MockEngine:
        """Provide a fresh MockEngine instance."""
        return MockEngine()

    @pytest.fixture
    def mock_player() -> PlayerStats:
        """Provide a standard test operative."""
        return MockGameState.create_player()

    @pytest.fixture
    def mock_quest() -> Quest:
        """Provide a test Quest with two objectives."""
        return MockGameState.create_quest(0)

    @pytest.fixture
    def mock_item() -> Item:
        """Provide a test Item."""
        return MockGameState.create_item()

    @pytest.fixture
    def sample_objective() -> Objective:
        """Provide a single test Objective."""
        return MockGameState.create_objective()

    @pytest.fixture
    def real_vfs():
        """Provide an initialized VirtualFileSystem instance."""
        from cybershell.engine.vfs import VirtualFileSystem
        return VirtualFileSystem()
