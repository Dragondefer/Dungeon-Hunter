__version__ = "20.0"
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
            'effect': self.effect.__name__  # Store the function name for reference
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Spell":
        """
        Create a Spell instance from a dictionary.

        Args:
            data (dict): A dictionary containing spell attributes.

        Returns:
            Spell: An instance of Spell created from the dictionary.
        """
        name = data.get('name')
        description = data.get('description')
        mana_cost = data.get('mana_cost')
        effect = data.get('effect')
        # effect might be a dict or function name, handle accordingly if needed
        # For now, assign effect directly
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

    def __str__(self):
        return f"{self.name} (Scroll) - {self.description}"
    
    def to_dict(self):
        """
        Convert the scroll to a dictionary representation.

        Returns:
            dict: A dictionary containing the scroll's attributes.
        """
        return {
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'spell': {
                'name': self.spell.name,
                'description': self.spell.description,
                'mana_cost': self.spell.mana_cost
            }
        }
    
    def from_dict(self, data):
        """
        Load scroll attributes from a dictionary.

        Args:
            data (dict): A dictionary containing scroll attributes.
        """
        self.name = data.get('name', self.name)
        self.description = data.get('description', self.description)
        self.value = data.get('value', self.value)
        spell_data = data.get('spell', {})
        self.spell = Spell(
            name=spell_data.get('name', self.spell.name),
            description=spell_data.get('description', self.spell.description),
            mana_cost=spell_data.get('mana_cost', self.spell.mana_cost),
            effect=self.spell.effect  # Assuming effect is already set
        )


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

