from sys import path
from os.path import abspath, dirname, join
# Define the root of the project
path.append(abspath(join(dirname(__file__), '..')))


from .inventory import Inventory
from .items import Item, Gear, Weapon, Armor, Shield, Gauntlets, Amulet, Ring, Belt, Potion, Equipment
from .spells import Spell, Scroll
