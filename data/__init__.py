# D?u?n?g?e?o?n? ?H?u?n?t?e?r? ?-? ?(?c?)? ?D?r?a?g?o?n?d?e?f?e?r? ?2?0?2?5
# L?i?c?e?n?s?e?d? ?u?n?d?e?r? ?C?C? ?B?Y?-?N?C? ?4?.?0

from sys import path
from os.path import abspath, dirname, join
# Define the root of the project
path.append(abspath(join(dirname(__file__), '..')))

from .progression_data import quests_dict, achievements, EVENTS
from .player_data import can_send_analytics, get_random_names, unlockable_classes
from .rooms_data import room_descriptions, rest_events, puzzle_choices
from .enemies_data import enemy_types, boss_types, enemy_sets, armor_sets
from .special_attacks import special_attacks_dict, weapon_special_attacks, flaming_strike, frost_slam, lightning_strike, arcane_explosion, earth_shatter


# Converting raw data
from .skills_data import skills_dict_raw
from core.skills import Skill

def build_skills(raw_skills: dict[str, dict]) -> dict[str, Skill]:
    return {name: Skill.from_dict(data) for name, data in raw_skills.items()}

skills_dict = build_skills(skills_dict_raw)

from .spells_data import spells_dict_raw
from core.spells import Spell

def build_spells(raw_spells: dict[str, dict]) -> dict[str, Spell]:
    return {name: Spell.from_dict(data=data) for name, data in raw_spells.items()}

spells_dict = build_spells(spells_dict_raw)


# Converting raw data
from data.crafting_data import weapon_upgrade_recipes_dict_raw, recipes_dict_raw
from items.crafting import Recipe

def build_recipes(raw_data: dict[str, dict]) -> dict[str, Recipe]:
    return {key: Recipe.from_dict(data) for key, data in raw_data.items()}

recipes_dict = build_recipes(recipes_dict_raw)
weapon_upgrade_recipes_dict = build_recipes(weapon_upgrade_recipes_dict_raw)


from items.resources import Resource
from .resources_data import resources_data_raw

def build_resources(raw_data: dict[str, dict[str, str|int]]) -> dict[str, Resource]:
    return {key: Resource.from_dict(data) for key, data in raw_data.items()}

resources_data = build_resources(resources_data_raw)