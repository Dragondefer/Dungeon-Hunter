__version__ = "87.0"
__creation__ = "09-03-2025"

import time

from interface.colors import Colors
from engine.game_utility import clear_screen
from engine.logger import logger

class Quest:
    """
    Represents a quest that the player can complete for rewards.

    Attributes:
        title (str): The name of the quest.
        description (str): A short explanation of the quest's objective.
        objective_type (str): The type of goal (e.g., "kill_enemies", "find_items").
        objective_amount (int): The required number of actions to complete the quest.
        current_progress (int): The current progress toward completion.
        completed (bool): Indicates if the quest is finished.
        reward_gold (int): The amount of gold given as a reward.
        reward_xp (int): The XP given as a reward.
        reward_item (Item | None): An optional item reward.

    Methods:
        update_progress(amount: int = 1) -> bool:
            Increases progress and checks for completion.
        
        __str__() -> str:
            Returns a formatted string representation of the quest.
    """
    def __init__(self, title, description, objective_type, objective_amount, reward_gold, reward_xp, reward_item=None):
        self.title = title
        self.description = description
        self.objective_type = objective_type  # "kill_enemies", "find_items", "explore_rooms", etc.
        self.objective_amount = objective_amount
        self.current_progress = 0
        self.completed = False
        self.reward_gold = reward_gold
        self.reward_xp = reward_xp
        self.reward_item = reward_item
    
    def update_progress(self, amount=1):
        self.current_progress += amount
        if self.current_progress >= self.objective_amount and not self.completed:
            self.completed = True
            return True
        return False
    
    def __str__(self):
        status = f"{Colors.GREEN}(COMPLETED){Colors.RESET}" if self.completed else f"{Colors.YELLOW}({self.current_progress}/{self.objective_amount}){Colors.RESET}"
        return f"{self.title} {status}\n  {self.description}"

    def to_dict(self):
        """Converts a quest to a dictionary for saving."""
        return {
            "title": self.title,
            "description": self.description,
            "objective_type": self.objective_type,
            "progress": self.current_progress,
            "goal": self.objective_amount,
            "reward_gold": self.reward_gold,
            "reward_xp": self.reward_xp,
            "reward_item": self.reward_item.to_dict() if self.reward_item else None,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a quest from a dictionary."""
        from items.items import Item
        quest = cls(
            data["title"],
            data["description"],
            data["objective_type"],
            data["goal"],
            data["reward_gold"],
            data["reward_xp"],
            Item.from_dict(data["reward_item"]) if data["reward_item"] else None
        )
        quest.current_progress = data["progress"]
        quest.completed = data["completed"]
        return quest




class Achievement:
    """
    Represents an achievement that can be unlocked by the player.
    
    Attributes:
        id (str): Unique identifier for the achievement.
        name (str): Name of the achievement.
        description (str): Description of the achievement.
        condition (function): A function that checks if the achievement can be unlocked.
        unlocked (bool): Indicates if the achievement has been unlocked.
    
    Methods:
        check(player): Checks if the achievement can be unlocked based on the player's state.
        __str__(): Returns a string representation of the achievement.
    """
    def __init__(self, id, name, description, condition, hidden=False):
        self.id = id
        self.name = name
        self.description = description
        self.condition = condition  # Fonction lambda qui prend le joueur en paramètre
        self.unlocked = False
        self.hidden = hidden


    def check(self, player):
        if not self.unlocked and self.condition(player):
            self.unlocked = True
            print(f"{Colors.GREEN}{self.name} unlocked ! - {self.description}{Colors.RESET}")
            time.sleep(2)
            return True
        return False

    def __str__(self):
        color_main, color_char, status_char = ((Colors.BRIGHT_GREEN, Colors.GREEN, "Y") if self.unlocked else (Colors.BRIGHT_RED, Colors.RED, "X"))
        return f"{color_main}[{color_char}{status_char}{color_main}] {self.name}: {self.description}{Colors.RESET}"

    def to_dict(self):
        """Converts an Achievement instance to a dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "unlocked": self.unlocked,
            "hidden": self.hidden,
            # Store the condition as the id, assuming external mapping for deserialization
            "condition_id": self.id
        }

    @classmethod
    def from_dict(cls, data, condition_mapping):
        """Creates an Achievement instance from a dictionary and a condition mapping."""
        condition_func = condition_mapping.get(data.get("condition_id"))
        achievement = cls(
            data["id"],
            data["name"],
            data["description"],
            condition_func,
            data.get("hidden", False)
        )
        achievement.unlocked = data.get("unlocked", False)
        return achievement



class Event:
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect  # une fonction

    def trigger(self, player):
        print(self.description)
        self.effect(player)
