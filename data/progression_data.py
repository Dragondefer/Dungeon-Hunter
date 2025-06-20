from core.progression import Quest, Achievement, Event

# Player's quests
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

# Achievements
achievements = [
    Achievement("first_blood", "First Blood", "Kill an enemy.", lambda p: p.kills >= 1),
    Achievement("collector", "Collector", "Get 10 items.", lambda p: p.items_collected >= 10),
    Achievement("hoarder", "Trunk rat", "Get 1000 gold.", lambda p: p.gold >= 1000),
    Achievement("still_alive", "I'm still standing !", "Having 1% HP", lambda p: round((p.stats.hp/p.stats.max_hp), 2) <= 0.01),
    Achievement("treasure_hunter", "Treasure Hunter", "Find 10 treasures.", lambda p: p.treasures_found >= 10),
    Achievement("puzzle_solver", "Puzzle Solver", "Solve 5 puzzles.", lambda p: p.puzzles_solved >= 5),
    Achievement("explorer", "Explorer", "Explore 100 rooms.", lambda p: p.total_rooms_explored >= 100),
    Achievement("10_steps", "Ten Steps Forward... or is it?", "Reach level 10", lambda p: p.dungeon_level == 10)
]

# Events
def blood_moon_effect(player):
    player.stats.permanent_stats["attack"] += 5
    print("Une puissance obscure vous renforce... (ATK +5)")

def healing_waters(player):
    player.stats.permanent_stats["hp"] = player.stats.max_hp
    print("Les eaux guérissantes restaurent tous vos PV.")

EVENTS = [
    Event("Blood Moon", "Une lune rouge illumine la salle...", blood_moon_effect),
    Event("Healing Fountain", "Une fontaine magique vous soigne entièrement.", healing_waters),
    # Add more events here
]
