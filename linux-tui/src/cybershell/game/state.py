"""Game State Management for CyberShell RPG v2.0.

Author: Aswin (Game State, Progression & Evaluator)
"""

import json
import os
from pathlib import Path
from typing import Optional

from cybershell.contracts import PlayerStats

SAVE_FILE_PATH = os.path.expanduser("~/.cybershell_save.json")

class SaveManager:
    """Manages local JSON persistence for the player state."""

    @staticmethod
    def save_state(player: PlayerStats, file_path: str = SAVE_FILE_PATH) -> bool:
        """Serialize player state and write to a JSON file.
        
        Args:
            player: The PlayerStats object to save.
            file_path: The file path to save to (defaults to ~/.cybershell_save.json).
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            data = player.to_dict()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:
            return False

    @staticmethod
    def load_state(file_path: str = SAVE_FILE_PATH) -> PlayerStats:
        """Read JSON save file and deserialize to PlayerStats.
        
        If the file does not exist or is invalid, a fresh level 1 player is returned.
        
        Args:
            file_path: The file path to load from.
            
        Returns:
            A PlayerStats object.
        """
        path = Path(file_path)
        if not path.is_file():
            return PlayerStats()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PlayerStats.from_dict(data)
        except Exception:
            # Fallback to a fresh player if the save is corrupted
            return PlayerStats()
