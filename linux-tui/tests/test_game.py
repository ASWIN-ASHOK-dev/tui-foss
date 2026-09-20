"""Tests for Game State and Quest Evaluator.

Author: Aswin (Game State, Progression & Evaluator)
"""

import os
import sys
import unittest

# Ensure 'src' and project root are on sys.path for direct test execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cybershell.contracts import Item  # noqa: E402
from cybershell.game.state import SaveManager  # noqa: E402
from cybershell.game.evaluator import QuestEvaluator  # noqa: E402
from tests.conftest import MockGameState  # noqa: E402

class MockNode:
    def __init__(self, mode_octal="755"):
        self.mode_octal = mode_octal

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

class TestGameStateAndEvaluator(unittest.TestCase):

    def setUp(self):
        self.temp_save_file = ".cybershell_test_save.json"
        if os.path.exists(self.temp_save_file):
            os.remove(self.temp_save_file)
        self.evaluator = QuestEvaluator()
        self.mock_vfs = MockVFS()
        self.mock_player = MockGameState.create_player()
        self.sample_objective = MockGameState.create_objective()
        
        # Test full quest progression and rewards.
        # mock_quest has 2 objectives (cwd_equals /home/operative, file_exists /tmp/flag)
        self.mock_quest = MockGameState.create_quest(0)
        
        # Override objectives to match exactly what test_check_quest_progress expects
        self.mock_quest.objectives[0].predicate_type = "cwd_equals"
        self.mock_quest.objectives[0].predicate_target = "/home/operative"
        self.mock_quest.objectives[0].predicate_expected = True
        self.mock_quest.objectives[0].xp_reward = 50

        self.mock_quest.objectives[1].predicate_type = "file_exists"
        self.mock_quest.objectives[1].predicate_target = "/tmp/flag"
        self.mock_quest.objectives[1].predicate_expected = True
        self.mock_quest.objectives[1].xp_reward = 50
        
        self.mock_quest.reward_xp = 100
        self.mock_quest.reward_item = Item(id="chip", name="Chip", description="Loot", category="chip", rarity="common", properties={"decrypt_power": 10})

    def tearDown(self):
        if os.path.exists(self.temp_save_file):
            os.remove(self.temp_save_file)

    def test_save_and_load_state(self):
        """Test that SaveManager can serialize and deserialize PlayerStats correctly."""
        # Modify player to test non-default values
        self.mock_player.gain_xp(150) # Level 2 requires 100 xp
        self.mock_player.hp = 85
        self.mock_player.add_item(Item(id="test_item", name="Test Item", description="A test item.", category="misc", rarity="common", properties={}))
        
        self.assertEqual(self.mock_player.level, 2)
        self.assertEqual(self.mock_player.rank, "Junior Operative")

        # Save to temp file
        self.assertTrue(SaveManager.save_state(self.mock_player, file_path=self.temp_save_file))
        self.assertTrue(os.path.exists(self.temp_save_file))

        # Load from temp file
        loaded_player = SaveManager.load_state(file_path=self.temp_save_file)

        self.assertEqual(loaded_player.character_name, self.mock_player.character_name)
        self.assertEqual(loaded_player.hp, 85)
        self.assertEqual(loaded_player.level, 2)
        self.assertEqual(loaded_player.xp, 150)
        self.assertEqual(loaded_player.rank, "Junior Operative")
        self.assertEqual(len(loaded_player.inventory), 1)
        self.assertEqual(loaded_player.inventory[0].id, "test_item")

    def test_load_state_no_file(self):
        """Test that load_state returns a fresh player if the save file doesn't exist."""
        self.assertFalse(os.path.exists(self.temp_save_file))
        player = SaveManager.load_state(file_path=self.temp_save_file)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.hp, 100)
        self.assertEqual(player.xp, 0)

    def test_evaluate_cwd_equals(self):
        """Test cwd_equals predicate."""
        self.sample_objective.predicate_type = "cwd_equals"
        self.sample_objective.predicate_target = "/home/operative"
        self.sample_objective.predicate_expected = True
        
        self.mock_vfs.cwd = "/home/operative"
        self.assertTrue(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

        self.mock_vfs.cwd = "/root"
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

    def test_evaluate_file_exists(self):
        """Test file_exists and file_not_exists predicates."""
        self.sample_objective.predicate_target = "/etc/passwd"
        
        self.sample_objective.predicate_type = "file_exists"
        self.sample_objective.predicate_expected = True
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))
        
        self.mock_vfs.files["/etc/passwd"] = "root:x:0:0:"
        self.assertTrue(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

        self.sample_objective.predicate_type = "file_not_exists"
        self.sample_objective.predicate_expected = True
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

    def test_evaluate_file_contains(self):
        """Test file_contains predicate."""
        self.sample_objective.predicate_type = "file_contains"
        self.sample_objective.predicate_target = "/home/operative/log.txt"
        self.sample_objective.predicate_expected = "ERROR"

        # File doesn't exist yet
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))
        
        # File exists, but doesn't contain ERROR
        self.mock_vfs.files["/home/operative/log.txt"] = "INFO: All systems green."
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

        # File contains ERROR
        self.mock_vfs.files["/home/operative/log.txt"] = "INFO: green\nERROR: CPU overloaded!"
        self.assertTrue(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

    def test_evaluate_permission_equals(self):
        """Test permission_equals predicate."""
        self.sample_objective.predicate_type = "permission_equals"
        self.sample_objective.predicate_target = "/home/operative/script.sh"
        self.sample_objective.predicate_expected = "755"

        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

        self.mock_vfs.nodes["/home/operative/script.sh"] = MockNode("644")
        self.assertFalse(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

        self.mock_vfs.nodes["/home/operative/script.sh"].mode_octal = "755"
        self.assertTrue(self.evaluator.evaluate_objective(self.sample_objective, self.mock_vfs, self.mock_player))

    def test_check_quest_progress(self):
        """Test full quest progression and rewards."""
        self.mock_vfs.cwd = "/home/operative"
        # First objective will pass, second will fail (file doesn't exist)
        
        is_completed, newly_completed = self.evaluator.check_quest_progress(self.mock_quest, self.mock_vfs, self.mock_player)
        
        self.assertFalse(is_completed)
        self.assertEqual(len(newly_completed), 1)
        self.assertEqual(newly_completed[0], self.mock_quest.objectives[0].id)
        self.assertTrue(self.mock_quest.objectives[0].completed)
        self.assertEqual(self.mock_player.xp, 50)
        self.assertFalse(self.mock_quest.completed)

        # Now make the second objective pass
        self.mock_vfs.files["/tmp/flag"] = ""
        is_completed, newly_completed = self.evaluator.check_quest_progress(self.mock_quest, self.mock_vfs, self.mock_player)
        
        self.assertTrue(is_completed)
        self.assertTrue(self.mock_quest.completed)
        self.assertEqual(len(newly_completed), 1)
        self.assertEqual(newly_completed[0], self.mock_quest.objectives[1].id)
        
        self.assertEqual(self.mock_player.xp, 200)
        self.assertEqual(self.mock_player.level, 3)
        self.assertEqual(len(self.mock_player.inventory), 1)
        self.assertEqual(self.mock_player.inventory[0].id, "chip")
        self.assertIn(self.mock_quest.sector_id, self.mock_player.completed_sectors)

if __name__ == "__main__":
    unittest.main()
