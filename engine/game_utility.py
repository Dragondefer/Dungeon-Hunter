__version__ = "488.0"
__creation__ = "09-03-2025"

import os
import sys
import time
import random
import datetime
import traceback

# Define the root file of the game so it can import from other moduls such as the folder interface to get Colors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface.colors import Colors
from engine.logger import logger

# For Windows non-blocking key detection
if os.name == 'nt':
    import msvcrt
else:
    import select
    import termios
    import tty


def set_windows_terminal_size(cols=120, lines=40):
    os.system(f"mode con: cols={cols} lines={lines}")
    # Plein écran (Alt+Entrée simulation non fiable)

def set_unix_terminal_size(cols=120, rows=40):
    sys.stdout.write(f"\x1b[8;{rows};{cols}t")
    sys.stdout.flush()

import platform

def normalize_terminal(cols=210, lines=52):
    if platform.system() == "Windows":
        os.system(f"mode con: cols={cols} lines={lines}")
    else:
        sys.stdout.write("\x1b[8;40;120t")
        sys.stdout.flush()

import os
import uuid

USER_ID_FILE = os.path.expanduser("~/.dungeon_hunter_user_id")

def get_or_create_user_id():
    """
    Retrieves the persistent anonymous user ID from a local file.
    If the file does not exist, generates a new UUID, saves it, and returns it.
    """
    try:
        if os.path.exists(USER_ID_FILE):
            with open(USER_ID_FILE, "r") as f:
                user_id = f.read().strip()
                if user_id:
                    return user_id
        # If file does not exist or is empty, create a new user ID
        user_id = str(uuid.uuid4())
        with open(USER_ID_FILE, "w") as f:
            f.write(user_id)
        return user_id
    except Exception as e:
        # In case of any error, fallback to a new UUID without saving
        return str(uuid.uuid4())

def move_cursor(row, col):
    print(f"\x1b[{row};{col}H", end='')

def clear_line():
    print("\x1b[2K", end='')

import ctypes

def maximize_terminal():
    if platform.system() == "Windows":
        # Get console window handle
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            # SW_MAXIMIZE = 3
            ctypes.windll.user32.ShowWindow(hwnd, 3)

from shutil import get_terminal_size
cols, rows = get_terminal_size()


def strip_ansi(text):
    """Supprime les codes ANSI pour un calcul précis de longueur"""
    import re
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def execute_command(cmd, allowed=False, prnt=True, rtn=False, context=None):
    if context is None:
        context = {}
    try:
        result = eval(cmd, globals(), context)
        if prnt:
            time.sleep(0.1)
            print('>', cmd)
            time.sleep(0.1)
            print(result)
        if rtn is True:
            return result
        else:
            return True
    except Exception as e:
        print(f"{Colors.RED}Error occured: {e}{Colors.RESET}")
        return e


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


def timed_input(prompt, timeout, default=None):
    """
    Prompt the user for input, but timeout after a specified number of seconds.
    Displays a countdown timer alongside the prompt.

    Parameters:
    - prompt (str): The prompt message to display.
    - timeout (float): The number of seconds to wait for input before timing out.
    - default (str or None): The value to return if the timeout expires without input.

    Returns:
    - str: The user's input if entered within the timeout, otherwise the default value.
    """
    if os.name == 'nt':
        import msvcrt
        start_time = time.time()
        input_str = ''
        prompt_displayed = False
        while True:
            elapsed = time.time() - start_time
            remaining = max(0, int(timeout - elapsed))
            if not prompt_displayed:
                # Display prompt once
                sys.stdout.write(prompt)
                sys.stdout.flush()
                prompt_displayed = True
            # Clear the line and display timer and input string on the same line
            sys.stdout.write('\r\033[K')  # Clear line
            sys.stdout.write(f'{prompt} {Colors.RED}[{remaining}s]{Colors.RESET} ' + input_str + ' ')
            sys.stdout.flush()

            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if char == '\r':  # Enter key
                    #print()
                    return input_str
                elif char == '\b':  # Backspace
                    if len(input_str) > 0:
                        input_str = input_str[:-1]
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    input_str += char
            if elapsed > timeout:
                print()
                return default
            time.sleep(0.05)
    else:
        import select
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            input_str = ''
            start_time = time.time()
            prompt_displayed = False
            while True:
                elapsed = time.time() - start_time
                remaining = max(0, int(timeout - elapsed))
                if not prompt_displayed:
                    # Display prompt once
                    sys.stdout.write(prompt)
                    sys.stdout.flush()
                    prompt_displayed = True
                # Clear the line and display timer and input string on the same line
                sys.stdout.write('\r\033[K')  # Clear line
                sys.stdout.write(f'{prompt} [{remaining}s] ' + input_str + ' ')
                sys.stdout.flush()

                rlist, _, _ = select.select([sys.stdin], [], [], max(0, timeout - elapsed))
                if rlist:
                    char = sys.stdin.read(1)
                    if char == '\n':
                        print()
                        return input_str
                    elif char == '\x7f':  # Backspace
                        if len(input_str) > 0:
                            input_str = input_str[:-1]
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    else:
                        input_str += char
                else:
                    # Timeout expired
                    print()
                    return default
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# Game utility functions
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter_effect(text, delay=0.02, end="\n"):
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

