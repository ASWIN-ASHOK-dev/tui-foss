"""Tests for Game State and Quest Evaluator.

Author: Aswin (Game State, Progression & Evaluator)
"""

import os
import json
import pytest

from cybershell.contracts import Objective, Quest, PlayerStats, Item
from cybershell.game.state import SaveManager, SAVE_FILE_PATH
from cybershell.game.evaluator import QuestEvaluator

class MockNode:
    def __init__(self, permissions="755"):
        self.permissions = permissions

class MockVFS:
    """A mock implementation of VFSProtocol for testing evaluator."""
    def __init__(self):
        self.cwd = "/home/operative"
        self.files = {}
        self.nodes = {}

    def get_cwd_path(self) -> str:
        return self.cwd

    def exists(self, path: str) -> bool:
        return path in self.files or path in self.nodes

    def read_file(self, path: str) -> str:
        if path in self.files:
            return self.files[path]
        raise Exception("File not found")

    def get_node(self, path: str):
        return self.nodes.get(path)

@pytest.fixture
def temp_save_file(tmp_path):
    """Fixture to provide a temporary file path for SaveManager."""
    save_path = tmp_path / ".cybershell_save.json"
    return str(save_path)

@pytest.fixture
def evaluator():
    return QuestEvaluator()

@pytest.fixture
def mock_vfs():
    return MockVFS()

def test_save_and_load_state(temp_save_file, mock_player):
    """Test that SaveManager can serialize and deserialize PlayerStats correctly."""
    # Modify player to test non-default values
    mock_player.gain_xp(150) # Level 2 requires 100 xp
    mock_player.hp = 85
    mock_player.add_item(Item(id="test_item", name="Test Item", description="A test item."))
    
    assert mock_player.level == 2
    assert mock_player.rank == "Junior Operative"

    # Save to temp file
    assert SaveManager.save_state(mock_player, file_path=temp_save_file)
    assert os.path.exists(temp_save_file)

    # Load from temp file
    loaded_player = SaveManager.load_state(file_path=temp_save_file)

    assert loaded_player.character_name == mock_player.character_name
    assert loaded_player.hp == 85
    assert loaded_player.level == 2
    assert loaded_player.xp == 150
    assert loaded_player.rank == "Junior Operative"
    assert len(loaded_player.inventory) == 1
    assert loaded_player.inventory[0].id == "test_item"

def test_load_state_no_file(temp_save_file):
    """Test that load_state returns a fresh player if the save file doesn't exist."""
    assert not os.path.exists(temp_save_file)
    player = SaveManager.load_state(file_path=temp_save_file)
    assert player.level == 1
    assert player.hp == 100
    assert player.xp == 0

def test_evaluate_cwd_equals(evaluator, mock_vfs, mock_player, sample_objective):
    """Test cwd_equals predicate."""
    sample_objective.predicate_type = "cwd_equals"
    sample_objective.predicate_target = ""
    sample_objective.predicate_expected = "/home/operative"
    
    mock_vfs.cwd = "/home/operative"
    assert evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

    mock_vfs.cwd = "/root"
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

def test_evaluate_file_exists(evaluator, mock_vfs, mock_player, sample_objective):
    """Test file_exists and file_not_exists predicates."""
    sample_objective.predicate_target = "/etc/passwd"
    
    sample_objective.predicate_type = "file_exists"
    sample_objective.predicate_expected = True
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)
    
    mock_vfs.files["/etc/passwd"] = "root:x:0:0:"
    assert evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

    sample_objective.predicate_type = "file_not_exists"
    sample_objective.predicate_expected = True
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

def test_evaluate_file_contains(evaluator, mock_vfs, mock_player, sample_objective):
    """Test file_contains predicate."""
    sample_objective.predicate_type = "file_contains"
    sample_objective.predicate_target = "/home/operative/log.txt"
    sample_objective.predicate_expected = "ERROR"

    # File doesn't exist yet
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)
    
    # File exists, but doesn't contain ERROR
    mock_vfs.files["/home/operative/log.txt"] = "INFO: All systems green."
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

    # File contains ERROR
    mock_vfs.files["/home/operative/log.txt"] = "INFO: green\nERROR: CPU overloaded!"
    assert evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

def test_evaluate_permission_equals(evaluator, mock_vfs, mock_player, sample_objective):
    """Test permission_equals predicate."""
    sample_objective.predicate_type = "permission_equals"
    sample_objective.predicate_target = "/home/operative/script.sh"
    sample_objective.predicate_expected = "755"

    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

    mock_vfs.nodes["/home/operative/script.sh"] = MockNode("644")
    assert not evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

    mock_vfs.nodes["/home/operative/script.sh"].permissions = "755"
    assert evaluator.evaluate_objective(sample_objective, mock_vfs, mock_player)

def test_check_quest_progress(evaluator, mock_vfs, mock_player, mock_quest):
    """Test full quest progression and rewards."""
    # mock_quest has 2 objectives (cwd_equals /home/operative, cwd_equals /home/operative)
    # Let's adjust them for a proper test
    mock_quest.objectives[0].predicate_type = "cwd_equals"
    mock_quest.objectives[0].predicate_expected = "/home/operative"
    mock_quest.objectives[0].xp_reward = 50

    mock_quest.objectives[1].predicate_type = "file_exists"
    mock_quest.objectives[1].predicate_target = "/tmp/flag"
    mock_quest.objectives[1].predicate_expected = True
    mock_quest.objectives[1].xp_reward = 50
    
    mock_quest.reward_xp = 100
    mock_quest.reward_item = Item(id="chip", name="Chip", description="Loot")

    mock_vfs.cwd = "/home/operative"
    # First objective will pass, second will fail (file doesn't exist)
    
    is_completed, newly_completed = evaluator.check_quest_progress(mock_quest, mock_vfs, mock_player)
    
    assert not is_completed
    assert len(newly_completed) == 1
    assert newly_completed[0] == mock_quest.objectives[0].id
    assert mock_quest.objectives[0].completed
    assert mock_player.xp == 50
    assert not mock_quest.completed

    # Now make the second objective pass
    mock_vfs.files["/tmp/flag"] = ""
    is_completed, newly_completed = evaluator.check_quest_progress(mock_quest, mock_vfs, mock_player)
    
    assert is_completed
    assert mock_quest.completed
    assert len(newly_completed) == 1
    assert newly_completed[0] == mock_quest.objectives[1].id
    
    # 50 + 50 (from objectives) + 100 (from quest completion) = 200 XP
    # 200 XP is enough for Level 3 (lvl 1 -> lvl 2 at 100, lvl 2 -> lvl 3 at 200)
    # Wait, the formula is while xp >= level * 100.
    # Level 1: needs 100 to level up. Level 2 needs 200 to level up.
    # Total xp = 200.
    # Start level 1, xp = 200.
    # 200 >= 1 * 100 -> level 2.
    # 200 >= 2 * 100 -> level 3.
    # So player should be Level 3.
    
    assert mock_player.xp == 200
    assert mock_player.level == 3
    assert len(mock_player.inventory) == 1
    assert mock_player.inventory[0].id == "chip"
    assert mock_quest.sector_id in mock_player.completed_sectors
