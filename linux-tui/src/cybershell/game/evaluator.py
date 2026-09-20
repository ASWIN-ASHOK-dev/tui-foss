"""Quest Evaluator Logic for CyberShell RPG v2.0.

Author: Aswin (Game State, Progression & Evaluator)
"""

from typing import Any, List, Tuple

from cybershell.contracts import Objective, PlayerStats, Quest


class QuestEvaluator:
    """Evaluates quest objectives against VFS and player state."""

    def evaluate_objective(self, objective: Objective, vfs: Any, state: PlayerStats) -> bool:
        """Check if an individual objective predicate is satisfied.
        
        Args:
            objective: The objective to evaluate.
            vfs: The virtual file system conforming to VFSProtocol.
            state: The player's current stats.
            
        Returns:
            True if the objective is met, False otherwise.
        """
        ptype = objective.predicate_type
        target = objective.predicate_target
        expected = objective.predicate_expected

        try:
            if ptype == "file_exists":
                return vfs.exists(target) == bool(expected)

            elif ptype == "file_not_exists":
                return (not vfs.exists(target)) == bool(expected)

            elif ptype == "file_contains":
                if not vfs.exists(target):
                    return False
                content = vfs.read_file(target)
                return str(expected) in content

            elif ptype == "permission_equals":
                node = vfs.get_node(target)
                if node is None:
                    return False
                # Assuming node has a 'permissions' attribute as per VFS design
                return str(getattr(node, "mode_octal", "")) == str(expected)

            elif ptype == "cwd_equals":
                return vfs.get_cwd_path() == str(target)

            else:
                # Unknown predicate type
                return False

        except Exception:
            # Catch any unexpected VFS errors (e.g. read_file on directory)
            return False

    def check_quest_progress(
        self, quest: Quest, vfs: Any, state: PlayerStats
    ) -> Tuple[bool, List[str]]:
        """Evaluate quest objectives and grant rewards for newly completed ones.
        
        Args:
            quest: The active quest.
            vfs: The virtual file system instance.
            state: The player's stats to update.
            
        Returns:
            A tuple of (is_fully_completed, newly_completed_ids).
        """
        newly_completed_ids = []

        for obj in quest.objectives:
            if not obj.completed:
                if self.evaluate_objective(obj, vfs, state):
                    obj.completed = True
                    state.gain_xp(obj.xp_reward)
                    newly_completed_ids.append(obj.id)

        # Check if the overall quest has just been completed
        if quest.is_completed and not quest.completed:
            quest.completed = True
            state.gain_xp(quest.reward_xp)
            if quest.reward_item:
                state.add_item(quest.reward_item)
            
            # Ensure the sector is marked as completed
            if quest.sector_id not in state.completed_sectors:
                state.completed_sectors.append(quest.sector_id)

        return (quest.completed, newly_completed_ids)