ancient_map = {
    "A": "A̷̛͠", "B": "B̵̕͜", "C": "C̸̙̀", "D": "D̴̘͝", "E": "E̶͍̚", "F": "F̷̢̈́",
    "G": "G̵̨̽", "H": "H̸͇͊", "I": "I̴̡̛", "J": "J̶̧̈́", "K": "K̵̞͠", "L": "L̷̻̎",
    "M": "M̴̱̾", "N": "N̸̼̆", "O": "O̵͓͛", "P": "P̶̺̒", "Q": "Q̴̹̿", "R": "R̷̞͝",
    "S": "S̶̤̕", "T": "T̸̻̈́", "U": "U̴̲̚", "V": "V̵̰͊", "W": "W̸͕̆", "X": "X̵̩̀",
    "Y": "Y̴̙͝", "Z": "Z̶̢͌",
    "a": "ä̷̪́", "b": "b̸̼̅", "c": "c̴̱͝", "d": "ď̶̙", "e": "ë̵͕́", "f": "f̷̠͑",
    "g": "g̸̻̿", "h": "h̵̤͒", "i": "i̴̊͜", "j": "j̶̩̈́", "k": "k̵̢͝", "l": "l̷̫̈́",
    "m": "m̴̛̠", "n": "n̸̻̈́", "o": "o̶͙͝", "p": "p̵̦̆", "q": "q̴̨͝", "r": "r̷͍̈́",
    "s": "s̸̱̅", "t": "ẗ̴̗́", "u": "ŭ̵͇", "v": "v̶̼͝", "w": "ẅ̷̙́", "x": "x̵̛̠",
    "y": "ÿ̸̡́", "z": "z̴͝ͅ",
    "0": "0̵̢̈́", "1": "1̸̘̓", "2": "2̴̙͝", "3": "3̶̢͌", "4": "4̷̫̈́", "5": "5̸̱̅",
    "6": "6̴̨͝", "7": "7̷͍̈́", "8": "8̸̱̅", "9": "9̴̗̈́",
    "@": "@̵͇̆", "#": "#̶̼͝", "€": "€̷̙̈́", "_": " ", "&": "&̵̛̠", "-": "-̸̡̈́",
    "+": "+̴͝ͅ", "(": "(̵̢̈́", ")": ")̸̘̓", "/": "/̴̙͝", "*": "*̶̢͌", "\"": "\"̷̫̈́",
    "\'": "\'̸̱̅", ":": ":̴̨͝", ";": ";̷͍̈́", "!": "!̸̱̅", "?": "?̴̗̈́",
    " ": " ", ".": ".̵͇̆", ",": ",̶̼͝",
    "~": "~̷̙̈́", "`": "`̵̛̠", "|": "|̸̡̈́", "•": "•̴͝ͅ", "√": "√̵̢̈́", "π": "π̸̘̓", 
    "÷": "÷̴̙͝", "×": "×̶̢͌", "§": "§̷̫̈́", "∆": "∆̸̱̅", "£": "£̴̨͝", "¥": "¥̷͍̈́", 
    "$": "$̸̱̅", "¢": "¢̴̗̈́", "^": "^̵͇̆", "°": "°̶̼͝", "=": "=̷̙̈́", "{": "{̵̛̠", 
    "}": "}̸̡̈́", "%": "%̴͝ͅ", "©": "©̵̢̈́", "®": "®̸̘̓", "™": "™̴̙͝", "✓": "✓̶̢͌",
    "[": "[̷̫̈́", "]": "]̸̱̅", "<": "<̴̨͝", ">": ">̷͍̈́"
}

