"""Quest Evaluator Logic for CyberShell RPG v2.0.

Author: Aswin (Game State, Progression & Evaluator)
"""

from typing import Any, List, Optional, Tuple

from cybershell.contracts import Objective, PlayerStats, Quest


class QuestEvaluator:
    """Evaluates quest objectives against VFS and player state."""

    def evaluate_objective(
        self,
        objective: Objective,
        vfs: Any,
        state: PlayerStats,
        last_command: Optional[str] = None,
    ) -> bool:
        """Check if an individual objective predicate is satisfied.
        
        Args:
            objective: The objective to evaluate.
            vfs: The virtual file system conforming to VFSProtocol.
            state: The player's current stats.
            last_command: Optional shell command string executed in this turn.
            
        Returns:
            True if the objective is met, False otherwise.
        """
        # If command tracking is active, ensure the executed command matches required command
        if last_command is None and hasattr(vfs, "last_command"):
            last_command = getattr(vfs, "last_command", None)

        if last_command is not None and objective.command:
            cmd_stripped = last_command.strip()
            if not cmd_stripped:
                return False
            tokens = cmd_stripped.split()
            first_token = tokens[0] if tokens else ""
            # Must match the objective's required command or be part of the command pipeline
            if first_token != objective.command and objective.command not in tokens:
                return False

        ptype = objective.predicate_type
        target = objective.predicate_target
        expected = objective.predicate_expected

        try:
            if ptype == "file_exists":
                exists = vfs.exists(target)
                if not exists and not target.startswith("/"):
                    try:
                        exists = vfs.exists(f"/home/operative/{target}")
                    except Exception:
                        pass
                return exists == bool(expected)

            elif ptype == "file_not_exists":
                exists = vfs.exists(target)
                if not exists and not target.startswith("/"):
                    try:
                        exists = vfs.exists(f"/home/operative/{target}")
                    except Exception:
                        pass
                return (not exists) == bool(expected)

            elif ptype == "file_contains":
                read_target = target
                if not vfs.exists(read_target):
                    if not target.startswith("/"):
                        read_target = f"/home/operative/{target}"
                    if not vfs.exists(read_target):
                        return False
                content = vfs.read_file(read_target)
                return str(expected) in content

            elif ptype == "permission_equals":
                node = vfs.get_node(target)
                if node is None and not target.startswith("/"):
                    node = vfs.get_node(f"/home/operative/{target}")
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
        self,
        quest: Quest,
        vfs: Any,
        state: PlayerStats,
        last_command: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Evaluate quest objectives sequentially and grant rewards for newly completed ones.
        
        Args:
            quest: The active quest.
            vfs: The virtual file system instance.
            state: The player's stats to update.
            last_command: Optional last command executed by player.
            
        Returns:
            A tuple of (is_fully_completed, newly_completed_ids).
        """
        if last_command is None and hasattr(vfs, "last_command"):
            last_command = getattr(vfs, "last_command", None)

        newly_completed_ids = []

        # Sequential evaluation: only evaluate the currently active (first uncompleted) objective
        current = quest.current_objective
        if current is not None:
            if self.evaluate_objective(current, vfs, state, last_command=last_command):
                current.completed = True
                state.gain_xp(current.xp_reward)
                newly_completed_ids.append(current.id)

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
