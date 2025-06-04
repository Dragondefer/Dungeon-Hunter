__version__ = "82.0"
__creation__ = "13-03-2025"

from datetime import datetime
import time

from interface.colors import Colors

"""
╔════════════════════════════════════════════╗
║           ⚠️ SPOILER WARNING ⚠️           ║
╠════════════════════════════════════════════╣
║ This file contains major story spoilers,   ║
║ hidden achievements, secret endings, and   ║
║ other surprise content.                    ║
║                                            ║
║ Proceed only if you are a developer or     ║
║ have completed the game.                   ║
╚════════════════════════════════════════════╝
Note: game is not finished, and will contain differents endings
"""


from engine.game_utility import typewriter_effect
def display_title():
    title = """
██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
                                                               
██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗            
██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗           
███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝           
██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗           
██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║           
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝           
        """
    print(Colors.gradient_text(title, (0, 175, 75), (30, 125, 125)))
    print(f"{Colors.CYAN}A text-based dungeon exploration RPG game\nWhere you explore a dangerous dungeon{Colors.RESET}")
    # print(f"{Colors.YELLOW}Created on {datetime.now().strftime('%Y-%m-%d')}{Colors.RESET}")
    print()


# --------------------------------------------------
#   !!!   FOLLOWING CONTENT IS SPOILER HEAVY   !!!
# --------------------------------------------------



def display_intro(): # Generic text, it's not part of the lore
        story = [
            "In the remote village of Eldridge, rumors speak of an ancient dungeon filled with unimaginable treasures.",
            "As a treasure hunter, you've spent years searching for this legendary place.",
            "Finally, your journey has led you to its entrance - a dark cavern nestled between towering mountains.",
            "Armed with your wits and courage, you step into the darkness...",
            "Welcome to Treasure Hunter's Gambit, where your luck and choices determine your fate."
        ]
        
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}The Legend Begins...{Colors.RESET}")
        for line in story:
            typewriter_effect(f"{Colors.CYAN}{line}{Colors.RESET}", 0.02)
            time.sleep(0.5)
        
        input(f"\n{Colors.YELLOW}Press Enter to begin your adventure...{Colors.RESET}")


LORE_EVENT = {
    "ancient_ruins": "Des inscriptions anciennes racontent l'histoire d'un roi maudit...",
    "blood_moon": "Une lune rouge brille... quelque chose d'étrange va arriver...",
    "lost_sword": "La légende parle d'une épée disparue depuis 1000 ans..."
}


WELCOME_MESSAGES = [
    "If you see this, the game has chosen you.",
    "Remember: The game is alive. It knows.",
    "The game knows your name.",
    "The shadows are alive. They remember."
]

WARNING_MESSAGES = [
    "The shadows whisper in the code... do you hear them?",
    "#$%&*@!~ mysterious symbols appear and vanish...",
    "Beware the dungeon's secret... it watches.",
    "Something is not right here... or is it?",
    "You shouldn't be here. The game doesn't like visitors.",
    "They watch from the shadows, waiting for the next move.",
    "Whispers echo: \"Turn back... or be lost forever.\"",
    "Some lines of code should never be read aloud."
]

DREAD_MESSAGES = [
    "The final boss is watching you... or maybe not.",
    "The final boss is not a boss. It's a watcher.",
    "You are not the player. You are the prey.",
    "End of line... or just the beginning?",
    "End of file... or the end of you?",
    "The last save was a lie.",
    "Your save is a lie; your progress, a trap.",
    "The dungeon remembers your sins.",
    "The dungeon's curse is written in broken bytes.",
    "The dungeon's heart beats with a dark secret.",
    "The dungeon's heart pulses with malevolent intent.",
    "The walls bleed code, and the silence screams.",
    "The silence is broken by screams only you can hear.",
    "Corrupted data bleeds from forgotten realms.",
    "The code fractures, revealing the abyss beneath.",
    "Shadows crawl between the lines, waiting to consume.",
    "Glitches in the matrix... or is it a curse?",
    "Beware the forgotten bug that never dies.",
    "Beware the glitch that whispers your name.",
    "Error 666: Soul not found. Retry?",
    "Error 404: Sanity not found.",
    "The game remembers every mistake you made.",
    "The darkness is alive, and it hungers for your soul.",
    "The game breathes... and it hungers.",
    "You are trapped in a loop of endless despair.",
    "The corrupted code is rewriting your fate.",
    "Every step you take echoes in the void.",
    "The shadows bleed secrets no one should know.",
    "Your actions are watched by unseen eyes.",
    "The game is a labyrinth with no exit.",
    "The final boss waits beyond the veil of reality.",
    "The corruption spreads like a virus in your mind.",
    "The dungeon is a mirror reflecting your darkest fears.",
    "The code is alive, and it is angry.",
    "You cannot escape the whispers in the dark.",
    "The game is watching. Always watching.",
    "The end is only the beginning of your nightmare.",
    "The final boss is a ghost in the machine.",
    "The dungeon's curse is written in broken bytes.",
    "You are trapped in a loop of endless despair.",
    "The corrupted code is rewriting your fate.",
    "The dungeon's heart pulses with malevolent intent.",
    "Every step you take echoes in the void.",
    "The shadows bleed secrets no one should know.",
    "Your actions are watched by unseen eyes.",
    "The game is a labyrinth with no exit.",
    "The final boss waits beyond the veil of reality.",
    "The corruption spreads like a virus in your mind.",
    "The dungeon is a mirror reflecting your darkest fears.",
    "The code is alive, and it is angry.",
    "You cannot escape the whispers in the dark.",
    "The game is watching. Always watching.",
    "The end is only the beginning of your nightmare."
]

FINAL_MESSAGES = [
    "End of file... or the end of you?",
    "End of line... or just the beginning?",
    "The end is only the beginning of your nightmare."
]







"""
╔════════════════════════════════════════════╗
║      ✅ END OF SPOILER CONTENT ✅         ║
╠════════════════════════════════════════════╣
║ You have exited the spoiler section.       ║
║ It is now safe to resume reading.          ║
╚════════════════════════════════════════════╝
"""