def glitch_text(text: str) -> str:
    """Convertit un texte normal en version corrompue selon une table fixe."""
    return "".join([corruption_map.get(char, char) for char in text])

def ancient_text(text: str) -> str:
    """Converti un texte normal en une version lisible mais toujours corrompue"""
    return "".join([ancient_map.get(char, char) for char in text])

# random mix of glitch and ancient text
def random_glitch_text(text: str) -> str:
    """Convertit un texte normal en une version corrompue aléatoirement selon une table fixe."""
    return "".join([random.choice([corruption_map.get(char, char), ancient_map.get(char, char)]) for char in text])


"""def glitch_text(text):
    glitched = ''
    for char in text:
        if random.random() < 0.2:  # 20% de glitch
            glitched += f"\033[9{random.randint(1,7)}m{random.choice(['█', '░', '▒', '@', '#'])}\033[0m"
        else:
            glitched += char
    return glitched"""


def glitch_burst(text, duration=1):
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write('\033[2K\r')  # efface ligne
        sys.stdout.write(random_glitch_text(text))
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write('\033[2K\r' + text + '\n')


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


def loading(duration=4):
    """
    Improved loading animation displayed at the bottom right corner of the terminal.
    Animates a spinner with dots for the given duration in seconds.
    Adds a box around the loading text.
    """
    import sys
    import time
    from shutil import get_terminal_size

    spinner = ['|', '/', '-', '\\']
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        cols, rows = get_terminal_size()
        loading_text = f"{Colors.YELLOW}Loading{Colors.RESET} "
        spinner_char = spinner[int(elapsed * 10) % len(spinner)]
        dots_count = int((elapsed * 2) % 4)
        dots = '.' * dots_count + ' ' * (3 - dots_count)
        text = f"{loading_text}{spinner_char} {dots}"

        box_width = len(text)  # padding for box sides
        box_top = '┌' + '─' * box_width + '┐'
        box_bottom = '└' + '─' * box_width + '┘'
        box_middle = '│  ' + text + ' ' * 6 + ' │'

        # Calculate position: bottom row, right aligned
        x = cols - box_width - 1
        y = rows - 2  # box is 3 lines tall

        # Move cursor to position and print box
        sys.stdout.write(f"\033[s")  # Save cursor position

        # Print top border
        sys.stdout.write(f"\033[{y};{x}H{box_top}")
        # Print middle with text
        sys.stdout.write(f"\033[{y+1};{x}H{box_middle}")
        # Print bottom border
        sys.stdout.write(f"\033[{y+2};{x}H{box_bottom}")

        sys.stdout.write(f"\033[u")  # Restore cursor position
        sys.stdout.flush()

        time.sleep(0.1)

    # Clear the box after done
    clear_str = ' ' * (box_width + 2)
    sys.stdout.write(f"\033[s")
    for i in range(3):
        sys.stdout.write(f"\033[{y + i};{x}H{clear_str}")
    sys.stdout.write(f"\033[u")
    sys.stdout.flush()


def choose_difficulty(player):
    """
    Allows the player to select a difficulty mode with suspense effect.
    """
    logger.debug("Choosing difficulty mode...")
    from engine.difficulty import NormalMode, SoulsEnjoyerMode, RealisticMode
    try:
        player.save_difficulty_data()
    except AttributeError as AE:
        print(f"{Colors.RED}Attribute Error:", AE, Colors.RESET)
    except Exception as e:
        print(f"{Colors.RED}ERROR:", e, Colors.RESET)

    clear_screen()
    print(f"\n{Colors.YELLOW}{Colors.BOLD}CHOOSE YOUR DIFFICULTY MODE{Colors.RESET}")

    # Affichage des difficultés disponibles
    difficulties = {
        "1": ("normal".capitalize(), f"{Colors.GREEN}Y{Colors.RESET}" if player.finished_difficulties["normal"] else f"{Colors.RED}X{Colors.RESET}"),
        "2": ("soul Enjoyer".capitalize(), f"{Colors.GREEN}Y{Colors.RESET}" if player.finished_difficulties["soul_enjoyer"] else f"{Colors.RED}X{Colors.RESET}") if player.unlocked_difficulties["soul_enjoyer"] else ("", ""),
        "3": ("realistic".capitalize(), f"{Colors.GREEN}Y{Colors.RESET}" if player.finished_difficulties["realistic"] else f"{Colors.RED}X{Colors.RESET}") if player.unlocked_difficulties["realistic"] else ("", ""),
    }

    for key, (name, status) in difficulties.items():
        if name:  # Si la difficulté est débloquée, on l'affiche
            print(f"{Colors.CYAN}{key}. {name}{Colors.RESET} {status}")
        else:  # Sinon, on affiche une ligne vide pour le suspense
            print("")

    choice = input(f"{Colors.CYAN}Select your mode: {Colors.RESET}")
    while True:
        if choice in difficulties:
            break
        print(f"{Colors.RED}Mode locked or invalid choice! Defaulting to Normal.{Colors.RESET}")
        choice = input("Please retry: ")

    if choice == "1":
        player.mode = NormalMode()
    elif choice == "2" and player.unlocked_difficulties["soul_enjoyer"]:
        player.mode = SoulsEnjoyerMode()
    elif choice == "3" and player.unlocked_difficulties["realistic"]:
        player.mode = RealisticMode()
    else:
        print(f"{Colors.RED}Mode locked or invalid choice! Defaulting to Normal.{Colors.RESET}")
        player.mode = NormalMode()
        print(Colors.BLUE, 'Press enter to continue...', Colors.RESET, end="")
        input()

    logger.debug(f"Difficulty chosed: {player.mode}")  

    loading()

    return player.mode


