__version__ = "476.0"
__creation__ = "09-03-2025"

import random
import time
import os

from colors import Colors
from game_utility import clear_screen, game_over, choose_difficulty, handle_error, collect_feedback, interactive_bar
from dungeon import Room, generate_dungeon, debug_menu 
from entity import Player, continue_game
from data import get_quests_dict
from story import display_title
from progression import Quest

debug = 0

def main(continue_game=False, loaded_player=None):
    global debug
    clear_screen()

    if continue_game == False:
        # Ask player for their name
        name = input(f"\n{Colors.CYAN}Enter your name, brave adventurer: {Colors.RESET}")
        player = Player(name if name else "Adventurer")
        choose_difficulty(player)
    elif continue_game and loaded_player is not None:
        player:Player = loaded_player
    else:
        print(f'{Colors.RED} hein? continue_game != False & continue_game and loaded_player IS None')

    
    # Give player a starting quest
    quests_dict = get_quests_dict()
    starting_quest = quests_dict.get("Dungeon Explorer")
    if starting_quest:
        player.quests.append(starting_quest)
    
    # Main game loop
    game_running = True
    end = False
    dungeon = generate_dungeon(player=player)
    rooms_explored = player.rooms_explored
    
    while game_running and player.is_alive():
        if debug >= 1:
            input()
        clear_screen()

        player.display_dungeon_level(rooms_explored=rooms_explored)
       
        player.display_status()
        
        print(f"\n{Colors.YELLOW}What would you like to do?{Colors.RESET}")
        print(f"{Colors.CYAN}1. Explore a new room{Colors.RESET}")
        print(f"{Colors.GREEN}2. Check inventory{Colors.RESET}")
        print(f"{Colors.RED}3. Rest{Colors.RESET}")
        print(f"{Colors.MAGENTA}4. View quests{Colors.RESET}")
        print(f"{Colors.BLUE}5. Display stats{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}6. Display success{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}7. Save game{Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}8. Quit game{Colors.RESET}\n")

        
        choice = input(f"{Colors.CYAN}Your choice: {Colors.RESET}")
        
        if choice == "1":  # Explore a new room
            if not dungeon:
                                
                if not player_survived or not player.is_alive():
                    game_over("died in battle")
                    game_running = False
                    end = True
                    continue
                
                print(f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You've cleared dungeon level {player.dungeon_level}!{Colors.RESET}")
                player.dungeon_level += 1

                # After finishing level 10 dungeon for the first time, 
                if player.dungeon_level == 11 and player.ng_plus[player.difficulty] == 0:
                    print(f"\n{Colors.BRIGHT_YELLOW}You have finished level 10 dungeon!{Colors.RESET}")
                    
                    # Unlock the two difficulty:
                    player.finished_difficulties["normal"] = True
                    player.unlocked_difficulties["soul_enjoyer"] = True
                    player.unlocked_difficulties["realistic"] = True

                    print(f"\n{Colors.BRIGHT_YELLOW}You can now change difficulty or start a new game + (NG+).{Colors.RESET}")
                    choice = input(f"\n{Colors.YELLOW}Do you want to change difficulty ? (y/n): {Colors.RESET}").lower()
                    if choice == "y":
                        print(f"\n{Colors.YELLOW}You can now choose a new difficulty level.{Colors.RESET}")
                        player.difficulty = choose_difficulty(player)
                        print(f"\n{Colors.YELLOW}You have chosen {player.difficulty} difficulty.{Colors.RESET}")
                    else:
                        print(f"\n{Colors.YELLOW}You have chosen to make a new game +.{Colors.RESET}")
                        print(f"\n{Colors.YELLOW}Generating a new dungeon...{Colors.RESET}")
                        time.sleep(2)
                        player.ng_plus[player.difficulty] += 1
                    player.dungeon_level = 1
                    player.rooms_explored = 0
                
                
                if debug >= 1:
                    print(Colors.BLUE, 'DEBUG: No dungeon, generating a new dungeon...', Colors.RESET)

                dungeon = generate_dungeon(player=player)
                
                # Update quest progress for complete_dungeon_levels
                for quest in player.quests:
                    if quest.objective_type == "complete_dungeon_levels" and not quest.completed:
                        if quest.update_progress():
                            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")

                if debug >= 1:
                    print(player.difficulty)
                
                # Reward player for clearing a dungeon level
                player.heal(player.stats.max_hp // 4)
                player.rest_stamina(100)
                player.regen_mana(25)
                level_reward = player.dungeon_level * 50
                print(f"{Colors.YELLOW}You receive {level_reward} gold for clearing the dungeon!{Colors.RESET}")
                player.gold += level_reward
                player.gain_xp(player.dungeon_level * 50)
                
                input(f"\n{Colors.YELLOW}Press Enter to continue to dungeon level {player.dungeon_level}...{Colors.RESET}")
            else:
                if debug >= 1:
                    print(f"{Colors.CYAN}DEBUG: Dungeon size before exploration: {len(dungeon)}{Colors.RESET}")
                room:Room = dungeon.pop(0)
                player_survived = room.enter(player)
                rooms_explored += 1
                
                # Update quest progress if applicable
                for quest in player.quests:
                    if quest.objective_type == "explore_rooms" and not quest.completed:
                        if quest.update_progress():
                            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
                    elif quest.objective_type == "collect_gold" and not quest.completed:
                        if player.gold >= quest.objective_amount:
                            quest.completed = True
                            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Quest Completed: {quest.title}!{Colors.RESET}")
                            print(f"{Colors.YELLOW}Rewards: {quest.reward_gold} gold, {quest.reward_xp} XP{Colors.RESET}")
                            player.gold += quest.reward_gold
                            player.gain_xp(quest.reward_xp)
                            
                            if quest.reward_item:
                                player.inventory.append(quest.reward_item)
                                print(f"{Colors.GREEN}You received: {quest.reward_item.name}{Colors.RESET}")
                            
                            player.quests.remove(quest)
                            player.completed_quests.append(quest)
                
                if not player_survived or not player.is_alive() and end == False:
                    game_over("died in battle")
                    game_running = False
                    end = True
                    continue
                
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "2":  # Check inventory
            player.manage_inventory()
        
        
        elif choice == "3":  # Rest
            amount = interactive_bar(0, 100, 10, False, 10, Colors.GREEN, 50)
            if player.gold >= amount:
                old_hp = player.stats.hp
                old_stamina = player.stats.stamina
                player.heal(amount)
                player.rest_stamina(amount)
                print(f"\n{Colors.GREEN}You rest for a while and recover:\n{player.stats.hp - old_hp} HP,\n{player.stats.stamina - old_stamina} Stamina.{Colors.RESET}")
                
                # Chance of being robbed by a goblin:
                if player.difficulty == "Normal":
                    amount = random.randint(int(amount * 0.8), int(amount * 1.2))
                else:
                    amount = random.randint(int(amount * 1), int(amount * 1.5))
                
                player.gold = max(0, player.gold - amount)
                if amount > 0:
                    print(f"\n{Colors.RED}A goblin stole {amount} gold while you were resting!{Colors.RESET}")
                # print(f"{Colors.YELLOW}You spent {amount} gold.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}You don't have enough gold to rest.{Colors.RESET}")
            
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        

        elif choice == "4":  # View quests
            player.view_quests()
        
        elif choice == "5":  # Display stats summary
            player.rooms_explored = rooms_explored
            player.display_stats_summary()
        
        elif choice == "6": # Display Achievement
            player.display_achievements()

        elif choice == "7":  # Save game
            # Save does not work for now
            # Ask the save name:
            save_name = input(f"\n{Colors.YELLOW}Enter a save name: {Colors.RESET}")
            player.save_player(save_name)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "8":  # Quit game
            confirm = input(f"{Colors.RED}Are you sure you want to quit? (y/n): {Colors.RESET}").lower()
            if confirm == "y":
                try:
                    player.save_player("auto_save")
                except Exception as e:
                    handle_error()
                    print(f"{Colors.RED}Error saving auto-save: {e}{Colors.RESET}")
                game_running = False
        
        elif choice == "dev": # activate dev debug test
            print(Colors.gradient_text('dev mode activated', (0, 0, 255), (0, 255, 0)))
            debug_menu(player, dungeon)
        
        elif choice == "stats":
            print(player.stats)
            input()
        
        else:
            print(f"{Colors.RED}Invalid choice. Try again.{Colors.RESET}")
            time.sleep(1)
    
    if not player.is_alive() and end == False:
        game_over("died in battle")
        end = True


if __name__ == '__main__':
    player = None
    def main_menu():
        while True:
            clear_screen()
            display_title()
            os.makedirs('./saves', exist_ok=True)
            saves = [f for f in os.listdir('./saves') if f.endswith('.json')]
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
                        print(f"\n{Colors.BRIGHT_MAGENTA}Saved games found:{Colors.RESET}\n")
                        for idx, save_file in enumerate(saves, 1):
                            print(f"{Colors.CYAN}{idx}. {save_file}{Colors.RESET}")
                        save_choice = input(f"\n{Colors.BRIGHT_YELLOW}Choose a save file number to load or 'b' to go back: {Colors.RESET}")
                        if save_choice.lower() == 'b':
                            continue
                        try:
                            save_index = int(save_choice) - 1
                            if 0 <= save_index < len(saves):
                                player = continue_game(saves[save_index])
                                if player:
                                    main(continue_game=True, loaded_player=player)
                                else:
                                    print(f"{Colors.YELLOW}Failed to load save. Starting new game...{Colors.RESET}")
                                    time.sleep(2)
                                    main()
                            else:
                                print(f"{Colors.RED}Invalid save selection.{Colors.RESET}")
                                time.sleep(2)
                        except ValueError:
                            print(f"{Colors.RED}Invalid input.{Colors.RESET}")
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
    
collect_feedback(player=player)
print(f"\n{Colors.CYAN}Thanks for playing Dungeon Hunter !{Colors.RESET}")
print(f"{Colors.UNDERLINE}Made by {Colors.BOLD}Dragondefer{Colors.RESET}")
