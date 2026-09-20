"""Full End-to-End Integration and Smoke Test Suite for CyberShell RPG v2.0.

Author: Amy (Project Lead & Master Integrator)
Role: Validates contracts, engine protocols, player progression, VFS integration,
      UI lifecycle, and end-to-end quest completion simulation.
Compatible with both standard library unittest and pytest.
"""

from __future__ import annotations

import json
import os
import sys
import unittest

# Ensure 'src' and project root are on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cybershell.contracts import (  # noqa: E402
    DEFAULT_BACKLASH_DAMAGE,
    DEFAULT_MAX_HP,
    CodexEntry,
    CommandResult,
    EngineProtocol,
    Item,
    Objective,
    PlayerStats,
    Quest,
    SectorNode,
    calculate_rank,
)
from cybershell.engine.vfs import VirtualFileSystem  # noqa: E402
from cybershell.ui.rpg_app import RPGApp  # noqa: E402
from tests.conftest import MockEngine, MockGameState  # noqa: E402


class TestCyberShellIntegration(unittest.TestCase):
    """Amy's master integration test suite."""

    def setUp(self) -> None:
        """Initialize fresh test state before each test case."""
        self.player = MockGameState.create_player(name="Cipher", hp=100)
        self.engine = MockEngine()
        self.vfs = VirtualFileSystem(default_user="operative")

    # -------------------------------------------------------------------------
    # 1. Contracts & Serialization Validation
    # -------------------------------------------------------------------------

    def test_contracts_serialization_roundtrip(self) -> None:
        """Verify that all frozen DTOs serialize and deserialize without loss."""
        # 1. Item
        item = Item(
            id="item_exploit_01",
            name="Buffer Overflow Exploit",
            description="Bypasses Sector 1 gatekeeper daemon.",
            category="exploit",
            rarity="epic",
            properties={"damage": 50, "single_use": True},
        )
        item_dict = item.to_dict()
        reconstructed_item = Item.from_dict(item_dict)
        self.assertEqual(item, reconstructed_item)

        # 2. Objective
        objective = Objective(
            id="obj_test_1",
            description="Run ls -la in root",
            hint="Try typing ls -la /",
            predicate_type="cwd_equals",
            predicate_target="/",
            completed=False,
            xp_reward=75,
        )
        obj_dict = objective.to_dict()
        reconstructed_obj = Objective.from_dict(obj_dict)
        self.assertEqual(objective, reconstructed_obj)

        # 3. Quest
        quest = Quest(
            id="quest_sector_1",
            sector_id=1,
            sector_name="The File Vault",
            npc_name="Cipher",
            lore="Infiltrate the secure archival cluster.",
            dialogue=["Break the encryption on the primary ledger."],
            objectives=[objective],
            reward_item=item,
            reward_xp=150,
            completed=False,
        )
        quest_dict = quest.to_dict()
        reconstructed_quest = Quest.from_dict(quest_dict)
        self.assertEqual(quest.id, reconstructed_quest.id)
        self.assertEqual(quest.sector_name, reconstructed_quest.sector_name)
        self.assertEqual(len(quest.objectives), len(reconstructed_quest.objectives))
        self.assertEqual(quest.reward_item, reconstructed_quest.reward_item)

        # 4. PlayerStats
        self.player.add_item(item)
        player_dict = self.player.to_dict()
        # Verify JSON serializability
        serialized_json = json.dumps(player_dict)
        deserialized_data = json.loads(serialized_json)
        reconstructed_player = PlayerStats.from_dict(deserialized_data)
        self.assertEqual(self.player.character_name, reconstructed_player.character_name)
        self.assertEqual(self.player.hp, reconstructed_player.hp)
        self.assertEqual(self.player.level, reconstructed_player.level)
        self.assertEqual(len(self.player.inventory), len(reconstructed_player.inventory))

        # 5. CodexEntry & SectorNode
        codex = CodexEntry(
            command="chmod",
            syntax="chmod [mode] [file]",
            description="Alter file security permissions.",
            flags={"-R": "Recursive"},
            combos=["chmod 755 run.sh && ./run.sh"],
        )
        self.assertEqual(codex, CodexEntry.from_dict(codex.to_dict()))

        sector_node = SectorNode(
            sector_id=2,
            name="Data Interception Grid",
            status="ACTIVE",
            description="Intercept corporate telemetries.",
        )
        self.assertEqual(sector_node, SectorNode.from_dict(sector_node.to_dict()))

    # -------------------------------------------------------------------------
    # 2. Player Progression & Combat Mechanics
    # -------------------------------------------------------------------------

    def test_player_damage_healing_and_leveling(self) -> None:
        """Verify health clamping, healing, XP gain, level up, and rank titles."""
        p = PlayerStats(character_name="ZeroCool", hp=100, max_hp=100, xp=0, level=1)
        self.assertEqual(p.rank, "Script Kiddie")

        # Take damage
        taken = p.take_damage(30)
        self.assertEqual(taken, 30)
        self.assertEqual(p.hp, 70)

        # Take overkill damage - should clamp at 0
        overkill = p.take_damage(150)
        self.assertEqual(overkill, 70)
        self.assertEqual(p.hp, 0)

        # Healing
        restored = p.heal(50)
        self.assertEqual(restored, 50)
        self.assertEqual(p.hp, 50)

        # Over-heal - should cap at max_hp
        p.heal(200)
        self.assertEqual(p.hp, 100)

        # Gain XP and level up
        leveled = p.gain_xp(50)
        self.assertFalse(leveled)
        self.assertEqual(p.level, 1)

        # Level up threshold: 100 XP triggers level 2
        leveled = p.gain_xp(60)
        self.assertTrue(leveled)
        self.assertEqual(p.level, 2)
        self.assertEqual(p.rank, "Junior Operative")
        self.assertEqual(p.max_hp, 110)
        self.assertEqual(p.hp, 110)

        # Test rank scaling helper
        self.assertEqual(calculate_rank(1), "Script Kiddie")
        self.assertEqual(calculate_rank(3), "Cyber Mercenary")
        self.assertEqual(calculate_rank(4), "Netrunner")
        self.assertEqual(calculate_rank(6), "Root Architect")

    def test_inventory_duplicate_protection(self) -> None:
        """Verify that duplicate items cannot be accidentally stacked in inventory."""
        chip = Item(id="chip_01", name="ROM Chip", description="Read only memory")
        self.assertTrue(self.player.add_item(chip))
        self.assertTrue(self.player.has_item("chip_01"))

        # Second addition of same ID must return False
        self.assertFalse(self.player.add_item(chip))
        self.assertEqual(len(self.player.inventory), 1)

    # -------------------------------------------------------------------------
    # 3. Engine Protocol & Electrical Backlash
    # -------------------------------------------------------------------------

    def test_engine_protocol_and_backlash(self) -> None:
        """Verify EngineProtocol conformance and syntax backlash damage (-15 HP)."""
        self.assertTrue(isinstance(self.engine, EngineProtocol))

        # Successful command
        res_pwd = self.engine.execute("pwd")
        self.assertTrue(res_pwd.is_success)
        self.assertEqual(res_pwd.stdout.strip(), "/home/operative")
        self.assertEqual(res_pwd.backlash_damage, 0)

        # Simulated cd
        self.engine.execute("cd /tmp")
        self.assertEqual(self.engine.get_cwd(), "/tmp")

        # Invalid command syntax causing electrical backlash
        bad_res = self.engine.execute("corrupted_daemon_call --inject")
        self.assertFalse(bad_res.is_success)
        self.assertEqual(bad_res.exit_code, 127)
        self.assertEqual(bad_res.backlash_damage, DEFAULT_BACKLASH_DAMAGE)
        self.assertTrue(bad_res.has_backlash)

    # -------------------------------------------------------------------------
    # 4. Virtual Filesystem (VFS) Integration
    # -------------------------------------------------------------------------

    def test_vfs_interaction_and_path_resolution(self) -> None:
        """Verify real VFS methods integrate with game requirements."""
        self.assertEqual(self.vfs.get_cwd_path(), "/home/operative")

        # Create a mission target file
        node = self.vfs.touch("/home/operative/flag.txt")
        self.assertIsNotNone(node)
        self.assertTrue(self.vfs.exists("/home/operative/flag.txt"))

        # Write data to file
        self.vfs.write_file("/home/operative/flag.txt", "CYBER_KEY{ROOT_ACCESS_GRANTED}")
        content = self.vfs.read_file("/home/operative/flag.txt")
        self.assertEqual(content, "CYBER_KEY{ROOT_ACCESS_GRANTED}")

        # Test chmod permission changes
        self.vfs.chmod("/home/operative/flag.txt", 0o600)
        flag_node = self.vfs.get_node("/home/operative/flag.txt")
        self.assertIsNotNone(flag_node)
        self.assertEqual(flag_node.permissions, 0o600)

    # -------------------------------------------------------------------------
    # 5. UI App Lifecycle Integration
    # -------------------------------------------------------------------------

    def test_ui_app_lifecycle(self) -> None:
        """Verify RPGApp initializes, changes screens, and renders cleanly."""
        app = RPGApp(
            character_name=self.player.character_name,
            hp=self.player.hp,
            max_hp=self.player.max_hp,
            xp=self.player.xp,
        )

        # Verify title screen rendering
        title_render = app.render_title(80)
        self.assertIn("CYBERSHELL RPG", title_render)

        # Switch to Mission Lab
        app.set_screen(RPGApp.SCREEN_LAB)
        self.assertEqual(app.get_screen_name(), "MISSION LAB")
        lab_render = app.render_lab(80)
        self.assertIn("MISSION INTEL", lab_render)
        self.assertIn("TERMINAL", lab_render)

        # Switch to Codex
        app.set_screen(RPGApp.SCREEN_CODEX)
        codex_render = app.render()
        self.assertIn("CODEX", codex_render)

        # Switch to Map
        app.set_screen(RPGApp.SCREEN_MAP)
        map_render = app.render()
        self.assertIn("MAP", map_render)

    # -------------------------------------------------------------------------
    # 6. End-to-End Quest Progression Simulation
    # -------------------------------------------------------------------------

    def test_full_quest_lifecycle_simulation(self) -> None:
        """Simulate an operative completing Sector 0 objectives and acquiring loot."""
        quest = MockGameState.create_quest(sector_id=0)
        self.assertEqual(len(quest.objectives), 2)
        self.assertFalse(quest.is_completed)

        # Step 1: Player mistakenly executes invalid command -> takes backlash damage
        res1 = self.engine.execute("cat /missing_core")
        # In mock engine this is valid command, let's run an unknown command:
        res_bad = self.engine.execute("pwdd")
        self.assertEqual(res_bad.exit_code, 127)
        self.assertEqual(res_bad.backlash_damage, 15)
        self.player.take_damage(res_bad.backlash_damage)
        self.assertEqual(self.player.hp, 85)

        # Step 2: Operative checks location with 'pwd' -> completes Objective 1
        res_pwd = self.engine.execute("pwd")
        self.assertTrue(res_pwd.is_success)
        obj1 = quest.objectives[0]
        obj1.completed = True
        self.player.gain_xp(obj1.xp_reward)
        self.assertEqual(self.player.xp, 50)

        # Step 3: Operative checks directory with 'ls' -> completes Objective 2
        res_ls = self.engine.execute("ls -la")
        self.assertTrue(res_ls.is_success)
        obj2 = quest.objectives[1]
        obj2.completed = True
        leveled = self.player.gain_xp(obj2.xp_reward)

        # Player hits 100 XP -> Leveled up to Level 2!
        self.assertTrue(leveled)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.rank, "Junior Operative")
        self.assertEqual(self.player.hp, 110)

        # Verify Quest completion & Loot drop
        self.assertTrue(quest.is_completed)
        quest.completed = True
        if quest.reward_item:
            added = self.player.add_item(quest.reward_item)
            self.assertTrue(added)
            self.assertTrue(self.player.has_item("item_quarantine_chip"))

        # Sector 0 complete, record progress
        self.player.completed_sectors.append(0)
        self.player.current_sector = 1

        # Final state verification
        self.assertIn(0, self.player.completed_sectors)
        self.assertEqual(self.player.current_sector, 1)
        self.assertEqual(len(self.player.inventory), 1)

    def test_full_six_sector_campaign_progression(self) -> None:
        """Verify seamless quest completion and sector advancement from Sector 0 to Sector 5."""
        from cybershell.engine.interpreter import Interpreter
        from cybershell.game.evaluator import QuestEvaluator
        from cybershell.game.quests import get_sector_quests

        vfs = VirtualFileSystem(default_user="operative")
        interpreter = Interpreter(vfs=vfs)
        evaluator = QuestEvaluator()
        player = PlayerStats(character_name="Byte", hp=100, max_hp=100, xp=0, current_sector=0)
        all_quests = get_sector_quests()

        campaign_actions = [
            (0, "pwd"),
            (1, "touch intel.txt"),
            (2, "mkdir backup"),
            (3, "chmod 755 run.sh"),
            (4, "cat firewall.log"),
            (5, "cd /root"),
        ]

        for sector_id, command in campaign_actions:
            self.assertEqual(player.current_sector, sector_id)
            quest = all_quests[sector_id]
            cmd_res = interpreter.execute(command)
            self.assertEqual(cmd_res.exit_code, 0)
            is_completed, newly = evaluator.check_quest_progress(quest, vfs, player)
            self.assertTrue(is_completed)
            self.assertGreater(len(newly), 0)
            self.assertIn(sector_id, player.completed_sectors)

            # Advance sector if available
            next_sector = player.current_sector + 1
            if next_sector in all_quests:
                player.current_sector = next_sector

        # Verify all 6 sectors are completed and legendary loot acquired
        self.assertEqual(len(player.completed_sectors), 6)
        self.assertTrue(player.has_item("item_root_access"))
        self.assertGreater(player.level, 20)


if __name__ == "__main__":
    unittest.main()
