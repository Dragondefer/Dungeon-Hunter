__version__ = "17.0"
__creation__ = "9-03-2025"

from colors import Colors
from game_utility import clear_screen
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
        from items import Item
        quest = cls(
            data["title"],
            data["description"],
            data["objective_type"],
            data["goal"],
            data["reward_gold"],
            data["reward_xp"],
            Item.from_dict(data["reward_item"]) if data["reward_item"] else None
        )
        quest.progress = data["progress"]
        quest.completed = data["completed"]
        return quest

