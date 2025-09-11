# Dungeon Hunter - (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0

# New spells dictionary as a dict keyed by spell name
spells_dict_raw = {
    "Fireball": {
        "name": "Fireball",
        "description": "A ball of fire that burns enemies.",
        "mana_cost": 10,
        "effect": {"burn_damage": 10}
    },
    "Greater Fireball": {
        "name": "Greater Fireball",
        "description": "A larger ball of fire that burns enemies more intensely.",
        "mana_cost": 20,
        "effect": {"burn_damage": 20}
    },
    "Ice Shard": {
        "name": "Ice Shard",
        "description": "Sharp shards of ice that pierce enemies.",
        "mana_cost": 8,
        "effect": {"freeze": 8}
    },
    "Greater Ice Shard": {
        "name": "Greater Ice Shard",
        "description": "Larger shards of ice that pierce enemies deeply.",
        "mana_cost": 16,
        "effect": {"freeze": 16}
    },
    "Healing Light": {
        "name": "Healing Light",
        "description": "A warm light that heals allies.",
        "mana_cost": 12,
        "effect": {"heal": 12}
    },
    "Greater Healing Light": {
        "name": "Greater Healing Light",
        "description": "A powerful light that heals allies significantly.",
        "mana_cost": 24,
        "effect": {"heal": 24}
    },
    "Lightning Bolt": {
        "name": "Lightning Bolt",
        "description": "A bolt of lightning that shocks enemies.",
        "mana_cost": 15,
        "effect": {"shock": 15}
    },
    "Greater Lightning Bolt": {
        "name": "Greater Lightning Bolt",
        "description": "A stronger bolt of lightning that shocks enemies severely.",
        "mana_cost": 30,
        "effect": {"shock": 30}
    },
    "Arcane Shield": {
        "name": "Arcane Shield",
        "description": "A magical shield that absorbs damage.",
        "mana_cost": 20,
        "effect": {"shield": 20}
    },
    "Greater Arcane Shield": {
        "name": "Greater Arcane Shield",
        "description": "A powerful magical shield that absorbs more damage.",
        "mana_cost": 40,
        "effect": {"shield": 40}
    },
    "Earthquake": {
        "name": "Earthquake",
        "description": "A powerful tremor that damages all enemies.",
        "mana_cost": 25,
        "effect": {"area_damage": 25}
    },
    "Wind Gust": {
        "name": "Wind Gust",
        "description": "A gust of wind that pushes enemies back.",
        "mana_cost": 7,
        "effect": {"knockback": 7}
    },
    "Shadow Bind": {
        "name": "Shadow Bind",
        "description": "Binds the target in shadows, immobilizing them.",
        "mana_cost": 18,
        "effect": {"immobilize": 18}
    },
    "Holy Smite": {
        "name": "Holy Smite",
        "description": "A holy attack that damages undead enemies.",
        "mana_cost": 22,
        "effect": {"holy_damage": 22}
    },
    "Mana Drain": {
        "name": "Mana Drain",
        "description": "Drains mana from the target and restores caster's mana.",
        "mana_cost": 14,
        "effect": {"mana_drain": 14}
    }
}

