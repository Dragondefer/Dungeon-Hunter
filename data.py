__version__ = "224.0"
__creation__ = "16-03-2025"

import random

# Rooms
room_descriptions = {
    "combat": [
        "a grand hall with a large stone door at the far end.",
        "a dimly lit chamber with weapon racks along the walls",
        "a large hall with ancient battle markings etched on the floor",
        "a circular arena-like room with bloodstains",
        "a narrow corridor with defensive positions",
        "a guard post with broken chairs and tables",
    ],
    "treasure": [
        "a foreboding cave with ancient carvings on the walls.",
        "a narrow corridor with a faint glow emanating from the end.",
        "a small vault with a ornate chest in the center",
        "a hidden alcove with gleaming objects",
        "an abandoned storeroom with scattered valuables",
        "a noble's personal treasury, long forgotten",
        "a shrine with offerings and tributes"
    ],
    "shop": [
        "a makeshift trading post set up by a wandering merchant",
        "a well-stocked storage room converted to a shop",
        "a traveling peddler's cart, somehow down here",
        "a smuggler's hideout with goods for sale",
        "an old dwarf's forge and supply store"
    ],
    "rest": [
        "a quiet sanctuary with a small fountain",
        "a warm, comfortable chamber with bedrolls",
        "an abandoned barracks with salvageable bedding",
        "a peaceful meditation room with incense still burning",
        "a secure room with a heavy door that can be barred"
    ],
    "puzzle": [
        "a mysterious chamber with strange symbols on the walls",
        "a room with a complex mechanism in the center",
        "an arcane laboratory with puzzling apparatus",
        "a trial chamber with riddles inscribed on pillars",
        "a test of wit designed by an eccentric wizard"
    ],
    "boss": [
        "a massive throne room with imposing decorations",
        "a lair filled with bones and treasures",
        "a sacred chamber corrupted by dark forces",
        "an ancient battlefield where a powerful entity awaits",
        "a sealed vault, obviously containing something dangerous"
    ]
}


rest_events = [
    {"description": "You have a prophetic dream that reveals hidden knowledge.", "effect": "luck", "value": 2},
    {"description": "You practice combat techniques in your sleep.", "effect": "attack", "value": 2},
    {"description": "You have a nightmare that leaves you alert to danger.", "effect": "defense", "value": 2},
    {"description": "A wandering merchant finds you and offers a special deal.", "effect": "item", "value": None},
    {"description": "You wake up to find a small creature has stolen some of your gold!", "effect": "gold", "value": -random.randint(5, 15)}
]


# Puzzles
puzzle_choices = [
    {
        "description": "In front of you are three coloured potions: red, blue and green.",
        "options": {
            "1": {"name": "Red Potion", "result": "good", "message": "You feel refreshed !", "effect": ("heal", 20)},
            "2": {"name": "Blue Potion", "result": "bad", "message": "You're feeling weak !", "effect": ("damage", 10)},
            "3": {"name": "Green Potion", "result": "good", "message": "You feel stronger !", "effect": ("attack_boost", 2)}
        }
    },
    {
        "description": "Three levers are engraved with strange symbols : ⚔️, ⛨ et ⚕️.",
        "options": {
            "1": {"name": "⚔️ Lever", "result": "good", "message": "A compartment reveals a weapon !", "effect": ("weapon", None)},
            "2": {"name": "⛨ Lever", "result": "good", "message": "A compartment reveals a suit of armor !", "effect": ("armor", None)},
            "3": {"name": "⚕️ Lever", "result": "mauvais", "message": "Poisoned gas escapes !", "effect": ("damage", 15)}
        }
    }
]

# Player

