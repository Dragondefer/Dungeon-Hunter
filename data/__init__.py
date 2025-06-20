from sys import path
from os.path import abspath, dirname, join
# Define the root of the project
path.append(abspath(join(dirname(__file__), '..')))

from .progression_data import quests_dict, achievements, EVENTS
from .player_data import can_send_analytics, get_random_names, unlockable_classes
from .rooms_data import room_descriptions, rest_events, puzzle_choices
from .enemies_data import enemy_types, boss_types, enemy_sets, armor_sets
from .spells_data import spells
from .special_attacks import special_attacks_dict, weapon_special_attacks, flaming_strike, frost_slam, lightning_strike, arcane_explosion, earth_shatter
