# Du​n​g​e​o​n​ ​H​u​n​t​e​r​ ​-​ ​(​c​)​ ​Dr​ag​o​nd​ef​er​ ​2​025
# L​ic​e​ns​ed​ ​un​de​r​ ​C​C ​B​Y​-​N​C​ 4​.​0

from sys import path as sys_path
from os.path import abspath, dirname

# Add the project root directory to sys.path to fix module import issues on Android/Termux
project_root = abspath(dirname(__file__))
if project_root not in sys_path:
    sys_path.insert(0, project_root)

__version__ = "856.0"
__creation__ = "09-03-2025"

import os
import time

from interface.colors import Colors
from engine.game_utility import (clear_screen, collect_feedback, maximize_terminal, get_input, strip_ansi)
from engine.logger import logger
from core.entity import continue_game
from core.story import display_title
from engine.save_system import SaveManager


# Note: You need to be at least beta tester to get the dev tools (as it can easley break everything and also spoil)
# Look at the game's discord for more info: https://discord.gg/3V7xGCvxEP
from config import set_dev_mode, is_dev_mode, setup_ai, agent_is_enabled, get_agent, aw
try:
    if os.path.exists("./engine/dev_mod.py"):
        from engine.dev_mod import debug_menu
        set_dev_mode(True)
        if is_dev_mode():
            logger.info("Developer mode enabled.")
except Exception as e:
    logger.warning(f"Error when trying to import dev_mod.py: {e}")
    dev_mode = False
    debug_menu = lambda *args, **kwargs: None

dev_mode = is_dev_mode()

maximize_terminal()

logger.info(f"dev_mode: {dev_mode}")
debug = 0

from engine.game_utility import set_game_speed_multiplier

# AI dev integration
try:
    if os.path.exists("./ai/agent.py") and os.path.exists("./ai/agent_wrapper.py"):
        print("AI agent detected. Would you like to enable AI agent to play? (y/N): ", end="")
        choice = input().lower()
        if debug>=1: print(f"AI agent choice: {choice}")
        setup_ai(choice)
        if choice == "y":
            set_game_speed_multiplier(0)
            if debug>=1: print(f"Enabling AI agent...")
            logger.info("AI enabled by user choice.")
        else:
            if debug>=1: print(f"Disabling AI agent...")
            logger.info("AI agent disabled by user choice.")
    else:
        logger.info("AI agent disabled because ai file not found.")
except Exception as e:
    logger.warning(f"Error while trying to import AI agent: {e}")

def main(continue_game=False, loaded_player=None):
    """Main entry point for the game. Instantiates and runs DungeonMode."""
    from engine.gamemodes import DungeonMode
    
    clear_screen()
    game_mode = DungeonMode(continue_game=continue_game, loaded_player=loaded_player, dev_mode=dev_mode, debug=debug)
    game_mode.run()

# Du​ng​e​o​n​ ​H​u​n​t​e​r​ ​-​ ​(​c​)​ ​Drag​o​nd​efer​ 2​025
# Lic​e​ns​ed​ ​un​der​ ​C​C ​B​Y​-​N​C​ 4​.​0