# Player's quests
def get_quests_dict():
    from progression import Quest
    quests_dict = {
        "Dungeon Master": Quest(
            title="Dungeon Master",
            description="Complete 10 dungeon levels.",
            objective_type="complete_dungeon_levels",
            objective_amount=10,
            reward_gold=500,
            reward_xp=1000,
            reward_item=None
        ),
        "Dungeon Explorer": Quest(
            title="Dungeon Explorer",
            description="Explore 5 rooms in the dungeon",
            objective_type="explore_rooms",
            objective_amount=5,
            reward_gold=50,
            reward_xp=30,
            reward_item=None
        ),
        "Treasure Hunter": Quest(
            title="Treasure Hunter",
            description="Find 10 items in the dungeon.",
            objective_type="find_items",
            objective_amount=10,
            reward_gold=100,
            reward_xp=60,
            reward_item=None
        ),
        "Slayer": Quest(
            title="Slayer",
            description="Kill 20 enemies in the dungeon.",
            objective_type="kill_enemies",
            objective_amount=20,
            reward_gold=150,
            reward_xp=80,
            reward_item=None
        ),
        "Gold Collector": Quest(
            title="Gold Collector",
            description="Collect 500 gold.",
            objective_type="collect_gold",
            objective_amount=500,
            reward_gold=200,
            reward_xp=100,
            reward_item=None
        ),
        "Potion Master": Quest(
            title="Potion Master",
            description="Use 5 healing potions.",
            objective_type="use_potions",
            objective_amount=5,
            reward_gold=120,
            reward_xp=70,
            reward_item=None
        ),
        "Puzzle Solver": Quest(
            title="Puzzle Solver",
            description="Complete 3 puzzles.",
            objective_type="complete_puzzles",
            objective_amount=3,
            reward_gold=130,
            reward_xp=90,
            reward_item=None
        ),
        "Dungeon Conqueror": Quest(
            title="Dungeon Conqueror",
            description="Defeat the final boss of the dungeon.",
            objective_type="defeat_final_boss",
            objective_amount=1,
            reward_gold=1000,
            reward_xp=2000,
            reward_item=None
        ),
    }
    return quests_dict

# Achievements
from progression import Achievement
achievements = [
    Achievement("first_blood", "First Blood", "Kill an enemy.", lambda p: p.kills >= 1),
    Achievement("collector", "Collector", "Get 10 items.", lambda p: p.items_collected >= 10),
    Achievement("hoarder", "Trunk rat", "Get 1000 gold.", lambda p: p.gold >= 1000),
    Achievement("still_alive", "I'm still standing !", "Having 1% HP", lambda p: round((p.stats.hp/p.stats.max_hp), 2) <= 0.01),
    Achievement("explorer", "Explorer", "Explore 100 rooms.", lambda p: p.total_rooms_explored >= 100),
    Achievement("10_steps", "Ten Steps Forward... or is it?", "Reach level 10", lambda p: p.dungeon_level == 10)
]


# Events
from progression import Event

def blood_moon_effect(player):
    player.stats.permanent_stats["attack"] += 5
    print("Une puissance obscure vous renforce... (ATK +5)")

def healing_waters(player):
    player.stats.permanent_stats["hp"] = player.stats.max_hp
    print("Les eaux guérissantes restaurent tous vos PV.")

EVENTS = [
    Event("Blood Moon", "Une lune rouge illumine la salle...", blood_moon_effect),
    Event("Healing Fountain", "Une fontaine magique vous soigne entièrement.", healing_waters),
    # Ajoute d'autres ici
]


# Enemies
enemy_types = [
    {"name": "Goblin",       "type": "Goblin",     "hp_mod": 0.8, "atk_mod": 0.9, "def_mod": 0.7, "min_level": 1},
    {"name": "Skeleton",     "type": "Skeleton",   "hp_mod": 0.7, "atk_mod": 1.0, "def_mod": 0.5, "min_level": 1},
    {"name": "Wolf",         "type": "Wolf",       "hp_mod": 0.6, "atk_mod": 1.2, "def_mod": 0.6, "min_level": 1},
    {"name": "Orc",          "type": "Orc",        "hp_mod": 1.2, "atk_mod": 1.1, "def_mod": 0.9, "min_level": 2},
    {"name": "Troll",        "type": "Troll",      "hp_mod": 1.5, "atk_mod": 1.3, "def_mod": 0.8, "min_level": 3},
    {"name": "Ghost",        "type": "Ghost",      "hp_mod": 0.9, "atk_mod": 1.0, "def_mod": 1.2, "min_level": 4},
    {"name": "Dark Elf",     "type": "Dark Elf",   "hp_mod": 1.0, "atk_mod": 1.4, "def_mod": 1.0, "min_level": 5},
    {"name": "Wraith",       "type": "Wraith",     "hp_mod": 1.1, "atk_mod": 1.5, "def_mod": 1.1, "min_level": 5},
    {"name": "Golem",        "type": "Golem",      "hp_mod": 1.8, "atk_mod": 1.0, "def_mod": 1.5, "min_level": 6},
    {"name": "Demon",        "type": "Demon",      "hp_mod": 2.0, "atk_mod": 1.8, "def_mod": 1.8, "min_level": 7},
    {"name": "Dragon Whelp", "type": "Dragon",     "hp_mod": 1.4, "atk_mod": 1.7, "def_mod": 1.2, "min_level": 8},
    {"name": "Dark Shape",   "type": "Dark Shape", "hp_mod": 1.0, "atk_mod": 2.0, "def_mod": 1.0, "min_level": 9},
]

