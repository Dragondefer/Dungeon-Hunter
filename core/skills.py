from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.entity import Player

__version__ = "10.0"
__creation__ = "06-06-2025"

# D​u​ng​e​on​ ​H​un​t​e​r​ ​-​ ​(​c)​ ​Dra​g​on​de​f​e​r​ ​2​02​5
# L​i​c​e​nse​d​ ​u​n​d​er ​C​C​-​B​Y​-​NC​ ​4.​0

from interface.colors import Colors
from engine.game_utility import timed_input_pattern


#̶̼͝ E̶͍̚v̶̼͝ë̵͕́r̷͍̈́ÿ̸̡́ s̸̱̅k̵̢͝i̴̊͜l̷̫̈́l̷̫̈́ h̵̤͒ä̷̪́s̸̱̅ ä̷̪́ p̵̦̆r̷͍̈́i̴̊͜c̴̱͝ë̵͕́.̵͇̆.̵͇̆.̵͇̆ s̸̱̅o̶͙͝m̴̛̠ë̵͕́ m̴̛̠o̶͙͝r̷͍̈́ë̵͕́ ẗ̴̗́h̵̤͒ä̷̪́n̸̻̈́ o̶͙͝ẗ̴̗́h̵̤͒ë̵͕́r̷͍̈́s̸̱̅.̵͇̆
class Skill:
    """
    Represents a special skill with:
    - name: the name of the skill.
    - description: a description of the skill.
    - level: the mastery level of the skill.
    - damage_multiplier: multiplier applied to the base damage.
    - temporary_bonus: a dict of bonus effects (e.g., {"defense": 5}).
    - cost: a dict of resource costs (e.g., {"mana": 10, "stamina": 5, "hp": 0}).
    """
    def __init__(self, name, description, damage_multiplier=1.0, temporary_bonus=None, cost=None):
        self.name = name
        self.description = description
        self.damage_multiplier = damage_multiplier
        self.temporary_bonus = temporary_bonus if temporary_bonus is not None else {}
        self.cost = cost if cost is not None else {}

    def to_dict(self):
        """Convertit l'objet Skill en dictionnaire automatiquement."""
        return self.__dict__.copy()
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            damage_multiplier=data.get("damage_multiplier", 1),
            temporary_bonus=data.get("temporary_bonus", {}),
            cost=data.get("cost", {})
        )
    
    def get_mastery_key(self):
        return f"weapon::{self.__class__.__name__}"

    def __str__(self):
        cost_str = ", ".join(f"{k}: {v}" for k, v in self.cost.items()) if self.cost else "No cost"
        bonus_str = ", ".join(f"{k}: +{v}" for k, v in self.temporary_bonus.items()) if self.temporary_bonus else "No bonus"
        return f"{self.name} (Lv): {self.description} | Multiplier: {self.damage_multiplier} | Cost: {cost_str} | Bonus: {bonus_str}"

    def activate(self, player:Player):
        """
        Activates the skill:
          - Checks if the player has enough resources (mana, stamina, hp) based on self.cost.
          - If not, prints an error and returns a multiplier of 0.
          - Otherwise, it deducts the cost and applies temporary bonuses.
          - Returns the damage multiplier of the skill.
        """
        # Vérifier que le joueur dispose des ressources nécessaires
        for resource, cost_value in self.cost.items():
            current_value = getattr(player.stats, resource, 0)
            if current_value < cost_value:
                print(f"{Colors.RED}You don't have enough {resource} to use {self.name}!{Colors.RESET}")
                return 0
        
        print(f"\n{Colors.YELLOW}Timing skill activation!\nPress Enter at the right moment to increase skill effect.{Colors.RESET}")
        input_multiplier = 1
        timing_success = timed_input_pattern(difficulty=1.0, return_type='int')

        if timing_success:
            print(f"{Colors.GREEN}Perfect timing! Skill damage increased by 50%.{Colors.RESET}")
            input_multiplier *= 1.5
        else:
            print(f"{Colors.RED}Poor timing! Skill damage reduced by 25%.{Colors.RESET}")
            input_multiplier *= 0.75

        # Déduire le coût des ressources
        for resource, cost_value in self.cost.items():
            # Deduct the correct resource cost
            if resource == "mana":
                player.use_mana(cost_value)
            elif resource == "stamina":
                player.use_stamina(cost_value)
            elif resource == "hp":
                player.stats.take_damage(cost_value)
                        
        # Appliquer les bonus temporaires
        for stat, bonus in self.temporary_bonus.items():
            player.stats.modify_stat(stat, bonus, "temporary")

        print(f"{Colors.GREEN}{self.name} activated!{Colors.RESET}")
        return self.damage_multiplier * input_multiplier