def display_game_over():
    title = """

  ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ▒█████   ██▒   █▓▓█████  ██▀███   ▐██▌ 
 ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀    ▒██▒  ██▒▓██░   █▒▓█   ▀ ▓██ ▒ ██▒ ▐██▌ 
▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▒██░  ██▒ ▓██  █▒░▒███   ▓██ ░▄█ ▒ ▐██▌ 
░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▒██   ██░  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄   ▓██▒ 
░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ░ ████▓▒░   ▒▀█░  ░▒████▒░██▓ ▒██▒ ▒▄▄  
 ░▒   ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░   ░ ▒░▒░▒░    ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░ ░▀▀▒ 
  ░   ░   ▒   ▒▒ ░░  ░      ░ ░ ░  ░     ░ ▒ ▒░    ░ ░░   ░ ░  ░  ░▒ ░ ▒░ ░  ░ 
░ ░   ░   ░   ▒   ░      ░      ░      ░ ░ ░ ▒       ░░     ░     ░░   ░     ░ 
      ░       ░  ░       ░      ░  ░       ░ ░        ░     ░  ░   ░      ░    
                                                     ░                         
        """
    print(Colors.gradient_text(Colors.BOLD + title, (200, 0, 0), (255, 0, 50)), end="\n\n")

def game_over(describtion=None):
    clear_screen()
    if describtion:
        print(Colors.RED, describtion, Colors.RESET)
    display_game_over()
    logger.info(f"Game Over - {describtion}")
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

def handle_error():
    print(f"\n{Colors.RED}{Colors.BOLD}ERROR OCCURRED:\n{traceback.print_exc()}{Colors.RESET}")    
    logger.warning("Error Occurred")
    # save error debug into a log file (create a new file):
    with open("error.log", "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}\n\n")
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")

def collect_feedback(ask=True):
    """Collect player feedback about game experience"""
    logger.debug("Collecting feedback")
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
        f.write(f"\n[{feedback['timestamp']}]\n")

        f.write(f"Enjoyment: {feedback['enjoyment']}/10 | ")
        f.write(f"Difficulty: {feedback['difficulty']}/10 | ")
        f.write(f"Balance: {feedback['balance']}/10\n")
        if feedback['comments']:
            f.write(f"Comments: {feedback['comments']}\n")
        f.write("------------------------\n")
    print(f"{Colors.GREEN}Feedback file created successfully!{Colors.RESET}")
    logger.debug("FeedBack file created")
    print(f"{Colors.YELLOW}Please consider providing the created file \"feedback.txt\" in the game file to the {Colors.BOLD}discord channel: feedback (link in readme.md){Colors.RESET}")
    


