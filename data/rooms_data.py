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
        "a small vault with an ornate chest in the center",
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
