import os
import sys
import time
import random
import datetime
import traceback

from colors import Colors

# For Windows non-blocking key detection
if os.name == 'nt':
    import msvcrt
else:
    import select
    import termios
    import tty

def timed_input_pattern(difficulty=1.0, return_type='bool', peak_int_min=0, peak_int_max=10):
    """
    Animates a pattern in the terminal and waits for the user to press Enter at the right moment.

    Parameters:
    - difficulty (float): Controls the speed and number of animation steps. Higher is faster and fewer steps.
    - return_type (str): 'bool' to return True/False, 'int' to return a score based on timing.
    - peak_int_min (int): Minimum integer score if return_type is 'int'.
    - peak_int_max (int): Maximum integer score if return_type is 'int'.

    Returns:
    - bool or int: Depending on return_type.
      If 'bool': True if Enter pressed at or before right moment, else False.
      If 'int': Score proportional to timing, 0 if pressed after right moment or not pressed.
    """
    # Define the animation patterns from wide to narrow
    base_pattern = "O"
    max_padding = 5  # max spaces on each side at start
    steps = max(1, int(max_padding / difficulty))  # number of animation steps

    # Generate patterns list from widest to narrowest
    patterns = []
    for i in range(steps + 1):
        left_padding = max_padding - i
        right_padding = max_padding - i
        pattern = ">" * i + " " * left_padding + base_pattern + " " * right_padding + "<" * i
        patterns.append(pattern)

    # The "right moment" is the last pattern (index = steps)
    right_moment_index = steps

    # Function to check for Enter key press with timeout
    def check_enter(timeout):
        if os.name == 'nt':
            start_time = time.time()
            while time.time() - start_time < timeout:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\r':  # Enter key
                        return True
                    else:
                        # flush other keys
                        continue
                time.sleep(0.01)
            return False
        else:
            # Unix-like system
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    char = sys.stdin.read(1)
                    if char == '\n':
                        return True
                return False
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Animation loop
    for idx, pattern in enumerate(patterns):
        # Clear line and print pattern
        sys.stdout.write('\r' + pattern + ' ' * 10)
        sys.stdout.flush()

        # Wait for a short time and check for Enter key press
        # Total animation duration can be adjusted by difficulty
        step_duration = max(0.1, 0.5 / difficulty)
        if check_enter(step_duration):
            # If pressed before right moment
            if idx <= right_moment_index:
                if return_type == 'bool':
                    print()  # move to next line
                    return True
                else:
                    # Calculate score proportional to closeness to right moment
                    score_range = peak_int_max - peak_int_min
                    score = peak_int_min + int(score_range * (idx / right_moment_index))
                    print()
                    return score
            else:
                # Pressed after right moment
                if return_type == 'bool':
                    print()
                    return False
                else:
                    print()
                    return 0

    # If no key pressed during animation
    print()
    if return_type == 'bool':
        return False
    else:
        return 0

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
    import inspect

    wait_time = 0.5

    # List of test functions to run
    test_functions = [
        ('clear_screen', clear_screen, []),
        ('typewriter_effect', typewriter_effect, ['typewriter_effect']),
        ('dice_animation', dice_animation, []),
        ('progress_bar', progress_bar, [50, 100]),
        ('game_over', game_over, []),
        ('glitch_text', glitch_text, ['Test']),
        ('timed_input_pattern', timed_input_pattern, [1.0, 'bool', 0, 10]),
    ]

    for name, func, args in test_functions:
        print(f"\n--- Testing {name} ---")
        # If function returns a value, print it
        if inspect.isfunction(func):
            result = func(*args)
            # For functions that print internally and return None, skip printing result
            if result is not None:
                print(f"Result: {result}")
        else:
            print(f"{name} is not callable")
        time.sleep(wait_time)
