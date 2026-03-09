from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player
    from engine.dungeon import Dungeon


__version__ = "34.0"
__creation__ = "08-03-2026"


"""
Save structure to simplify the saves' names and make it easier to load them later.
Each save will be stored as a JSON file with the following structure:
{
  "meta": {
    "player_name": "Dragondefer",
    "level": 12,
    "difficulty": "Realistic",
    "location": "Dungeon Floor 5",
    "playtime": 14235,
    "last_save": "2026-03-08 19:42",
    "save_type": "auto"
  },

  "player_data": {...},
  "dungeon_state": {...},
  "inventory": {...}
}

---

Saves' display format in the load menu to make it more user-friendly:
Saved Games

    Nom        |  Niveau | Floor   | Difficulté | Temps | Type
1. Dragondefer |  Lv12   | Floor 5 | Realistic  | 3h57  | AUTO
2. Dragondefer |  Lv9    | Floor 3 | Realistic  | 2h10  | AUTO
3. Dragondefer |  Lv5    | Floor 2 | Normal     | 1h12  | MANUAL

---

Autosave system that keeps the last 3 autosaves and rotates them:

autosave_3 deleted
autosave_2 → autosave_3
autosave_1 → autosave_2
new → autosave_1
"""


import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from engine.game_utility import strip_ansi


class SaveManager:

    def __init__(self, save_dir: str = "./saves"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def list_saves(self) -> List[Dict[str, Any]]:
        """Returns a list of available saves with their metadata."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    if 'meta' in data:
                        meta = data['meta']
                    else:
                        # Old save format
                        player_data = data
                        difficulty = player_data.get('difficulty', 'Normal')
                        if isinstance(difficulty, dict):
                            difficulty = difficulty.get('name', 'Normal')
                        meta = {
                            "player_name": strip_ansi(player_data.get('name') or 'Unknown'),
                            "level": player_data.get('level', 1),
                            "difficulty": str(difficulty).strip(),
                            "location": f"Dungeon Floor {player_data.get('dungeon_level', 1)}",
                            "playtime": player_data.get('playtime_seconds', 0),
                            "last_save": "Unknown",
                            "save_type": "manual"
                        }
                    meta['filename'] = filename
                    saves.append(meta)
                except (json.JSONDecodeError, KeyError):
                    continue
        # Sort by last_save descending
        saves.sort(key=lambda x: x.get('last_save', ''), reverse=True)
        return saves

    def load_save(self, save_id: str) -> Optional[Dict[str, Any]]:
        """Loads a save by its ID and returns the data."""
        filepath = os.path.join(self.save_dir, save_id)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            # Handle old saves that are just player dict
            if 'meta' not in data:
                # Old save format
                player_data = data
                difficulty = player_data.get('difficulty', 'Normal')
                if isinstance(difficulty, dict):
                    difficulty = difficulty.get('name', 'Normal')
                meta = {
                    "player_name": strip_ansi(player_data.get('name') or 'Unknown'),
                    "level": player_data.get('level', 1),
                    "difficulty": str(difficulty).strip(),
                    "location": f"Dungeon Floor {player_data.get('dungeon_level', 1)}",
                    "playtime": player_data.get('playtime_seconds', 0),
                    "last_save": "Unknown",
                    "save_type": "manual"
                }
                data = {
                    "meta": meta,
                    "player_data": player_data,
                    "dungeon_state": {},
                    "inventory": {}
                }
            return data
        except json.JSONDecodeError:
            return None

    def create_save(self, player: 'Player', dungeon: Optional['Dungeon'] = None, save_type: str = "manual") -> str:
        """Creates a new save with the current player and dungeon state."""
        from core.entity import Player  # Import here to avoid circular import

        try:
            meta = {
                "player_name": player.name,
                "level": player.level,
                "difficulty": str(player.difficulty),
                "location": f"Dungeon Floor {player.dungeon_level}",
                "playtime": int(player.get_playtime()),
                "last_save": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "save_type": save_type
            }

            save_data = {
                "meta": meta,
                "player_data": player.to_dict(),
                "dungeon_state": {},  # TODO: implement dungeon serialization
                "inventory": {}  # Inventory is part of player_data
            }

            filename = f"{save_type}-{player.name}(lv{player.level})-{player.player_id}.json"
            filepath = os.path.join(self.save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)

            return filename
        except Exception as e:
            from engine.game_utility import handle_error
            handle_error()
            # Return a dummy filename or raise
            raise

    def delete_save(self, save_id: str) -> bool:
        """Deletes a save by its ID."""
        filepath = os.path.join(self.save_dir, save_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def autosave(self, player: 'Player', dungeon: Optional['Dungeon'] = None):
        """Automatically saves the current state at regular intervals."""
        try:
            # Rotate autosaves
            autosave_files = [f for f in os.listdir(self.save_dir) if f.startswith('autosave_') and f.endswith('.json')]
            autosave_files.sort(reverse=True)

            # Delete autosave_3 if exists
            for f in autosave_files:
                if 'autosave_3' in f:
                    os.remove(os.path.join(self.save_dir, f))
                    break

            # Rename autosave_2 to autosave_3
            for f in autosave_files:
                if 'autosave_2' in f:
                    os.rename(os.path.join(self.save_dir, f), os.path.join(self.save_dir, f.replace('autosave_2', 'autosave_3')))
                    break

            # Rename autosave_1 to autosave_2
            for f in autosave_files:
                if 'autosave_1' in f:
                    os.rename(os.path.join(self.save_dir, f), os.path.join(self.save_dir, f.replace('autosave_1', 'autosave_2')))
                    break

            # Create new autosave_1
            filename = self.create_save(player, dungeon, "auto")
            new_path = os.path.join(self.save_dir, filename)
            autosave_1_path = os.path.join(self.save_dir, filename.replace('auto-', 'autosave_1-'))
            os.rename(new_path, autosave_1_path)
        except Exception as e:
            from engine.game_utility import handle_error
            handle_error()