if __name__ == '__main__':
    input()
    player = None
    def main_menu():
        manager = SaveManager()
        while True:
            clear_screen()
            display_title()
            saves = manager.list_saves()
            options = []
            if saves:
                options.append((f"{Colors.BRIGHT_CYAN}Continue{Colors.RESET}", "continue"))
            options.append((f"{Colors.BRIGHT_GREEN}New Game{Colors.RESET}", "new_game"))
            options.append((f"{Colors.BRIGHT_RED}Quit Game{Colors.RESET}", "quit"))
            # Calculate box width based on longest option text and title length
            option_texts = [f"{idx}. {text}" for idx, (text, _) in enumerate(options, 1)]
            
            # Function to strip ANSI escape sequences for accurate length calculation
            import re
            ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
            def strip_ansi(text):
                return ansi_escape.sub('', text)
            
            # Define gold color using RGB ANSI escape sequence
            # GOLD = '\033[38;2;255;215;0m'
            
            # D​u​n​g​eo​n​ H​u​n​t​e​r ​-​ ​(​c​)​ ​Dr​a​g​o​n​de​f​e​r​ 2​0​2​5
            # L​i​ce​n​s​e​d​ u​n​de​r​ ​C​C​-​BY​-​N​C​ ​4.​0

            # Calculate box width as max of title length and longest option text plus padding
            box_title = " MAIN MENU "
            title_len = len(box_title)
            max_option_len = max(len(strip_ansi(text)) for text in option_texts)
            padding_horizontal = 12
            box_inner_width = max(title_len, max_option_len) + padding_horizontal * 2
            box_width = box_inner_width + 2  # for border chars
            
            # Calculate left and right padding for title centering
            left_padding = (box_inner_width - title_len) // 2
            right_padding = box_inner_width - title_len - left_padding
            
            # Print top border with title
            print(f"{Colors.YELLOW}╔{'═' * left_padding}{Colors.BLUE}{box_title}{Colors.YELLOW}{'═' * right_padding}╗{Colors.RESET}")
            
            # Print empty line for padding
            print(f"{Colors.YELLOW}║{' ' * box_inner_width}║{Colors.RESET}")
            
            # Print options inside box centered horizontally
            for idx, (text, _) in enumerate(options, 1):
                line = f"{idx}. {text}"
                line_len = len(strip_ansi(line))
                left_pad = (box_inner_width - line_len) // 2
                right_pad = box_inner_width - line_len - left_pad
                print(f"{Colors.YELLOW}║{Colors.RESET}{' ' * left_pad}{line}{' ' * right_pad}{Colors.YELLOW}║{Colors.RESET}")
            
            # Print empty line for padding
            print(f"{Colors.YELLOW}║{' ' * box_inner_width}║{Colors.RESET}")
            
            # Print bottom border (same length as top border)
            print(f"{Colors.YELLOW}╚{'═' * box_inner_width}╝{Colors.RESET}")
            
            choice = input(f"\n{Colors.BRIGHT_YELLOW}Select an option: {Colors.RESET}")
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    action = options[choice_num - 1][1]
                    if action == "continue":
                        try:
                            if not saves:
                                print(f"\n{Colors.BRIGHT_RED}No saved games found.{Colors.RESET}")
                                time.sleep(2)
                            else:
                                print(f"\n{Colors.BRIGHT_MAGENTA}Saved Games{Colors.RESET}\n")
                                # column width configuration
                                COL_FILE = 6
                                COL_NAME = 10
                                COL_LVL = 5
                                COL_FLOOR = 8
                                COL_DIFF = 10
                                COL_TIME = 6
                                COL_TYPE = 6

                                # print header with adjustable widths
                                header = (
                                    f"{'ID':>2} "
                                    f"{Colors.CYAN}{'File':<{COL_FILE}}{Colors.RESET} | "
                                    f"{Colors.CYAN}{'Name':<{COL_NAME}}{Colors.RESET} | "
                                    f"{Colors.GREEN}{'Lvl':<{COL_LVL}}{Colors.RESET} | "
                                    f"{Colors.YELLOW}{'Floor':<{COL_FLOOR}}{Colors.RESET} | "
                                    f"{Colors.MAGENTA}{'Diff':<{COL_DIFF}}{Colors.RESET} | "
                                    f"{Colors.BLUE}{'Time':<{COL_TIME}}{Colors.RESET} | "
                                    f"{Colors.RED}{'Type':<{COL_TYPE}}{Colors.RESET}"
                                )
                                print(header)
                                for idx, meta in enumerate(saves, 1):
                                    try:
                                        fname = meta.get('filename', '')[:COL_FILE]
                                        name = strip_ansi(meta.get('player_name', 'Unknown'))[:COL_NAME]
                                        level = f"Lv{meta.get('level', 1)}"[:COL_LVL]
                                        floor = meta.get('location', 'Dungeon Floor 1').replace('Dungeon Floor ', 'Floor ')[:COL_FLOOR]
                                        difficulty = str(meta.get('difficulty', 'Normal'))[:COL_DIFF]
                                        playtime_seconds = int(meta.get('playtime', 0))
                                        hours = playtime_seconds // 3600
                                        minutes = (playtime_seconds % 3600) // 60
                                        time_str = f"{hours}h{minutes:02d}" if hours > 0 else f"{minutes}m"
                                        time_str = time_str[:COL_TIME]
                                        save_type = meta.get('save_type', 'manual').upper()[:COL_TYPE]
                                        print(
                                            f"{idx:>2} "
                                            f"{fname:<{COL_FILE}} | "
                                            f"{name:<{COL_NAME}} | "
                                            f"{level:<{COL_LVL}} | "
                                            f"{floor:<{COL_FLOOR}} | "
                                            f"{difficulty:<{COL_DIFF}} | "
                                            f"{time_str:<{COL_TIME}} | "
                                            f"{save_type:<{COL_TYPE}}"
                                        )
                                    except Exception as e:
                                        logger.error(f"Error displaying save {idx}: {e}")
                                        # fallback show filename prefix if available
                                        fname = meta.get('filename', '')[:COL_FILE]
                                        print(f"{idx:>2} {fname:<{COL_FILE}} | <corrupt save>")
                                
                                save_choice = get_input(f"\n{Colors.BRIGHT_YELLOW}Choose a save file number to load or 'b' to go back: {Colors.RESET}")
                                if save_choice.lower() == 'b':
                                    continue
                                try:
                                    save_index = int(save_choice) - 1
                                    if 0 <= save_index < len(saves):
                                        filename = saves[save_index]['filename']
                                        save_data = manager.load_save(filename)
                                        if save_data and 'player_data' in save_data:
                                            from core.entity import Player
                                            player = Player.from_dict(save_data['player_data'])
                                            if player:
                                                main(continue_game=True, loaded_player=player)
                                            else:
                                                print(f"{Colors.RED}Failed to load save.{Colors.RESET}")
                                                time.sleep(2)
                                        else:
                                            print(f"{Colors.RED}Invalid save data.{Colors.RESET}")
                                            time.sleep(2)
                                    else:
                                        print(f"{Colors.RED}Invalid save selection. Please enter a number between 1 and {len(saves)}.{Colors.RESET}")
                                        time.sleep(2)
                                except ValueError:
                                    print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
                                    time.sleep(2)
                        except Exception as e:
                            logger.error(f"Error in continue action: {e}")
                            print(f"{Colors.RED}An error occurred while loading saves.{Colors.RESET}")
                            time.sleep(2)
                    elif action == "new_game":
                        main()
                    elif action == "quit":
                        print(f"{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}")
                        break
                else:
                    print(f"{Colors.BRIGHT_RED}Invalid choice. Please try again.{Colors.RESET}")
                    time.sleep(2)
            except ValueError:
                print(f"{Colors.BRIGHT_RED}Invalid input. Please enter a number.{Colors.RESET}")
                time.sleep(2)

    main_menu()
    
    collect_feedback()
    print(f"\n{Colors.CYAN}Thanks for playing Dungeon Hunter !{Colors.RESET}")
    print(f"{Colors.UNDERLINE}Made by {Colors.BOLD}Dragondefer{Colors.RESET}")
