import os
import sys
import time
import random
import datetime
import traceback

from colors import Colors

# Game utility functions
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter_effect(text, delay=0.02, end=None):
    """Affiche du texte avec un effet de machine à écrire sans retour à la ligne forcé."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if end:
        sys.stdout.write(end)
    sys.stdout.flush()

# Table de correspondance des caractères corrompus
corruption_map = {
    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F",
    "G": "G", "H": "H", "I": "I", "J": "J", "K": "K", "L": "L",
    "M": "M", "N": "N", "O": "O", "P": "P", "Q": "Q", "R": "R",
    "S": "S", "T": "T", "U": "U", "V": "V", "W": "W", "X": "X",
    "Y": "Y", "Z": "Z",
    "a": "▒", "b": "␉", "c": "␌", "d": "␍", "e": "␊", "f": "°",
    "g": "±", "h": "█", "i": "␋", "j": "┘", "k": "┐", "l": "┌",
    "m": "└", "n": "┼", "o": "⎺", "p": "⎻", "q": "─", "r": "⎼",
    "s": "⎽", "t": "├", "u": "┤", "v": "┴", "w": "┬", "x": "│",
    "y": "≤", "z": "≥",
    "0": "█", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5",
    "6": "6", "7": "7", "8": "8", "9": "9",
    "@": "@", "#": "#", "€": "€", "_": " ", "&": "&", "-": "▲",
    "+": "▶", "(": "(", ")": ")", "/": "/", "*": "*", "\"": "\"",
    "\'": "\'", ":": ":", ";": ";", "!": "!", "?": "?",
    " ": " ", ".": "▼", ",": "◀",
    "~": "•", "`": "⬥", "|": "≠", "•": "•", "√": "√", "π": "π", "÷": "÷",
    "×": "×", "§": "§", "∆": "∆", "£": "£", "¥": "¥", "$": "$",
    "¢": "¢", "^": "^", "°": "°", "=": "=", "{": "π", "}": "£", "%": "%", "©": "©",
    "®": "®", "™": "™", "✓": "✓", "[": "[", "]": "]", "<": "<", ">": ">"
}

def glitch_text(text):
    """Convertit un texte normal en version corrompue selon une table fixe."""
    return "".join(corruption_map.get(char, char) for char in text)


def dice_animation(sides=6, rolls=10, delay=0.1):
    for i in range(rolls):
        clear_screen()
        value = random.randint(1, sides)
        if sides == 6:
            display_dice(value)
        else:
            print(f"\n  {Colors.YELLOW}{Colors.BOLD}Rolling d{sides}...{Colors.RESET}")
            print(f"\n  {Colors.CYAN}{Colors.BOLD}[ {value} ]{Colors.RESET}")
        time.sleep(delay)
    return value

def display_dice(value):
    dice = [
        ["┌───────┐",
         "│       │",
         "│   •   │",
         "│       │",
         "└───────┘"],
        
        ["┌───────┐",
         "│ •     │",
         "│       │",
         "│     • │",
         "└───────┘"],
        
        ["┌───────┐",
         "│ •     │",
         "│   •   │",
         "│     • │",
         "└───────┘"],
        
        ["┌───────┐",
         "│ •   • │",
         "│       │",
         "│ •   • │",
         "└───────┘"],
        
        ["┌───────┐",
         "│ •   • │",
         "│   •   │",
         "│ •   • │",
         "└───────┘"],
        
        ["┌───────┐",
         "│ •   • │",
         "│ •   • │",
         "│ •   • │",
         "└───────┘"]
    ]
    
    for line in dice[value-1]:
        print(f"  {Colors.CYAN}{line}{Colors.RESET}")

def progress_bar(current, total, length=40, fill='█', empty='░'):
    percent = current / total
    filled_length = int(length * percent)
    bar = fill * filled_length + empty * (length - filled_length)
    return f"{Colors.GREEN}{bar}{Colors.RESET} {Colors.YELLOW}{int(100 * percent)}%{Colors.RESET}"

def choose_difficulty(player):
    """
    Allows the player to select a difficulty mode with suspense effect.
    """
    clear_screen()
    print(f"\n{Colors.YELLOW}{Colors.BOLD}CHOOSE YOUR DIFFICULTY MODE{Colors.RESET}")

    # Affichage des difficultés disponibles
    difficulties = {
        "1": ("normal".capitalize(), "✓" if player.finished_difficulties["normal"] else ""),
        "2": ("soul Enjoyer".capitalize(), "✓" if player.finished_difficulties["soul_enjoyer"] else "") if player.unlocked_difficulties["soul_enjoyer"] else ("", ""),
        "3": ("realistic".capitalize(), "✓" if player.finished_difficulties["realistic"] else "") if player.unlocked_difficulties["realistic"] else ("", ""),
    }

    for key, (name, status) in difficulties.items():
        if name:  # Si la difficulté est débloquée, on l'affiche
            print(f"{Colors.CYAN}{key}. {name}{Colors.RESET} {status}")
        else:  # Sinon, on affiche une ligne vide pour le suspense
            print("")

    choice = input(f"{Colors.CYAN}Select your mode: {Colors.RESET}")

    if choice == "1":
        player.difficulty = "normal"
    elif choice == "2" and player.unlocked_difficulties["soul_enjoyer"]:
        player.difficulty = "noul_enjoyer"
    elif choice == "3" and player.unlocked_difficulties["realistic"]:
        player.difficulty = "realistic"
    else:
        print(f"{Colors.RED}Mode locked or invalid choice! Defaulting to Normal.{Colors.RESET}")
        player.difficulty = "normal"
        print(Colors.BLUE, 'Press enter to continue...', Colors.RESET, end="")
        input()


def game_over(describtion=None):
    if describtion:
        print(Colors.RED, describtion, Colors.RESET)
    print(f"\n{Colors.RED}{Colors.BOLD}GAME OVER!{Colors.RESET}")
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

def handle_error():
    print(f"\n{Colors.RED}{Colors.BOLD}ERROR OCCURRED:\n{traceback.print_exc()}{Colors.RESET}")    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
    # save error debug into a log file (create a new file):
    with open("error.log", "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}\n\n")

def collect_feedback(player=None, ask=True):
    """Collect player feedback about game experience"""
    if ask == False:
        return
    if input(f'{Colors.YELLOW}Do you want to send a quick feedback ? It would really help (y/n) : {Colors.RESET}') != "y":
        return
    
    clear_screen()
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════╗")
    print(f"║         GAME FEEDBACK QUESTIONNAIRE      ║")
    print(f"╚══════════════════════════════════════════╝{Colors.RESET}")
    
    feedback = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'enjoyment': input(f"\n{Colors.YELLOW}How much did you enjoy the game? (1-10): {Colors.RESET}"),
        'difficulty': input(f"{Colors.YELLOW}How challenging was the game? (1-10): {Colors.RESET}"),
        'balance': input(f"{Colors.YELLOW}How balanced were enemies/drops? (1-10): {Colors.RESET}"),
        'comments': input(f"{Colors.YELLOW}Any specific feedback? (optional): {Colors.RESET}")
    }
    
    # Save feedback to file
    with open("feedback.txt", "a") as f:
        f.write(f"\n[{feedback['timestamp']}]")
        if player:
            f.write(f" Player: {player.name} | Level: {player.dungeon_level} | Gold: {player.gold}\n")
        else:
            f.write("\n")
        f.write(f"Enjoyment: {feedback['enjoyment']}/10 | ")
        f.write(f"Difficulty: {feedback['difficulty']}/10 | ")
        f.write(f"Balance: {feedback['balance']}/10\n")
        if feedback['comments']:
            f.write(f"Comments: {feedback['comments']}\n")
        f.write("------------------------\n")


if __name__ == '__main__':
    print('clear_screen:')
    time.sleep(0.5)
    clear_screen()
    time.sleep(0.5)
    print('typewriter_effect:')
    time.sleep(0.5)
    typewriter_effect('typewriter_effect')
    time.sleep(0.5)
    print('\ndice_animation:')
    time.sleep(0.5)
    dice_animation()
    time.sleep(0.5)
    print('progress_bar')
    time.sleep(0.5)
    print(progress_bar(50, 100))
    time.sleep(0.5)
    game_over()
    time.sleep(0.5)
    print(glitch_text('Test'))