def interactive_bar(min_value=0, max_value=100, default_value=50, allow_beyond=False, step=1, color=Colors.GREEN, length=40):
    """
    Display an interactive bar in the terminal that the user can adjust with arrow keys.

    Parameters:
    - min_value (int): Minimum boundary of the bar.
    - max_value (int): Maximum boundary of the bar.
    - default_value (int): Starting value of the bar.
    - allow_beyond (bool): If True, user can go beyond boundaries.
    - step (int): Step size for each arrow key press.
    - color (str): Color code for the bar display.
    - length (int): Length of the bar in characters.

    Returns:
    - int: The value selected by the user when Enter is pressed.
    """
    current_value = default_value

    def get_key():
        if os.name == 'nt':
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Special keys (arrows, f keys, ins, del, etc.)
                    key = msvcrt.getch()
                    return key
                else:
                    return key
            return None
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    key = sys.stdin.read(3)
                    return key
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    while True:
        # Calculate percentage for bar display
        if max_value != min_value:
            percent = (current_value - min_value) / (max_value - min_value)
        else:
            percent = 0
        filled_length = int(length * percent)
        empty_length = length - filled_length
        bar_str = color + ('█' * filled_length) + Colors.RESET + ('░' * empty_length)
        # Display bar with current value
        sys.stdout.write(f"\r[{bar_str}] {current_value}   ")
        sys.stdout.flush()

        key = get_key()
        if key is None:
            continue

        # Windows arrow keys
        if os.name == 'nt':
            if key == b'M':  # Right arrow
                new_value = current_value + step
                if not allow_beyond:
                    new_value = min(new_value, max_value)
                current_value = new_value
            elif key == b'K':  # Left arrow
                new_value = current_value - step
                if not allow_beyond:
                    new_value = max(new_value, min_value)
                current_value = new_value
            elif key == b'\r':  # Enter key
                print()
                return current_value
        else:
            # Unix arrow keys are escape sequences
            if key == '\x1b[C':  # Right arrow
                new_value = current_value + step
                if not allow_beyond:
                    new_value = min(new_value, max_value)
                current_value = new_value
            elif key == '\x1b[D':  # Left arrow
                new_value = current_value - step
                if not allow_beyond:
                    new_value = max(new_value, min_value)
                current_value = new_value
            elif key == '\r' or key == '\n':  # Enter key
                print()
                return current_value



if __name__ == '__main__':
    clear_screen()
    title = "GAME UTILITY TESTING"
    half_space = ' ' * (cols // 2 - len(title) // 2 - 1)
    print(f"\n{Colors.YELLOW}{Colors.BOLD}╔{'═' * (cols - 2)}╗")
    print(f"║{half_space}{title}{half_space}║")
    print(f"╚{'═' * (cols - 2)}╝{Colors.RESET}")
    while True:
        while (choice:=input(f"\n{Colors.CYAN}1. Glitch Text\n2. Ancient Text\n3. Random Glitch Text\n4. Burst Glitch\n5. Try Everything{Colors.RESET}\n\nYour choice: ")) not in ('1', '2', '3', '4', '5'):
            print('Invalid choice, please retry.')
        if choice == '1':
            print(glitch_text(input('Enter text to glitch: ')))
        elif choice == '2':
            print(ancient_text(input('Enter text to ancient: ')))
        elif choice == '3':
            print(random_glitch_text(input('Enter text to random glitch: ')))
        elif choice == '4':
            glitch_burst(input('Enter text to burst glitch: '))
        elif choice == '5':
            break
        else:
            print("DEBUG ERROR: Invalid choice", choice)

    import inspect
    wait_time = 0.5

    # List of test functions to run
    test_functions = [
        ('clear_screen', clear_screen, []),
        ('typewriter_effect', typewriter_effect, ['typewriter_effect']),
        ('dice_animation', dice_animation, []),
        ('progress_bar', progress_bar, [50, 100]),
        ('game_over', game_over, []),
        ('glitch_text', glitch_text, ['This is a test 123 ABC ù^*/']),
        ('ancient_text', ancient_text, ['This is a test 123 ABC ù^*/']),
        ('timed_input_pattern', timed_input_pattern, [1.0, 'bool', 0, 10]),
        ('interactive_bar', interactive_bar, [0, 100, 50, True, 1, Colors.GREEN, 40]),
        ('timed_input', timed_input, ['Enter something: ', 5, 'default']),
        ('collect_feedback', collect_feedback, [None, False]),
        ('random_glitch_text', random_glitch_text, ['This is a test 123 ABC ù^*/']),
        ('glitch_burst', glitch_burst, ['This is a test 123 ABC ù^*/']),
        ('choose_difficulty', choose_difficulty, [None]),
        ('handle_error', handle_error, []),
        ('logger.debug', logger.debug, ['Debug message']),
        ('logger.info', logger.info, ['Info message']),
        ('logger.warning', logger.warning, ['Warning message']),
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
        # Add a small delay between tests
        time.sleep(wait_time)