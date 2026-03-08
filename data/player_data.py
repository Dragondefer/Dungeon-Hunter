# Dungeon Hunter - (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0

import random
from interface.colors import Colors
from core.player_class import PlayerClass

send_analytics:bool = False

def change_analytics(state:bool) -> bool:
    global send_analytics
    send_analytics = state
    return send_analytics

def can_send_analytics() -> bool:
    return send_analytics

# Random names for player
def get_random_names():
    player_name_list = [
        "Adventurer",
        f"{Colors.BRIGHT_BLACK}Dragondefer{Colors.RESET}",
        f"{Colors.BRIGHT_BLACK}Grim{Colors.RESET}",
    ]
    # Add weights
    player_name_weights = [0.9, 0.05, 0.05]
    player_name = random.choices(player_name_list, weights=player_name_weights, k=1)[0]
    return player_name

unlockable_classes = {
    5: [
        PlayerClass("Warrior", {"max_hp": 30, "attack": 5, "defense": 8, "agility": 3}, "Berserk Rage"),
        PlayerClass("Archer", {"max_hp": 15, "attack": 8, "defense": 3, "agility": 8}, "Shadow Strike"),
        PlayerClass("Mage", {"max_hp": 10, "attack": 10, "defense": 0, "agility": 2}, "Arcane Blast"),
        PlayerClass("Knight", {"max_hp": 25, "attack": 3, "defense": 10, "agility": 5}, "Divine Shield")
    ],
    10: [
        PlayerClass("Warrior", {"max_hp": 30, "attack": 5, "defense": 8, "agility": 3}, "Berserk Rage"),
        PlayerClass("Rogue", {"max_hp": 15, "attack": 8, "defense": 3, "agility": 8}, "Shadow Strike"),
        PlayerClass("Mage", {"max_hp": 10, "attack": 10, "defense": 0, "agility": 2}, "Arcane Blast"),
        PlayerClass("Knight", {"max_hp": 25, "attack": 3, "defense": 10, "agility": 5}, "Divine Shield")
    ]
}

