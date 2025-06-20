# Enemies
enemy_types = [
    {"name": "Goblin",       "type": "Goblin",     "hp_mod": 0.8, "atk_mod": 0.9, "def_mod": 0.7, "min_level": 1},
    {"name": "Skeleton",     "type": "Skeleton",   "hp_mod": 0.7, "atk_mod": 1.0, "def_mod": 0.5, "min_level": 1},
    {"name": "Wolf",         "type": "Wolf",       "hp_mod": 0.6, "atk_mod": 1.2, "def_mod": 0.6, "min_level": 1},
    {"name": "Orc",          "type": "Orc",        "hp_mod": 1.0, "atk_mod": 1.4, "def_mod": 0.9, "min_level": 2},
    {"name": "Troll",        "type": "Troll",      "hp_mod": 1.5, "atk_mod": 1.3, "def_mod": 0.8, "min_level": 3},
    {"name": "Ghost",        "type": "Ghost",      "hp_mod": 0.9, "atk_mod": 1.5, "def_mod": 1.2, "min_level": 4},
    {"name": "Dark Elf",     "type": "Dark Elf",   "hp_mod": 1.0, "atk_mod": 1.4, "def_mod": 1.0, "min_level": 5},
    {"name": "Wraith",       "type": "Wraith",     "hp_mod": 1.1, "atk_mod": 1.5, "def_mod": 1.1, "min_level": 5},
    {"name": "Golem",        "type": "Golem",      "hp_mod": 1.8, "atk_mod": 1.0, "def_mod": 1.5, "min_level": 6},
    {"name": "Demon",        "type": "Demon",      "hp_mod": 2.0, "atk_mod": 1.8, "def_mod": 1.8, "min_level": 7},
    {"name": "Dragon Whelp", "type": "Dragon",     "hp_mod": 1.4, "atk_mod": 1.7, "def_mod": 1.2, "min_level": 8},
    {"name": "Dark Shape",   "type": "Dark Shape", "hp_mod": 0.6, "atk_mod": 1.8, "def_mod": 2.0, "min_level": 9},
]