boss_types = [
    {"name": "Goblin King",     "type": "Goblin",     "hp_mod": 1.0, "atk_mod": 1.0, "def_mod": 1.0, "agl_mod": 1.0, "min_level": 1},
    {"name": "Skeleton Lord",   "type": "Skeleton",   "hp_mod": 0.8, "atk_mod": 1.5, "def_mod": 1.2, "agl_mod": 1.0, "min_level": 2},
    {"name": "Alpha Dire Wolf", "type": "Wolf",       "hp_mod": 1.0, "atk_mod": 2.0, "def_mod": 1.4, "agl_mod": 2.0, "min_level": 3},
    {"name": "Orc Warlord",     "type": "Orc",        "hp_mod": 2.4, "atk_mod": 2.1, "def_mod": 1.7, "agl_mod": 0.5, "min_level": 4},
    {"name": "Ancient Troll",   "type": "Troll",      "hp_mod": 2.7, "atk_mod": 1.8, "def_mod": 1.6, "agl_mod": 0.5, "min_level": 5},
    {"name": "Spectre Lord",    "type": "Ghost",      "hp_mod": 2.2, "atk_mod": 2.0, "def_mod": 2.2, "agl_mod": 3.0, "min_level": 6},
    {"name": "Dark Elf Queen",  "type": "Dark Elf",   "hp_mod": 2.3, "atk_mod": 2.4, "def_mod": 2.0, "agl_mod": 2.0, "min_level": 7},
    {"name": "Wraith King",     "type": "Wraith",     "hp_mod": 2.5, "atk_mod": 2.5, "def_mod": 2.1, "agl_mod": 3.0, "min_level": 8},
    {"name": "Ancient Golem",   "type": "Golem",      "hp_mod": 3.0, "atk_mod": 2.0, "def_mod": 2.5, "agl_mod": 0.0, "min_level": 9},
    {"name": "Elder Dragon",    "type": "Dragon",     "hp_mod": 3.5, "atk_mod": 2.7, "def_mod": 2.2, "agl_mod": 1.0, "min_level": 10},
    {"name": "Dark Lord",       "type": "Dark Shape", "hp_mod": 3.5, "atk_mod": 3.5, "def_mod": 2.0, "agl_mod": 1.5, "min_level": 11},
    {"name": "Senessax",        "type": "Dragon",     "hp_mod": 5.0, "atk_mod": 5.0, "def_mod": 5.0, "agl_mod": 5.0, "min_level": 12},
]

# Sets
enemy_sets = {
    "Goblin":     {"armor": "Brigand",     "weapon": "Goblin Dagger"},
    "Skeleton":   {"armor": "Cursed Bone", "weapon": "Undead Blade"},
    "Wolf":       {"armor": "Hunter",      "weapon": "Wolf Claws"},
    "Orc":        {"armor": "Warrior",     "weapon": "Orcish Battle Axe"},
    "Troll":      {"armor": "Trollhide",   "weapon": "Bone Crusher"},
    "Ghost":      {"armor": "Spectral",    "weapon": "Phantom Scythe"},
    "Dark Elf":   {"armor": "Shadow",      "weapon": "Twin Shadow Blades"},
    "Wraith":     {"armor": "Fallen King", "weapon": "Wraithblade"},
    "Golem":      {"armor": "Stonebound",  "weapon": "Earthshatter Maul"},
    "Demon":      {"armor": "Infernal",    "weapon": "Hellfire Sword"},
    "Dragon":     {"armor": "Draconic",    "weapon": "Dragon Slayer"},
    "Dark Shape": {"armor": "Voidwalker",  "weapon": "Void Staff"},
}

