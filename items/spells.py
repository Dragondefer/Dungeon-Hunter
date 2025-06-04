__version__ = "7.0"
__creation__ = "24-05-2025"

from interface.colors import Colors
from engine.logger import logger

class Spell:
    """
    Represents a spell that can be cast by the player.

    Attributes:
        name (str): The name of the spell.
        description (str): A brief description of the spell.
        mana_cost (int): The mana cost to cast the spell.
        effect (callable): A function that defines the spell's effect when cast.
    """
    def __init__(self, name, description, mana_cost, effect):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.effect = effect  # function(caster, target) -> None

    def cast(self, caster, target):
        """
        Cast the spell, applying its effect if the caster has enough mana.

        Args:
            caster (Player): The entity casting the spell.
            target (Entity): The target of the spell.
        """
        if caster.stats.mana < self.mana_cost:
            print(f"{Colors.RED}Not enough mana to cast {self.name}!{Colors.RESET}")
            return False
        caster.use_mana(self.mana_cost)
        print(f"{Colors.MAGENTA}{caster.name} casts {self.name}!{Colors.RESET}")
        self.effect(caster, target)
        return True

    def __str__(self):
        return f"{self.name} - {self.description} (Mana Cost: {self.mana_cost})"


class Scroll:
    """
    Represents a consumable scroll that casts a spell when used.

    Attributes:
        name (str): The name of the scroll.
        description (str): Description of the scroll.
        value (int): The value of the scroll.
        spell (Spell): The spell contained in the scroll.
    """
    def __init__(self, name, description, value, spell):
        self.name = name
        self.description = description
        self.value = value
        self.spell = spell

    def use(self, caster, target):
        """
        Use the scroll to cast its spell and consume the scroll.

        Args:
            caster (Player): The entity using the scroll.
            target (Entity): The target of the spell.
        """
        success = self.spell.cast(caster, target)
        if success:
            try:
                caster.inventory.remove(self)
                print(f"{Colors.YELLOW}The scroll of {self.spell.name} crumbles to dust after use.{Colors.RESET}")
            except ValueError:
                logger.warning(f"Scroll {self.name} not found in inventory during use.")
        return success

    def __str__(self):
        return f"{self.name} (Scroll) - {self.description} (Casts: {self.spell.name})"