boss_types = [
    {"name": "Goblin King",     "type": "Goblin",     "hp_mod": 1.0, "atk_mod": 1.0, "def_mod": 1.0, "agl_mod": 1.0, "min_level": 1},
    {"name": "Skeleton Lord",   "type": "Skeleton",   "hp_mod": 0.8, "atk_mod": 1.5, "def_mod": 1.2, "agl_mod": 1.0, "min_level": 2},
    {"name": "Alpha Dire Wolf", "type": "Wolf",       "hp_mod": 0.6, "atk_mod": 2.0, "def_mod": 1.4, "agl_mod": 2.0, "min_level": 3},
    {"name": "Orc Warlord",     "type": "Orc",        "hp_mod": 2.4, "atk_mod": 2.1, "def_mod": 1.7, "agl_mod": 0.5, "min_level": 4},
    {"name": "Ancient Troll",   "type": "Troll",      "hp_mod": 2.7, "atk_mod": 1.8, "def_mod": 1.6, "agl_mod": 0.5, "min_level": 5},
    {"name": "Spectre Lord",    "type": "Ghost",      "hp_mod": 2.2, "atk_mod": 2.0, "def_mod": 2.2, "agl_mod": 3.0, "min_level": 6},
    {"name": "Dark Elf Queen",  "type": "Dark Elf",   "hp_mod": 2.3, "atk_mod": 2.4, "def_mod": 2.0, "agl_mod": 2.0, "min_level": 7},
    {"name": "Wraith King",     "type": "Wraith",     "hp_mod": 2.5, "atk_mod": 2.5, "def_mod": 2.1, "agl_mod": 3.0, "min_level": 8},
    {"name": "Ancient Golem",   "type": "Golem",      "hp_mod": 3.0, "atk_mod": 2.0, "def_mod": 2.5, "agl_mod": 0.0, "min_level": 9},
    {"name": "Ancient Dragon",  "type": "Dragon",     "hp_mod": 3.5, "atk_mod": 2.7, "def_mod": 2.2, "agl_mod": 1.0, "min_level": 10},
    {"name": "Dark Lord",       "type": "Dark Shape", "hp_mod": 3.5, "atk_mod": 3.5, "def_mod": 2.0, "agl_mod": 1.5, "min_level": 11},
    {"name": "Iron Dragon",     "type": "Dragon",     "hp_mod": 5.0, "atk_mod": 5.0, "def_mod": 5.0, "agl_mod": 5.0, "min_level": 12},
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
            "goblin_tenacity": {"agility": 10, "max_stamina": 15},  # +10 agilité, +15 stamina
        }
    },
    "Cursed Bone": {
        "bonus_thresholds": {2: "undead_resilience", 4: "bone_armor"},
        "effects": {
            "undead_resilience": {"defense": 5, "max_hp": 10},  # +5 défense, +10 HP max
            "bone_armor": {"defense": 5, "attack": 5},  # +10 résistance, +5 attaque
        }
    },
    "Hunter": {
        "bonus_thresholds": {2: "wolf_agility", 4: "predator_instinct"},
        "effects": {
            "wolf_agility": {"agility": 8, "attack": 5},  # +8 agilité, +5 esquive
            "predator_instinct": {"critical_chance": 10, "attack": 5},  # +10 chance critique, +5 attaque
        }
    },
    "Warrior": {
        "bonus_thresholds": {2: "orc_strength", 4: "berserker_fury"},
        "effects": {
            "orc_strength": {"attack": 7, "defense": 5},  # +7 attaque, +5 défense
            "berserker_fury": {"attack": 10, "max_stamina": 20},  # +10 attaque, +20 stamina
        }
    },
    "Trollhide": {
        "bonus_thresholds": {2: "regenerative_skin", 4: "troll_resilience"},
        "effects": {
            "regenerative_skin": {"hp_regen": 3, "defense": 5},  # +3 HP régén par tour, +5 défense
            "troll_resilience": {"max_hp": 30, "defense": 10},  # +30 HP max, +10 résistance
        }
    },
    "Spectral": {
        "bonus_thresholds": {2: "ghostly_presence", 4: "ethereal_form"},
        "effects": {
            "ghostly_presence": {"agility": 10, "max_mana": 10},  # +10 d'agilité, +10 mana
            "ethereal_form": {"agility": 5, "magic_resist": 10},  # +15 d'agilité, +10 résistance magique
        }
    },
    "Shadow": {
        "bonus_thresholds": {2: "shadow_step", 4: "invisibility"},
        "effects": {
            "shadow_step": {"agility": 10, "attack": 5},  # +10 d'agilité, +10 d'attaque
            "invisibility": {"agility": 15, "critical_chance": 5},  # +15 agilité, +5 critique
        }
    },
    "Fallen King": {
        "bonus_thresholds": {2: "wraith_presence", 4: "king_of_the_dead"},
        "effects": {
            "wraith_presence": {"max_mana": 10, "magic_resist": 10},  # +10 mana, +10 résistance magique
            "king_of_the_dead": {"attack": 10, "defense": 10},  # +10 attaque, +10 défense
        }
    },
    "Stonebound": {
        "bonus_thresholds": {2: "earthly_endurance", 4: "titanic_resistance"},
        "effects": {
            "earthly_endurance": {"defense": 10, "hp": 20},  # +10 défense, +20 HP max
            "titanic_resistance": {"defense": 20, "stamina_cost": -5},  # +20 résistance physique, -5 coût stamina
        }
    },
    "Infernal": {
        "bonus_thresholds": {2: "hellfire_aura", 4: "infernal_rage"},
        "effects": {
            "hellfire_aura": {"fire_damage": 20, "fire_resist": 10},  # +20 dégâts de feu, +10 résistance feu
            "infernal_rage": {"attack": 15, "defense": -5},  # +15 attaque, -5 défense
        }
    },
    "Draconic": {
        "bonus_thresholds": {2: "fire_resistance", 4: "full_draconic_power"},
        "effects": {
            "fire_resistance": {"fire_resist": 15},  # +15 résistance au feu
            "full_draconic_power": {"defense": 15, "attack": 10, "max_hp": 25},  # +15 défense, +10 attaque, +25 HP
        }
    },
    "Voidwalker": {
        "bonus_thresholds": {2: "dark_energy", 4: "void_mastery"},
        "effects": {
            "dark_energy": {"mana": 15, "magic_damage": 10},  # +15 mana, +10 dégâts magiques
            "void_mastery": {"agility": 10, "critical_chance": 10},  # +10 furtivité, +10 critique
        }
    }
}
