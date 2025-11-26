__version__ = "40.0"
__creation__ = "24-05-2025"

# D​un​g​e​on​ ​H​u​n​te​r​ ​-​ ​(​c)​ ​D​ra​g​onde​f​er​ ​2​02​5
# L​i​c​en​se​d​ ​u​nd​er​ ​C​C​-​B​Y​-​NC​ 4.​0

from interface.colors import Colors
from engine.logger import logger
from engine.game_utility import ancient_text, glitch_text

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
        self.encrypted_name = glitch_text(name)
        self.description = description
        self.mana_cost = mana_cost
        self.effect = effect  # function(caster, target) -> None

    def __str__(self):
        return f"{self.name} - {self.description} (Mana Cost: {self.mana_cost})"
    
    def to_dict(self):
        """
        Convert the spell to a dictionary representation.

        Returns:
            dict: A dictionary containing the spell's attributes.
        """
        return {
            'name': self.name,
            'description': self.description,
            'mana_cost': self.mana_cost,
            'effect': self.effect.__name__ if callable(self.effect) else self.effect  # Store the function name for reference
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Spell":
        name: str = data.get("name", "")
        description: str = data.get("description", "")
        mana_cost: int = data.get("mana_cost", 0)

        effect_name = data.get("effect")
        effect = None
        if isinstance(effect_name, str):
            effect = globals().get(effect_name, None)
        # fallback : garde la valeur brute si jamais pas une str
        if effect is None:
            effect = effect_name  

        return cls(name, description, mana_cost, effect)


    def get_mastery_key(self):
        return f"weapon::{self.__class__.__name__}"

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



def get_random_spell(name=None):
    """
    Get a random spell from the predefined spells data.

    Returns:
        Spell: A randomly selected spell.
    """
    import random
    from data import spells_dict
    if name:
        spell = spells_dict.get(name)
    else:
        spell = random.choice(list(spells_dict.values()))
    return spell

def get_random_scroll(name=None):
    """
    Get a random scroll containing a spell.

    Returns:
        Scroll: A randomly selected scroll with a spell.
    """
    import random
    from data import spells_dict
    from items.items import Scroll
    if name:
        spell = spells_dict.get(name)
        if spell is None:
            logger.error(f"Spell with name '{name}' not found.")
            return None
    else:
        spell = random.choice(list(spells_dict.values()))
    return Scroll(
        name=f"Scroll of {spell.encrypted_name}",
        description=f"A scroll that allows you to cast {spell.encrypted_name}.",
        value=500,  # Default value if not specified
        spell=spell
    )