armor_sets = {
    "Brigand": {
        "bonus_thresholds": {2: "quick_strikes", 4: "goblin_tenacity"},
        "effects": {
            "quick_strikes": {"agility": 5, "attack": 3},  # +5 agilité, +3 attaque
            "goblin_tenacity": {"agility": 10, "stamina": 15},  # +10% agilité, +15 stamina
        }
    },
    "Cursed Bone": {
        "bonus_thresholds": {2: "undead_resilience", 4: "bone_armor"},
        "effects": {
            "undead_resilience": {"defense": 5, "hp": 10},  # +5 défense, +10 HP max
            "bone_armor": {"defense": 5, "attack": 5},  # +10% résistance, +5 attaque
        }
    },
    "Hunter": {
        "bonus_thresholds": {2: "wolf_agility", 4: "predator_instinct"},
        "effects": {
            "wolf_agility": {"agility": 8, "attack": 5},  # +8 agilité, +5% esquive
            "predator_instinct": {"critical_chance": 10, "attack": 5},  # +10% chance critique, +5 attaque
        }
    },
    "Warrior": {
        "bonus_thresholds": {2: "orc_strength", 4: "berserker_fury"},
        "effects": {
            "orc_strength": {"attack": 7, "defense": 5},  # +7 attaque, +5 défense
            "berserker_fury": {"attack": 10, "stamina": 20},  # +10 attaque, +20 stamina
        }
    },
    "Trollhide": {
        "bonus_thresholds": {2: "regenerative_skin", 4: "troll_resilience"},
        "effects": {
            "regenerative_skin": {"hp_regen": 3, "defense": 5},  # +3 HP régén par tour, +5 défense
            "troll_resilience": {"hp": 30, "defense": 10},  # +30 HP max, +10% résistance
        }
    },
    "Spectral": {
        "bonus_thresholds": {2: "ghostly_presence", 4: "ethereal_form"},
        "effects": {
            "ghostly_presence": {"agility": 10, "mana": 10},  # +10% d'agilité, +10 mana
            "ethereal_form": {"agility": 5, "magic_resist": 10},  # +15% d'agilité, +10% résistance magique
        }
    },
    "Shadow": {
        "bonus_thresholds": {2: "shadow_step", 4: "invisibility"},
        "effects": {
            "shadow_step": {"agility": 10, "attack": 5},  # +10% d'agilité, +10% d'attaque
            "invisibility": {"agility": 15, "critical_chance": 5},  # +15% agilité, +5% critique
        }
    },
    "Fallen King": {
        "bonus_thresholds": {2: "wraith_presence", 4: "king_of_the_dead"},
        "effects": {
            "wraith_presence": {"mana": 10, "magic_resist": 10},  # +10 mana, +10% résistance magique
            "king_of_the_dead": {"attack": 10, "defense": 10},  # +10 attaque, +10 défense
        }
    },
    "Stonebound": {
        "bonus_thresholds": {2: "earthly_endurance", 4: "titanic_resistance"},
        "effects": {
            "earthly_endurance": {"defense": 10, "hp": 20},  # +10 défense, +20 HP max
            "titanic_resistance": {"defense": 20, "stamina_cost": -5},  # +20% résistance physique, -5% coût stamina
        }
    },
    "Infernal": {
        "bonus_thresholds": {2: "hellfire_aura", 4: "infernal_rage"},
        "effects": {
            "hellfire_aura": {"fire_damage": 20, "fire_resist": 10},  # +20% dégâts de feu, +10% résistance feu
            "infernal_rage": {"attack": 15, "defense": -5},  # +15 attaque, -5 défense
        }
    },
    "Draconic": {
        "bonus_thresholds": {2: "fire_resistance", 4: "full_draconic_power"},
        "effects": {
            "fire_resistance": {"fire_resist": 15},  # +15% résistance au feu
            "full_draconic_power": {"defense": 15, "attack": 10, "hp": 25},  # +15 défense, +10 attaque, +25 HP
        }
    },
    "Voidwalker": {
        "bonus_thresholds": {2: "dark_energy", 4: "void_mastery"},
        "effects": {
            "dark_energy": {"mana": 15, "magic_damage": 10},  # +15 mana, +10% dégâts magiques
            "void_mastery": {"agility": 10, "critical_chance": 10},  # +10% furtivité, +10% critique
        }
    }
}
