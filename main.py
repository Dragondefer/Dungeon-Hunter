import time
import os

from colors import Colors
from game_utility import clear_screen, game_over, choose_difficulty, handle_error, collect_feedback
from dungeon import generate_dungeon, debug_menu 
from entity import Player, continue_game
from quests import Quest
from story import display_title

def main(continue_game=False, loaded_player=None, debug=0):
    clear_screen()
    display_title()
    
    if continue_game == False:
        # Ask player for their name
        name = input(f"\n{Colors.CYAN}Enter your name, brave adventurer: {Colors.RESET}")
        player = Player(name if name else "Adventurer")
        choose_difficulty(player)
    elif continue_game and loaded_player is not None:
        player = loaded_player
    else:
        print(f'{Colors.RED} hein? continue_game != False & continue_game and loaded_player IS None')

    
    # Give player a starting quest
    starting_quest = Quest(
        "Dungeon Explorer", 
        "Explore 5 rooms in the dungeon", 
        "explore_rooms", 
        5, 
        50, 
        30
    )
    player.quests.append(starting_quest)
    
    # Main game loop
    game_running = True
    end = False
    dungeon = generate_dungeon(player=player)
    rooms_explored = 0
    
    while game_running and player.is_alive():
        clear_screen()

        player.display_dungeon_level(rooms_explored=rooms_explored)
       
        player.display_status()
        
        print(f"\n{Colors.YELLOW}What would you like to do?{Colors.RESET}")
        print(f"{Colors.CYAN}1. Explore a new room{Colors.RESET}")
        print(f"{Colors.GREEN}2. Check inventory{Colors.RESET}")
        print(f"{Colors.MAGENTA}3. View quests{Colors.RESET}")
        print(f"{Colors.RED}4. Rest (Recover 10 HP and 10 stamina){Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}5. Save game{Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}6. Quit game{Colors.RESET}")
        
        choice = input(f"\n{Colors.CYAN}Your choice: {Colors.RESET}")
        
        if choice == "1":  # Explore a new room
            if not dungeon:
                if debug >= 1:
                    print(Colors.BLUE, 'DEBUG: No dungeon, generating boss room', Colors.RESET)
                # Generate boss room at the end of the dungeon
                #boss_room = generate_random_room(player.dungeon_level, is_boss_room=True)
                #player_survived = boss_room.enter(player)
                
                if not player_survived or not player.is_alive():
                    game_over("died in battle")
                    game_running = False
                    end = True
                    continue
                
                print(f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You've cleared dungeon level {player.dungeon_level}!{Colors.RESET}")
                player.dungeon_level += 1
                if debug >= 1:
                    print(player.difficulty)
                    input()
                dungeon = generate_dungeon(player)
                rooms_explored = 0
                
                # Reward player for clearing a dungeon level
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
                room = dungeon.pop(0)
                player_survived = room.enter(player)
                rooms_explored += 1
                
                # Update quest progress if applicable
                for quest in player.quests:
                    if quest.objective_type == "explore_rooms" and not quest.completed:
                        if quest.update_progress():
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
        
        elif choice == "3":  # View quests
            player.view_quests()
        
        elif choice == "4":  # Rest
            rest_cost = 10
            if player.gold >= rest_cost:
                old_hp = player.stats.hp
                old_stamina = player.stats.stamina
                player.heal(10)
                player.rest_stamina(10)
                player.gold -= rest_cost
                print(f"\n{Colors.GREEN}You rest for a while and recover:\n{player.stats.hp - old_hp} HP,\n{player.stats.stamina - old_stamina} Stamina.{Colors.RESET}")
                print(f"{Colors.YELLOW}You spent {rest_cost} gold.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}You don't have enough gold to rest.{Colors.RESET}")
            
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "5":  # Save game
            # Ask the save name:
            save_name = input(f"\n{Colors.YELLOW}Enter a save name: {Colors.RESET}")
            player.save_player(save_name)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
        
        elif choice == "6":  # Quit game
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
    try:
        print('searching for saves')
        saves = [f for f in os.listdir() if f.endswith('.json')]
        if saves:
            print("Saved game found!")
            choice = input('Do you want to load the save ? (y/n)')
            if choice.lower() == "y":
                try:
                    print(f'Saves found:\n', saves)
                    save_name = input(f'Choose a name file:')
                    player = continue_game(save_name)

                    if player:  # Vérifie si le joueur est bien chargé
                        main(continue_game=True, loaded_player=player)
                    else:
                        print(f"{Colors.YELLOW}Starting new game instead...{Colors.RESET}")
                        time.sleep(2)
                        main()

                except Exception as e:
                    print(f"{Colors.RED}Error loading saved game: {e}{Colors.RESET}")
                    handle_error()
                    time.sleep(2)
                    main()
            else:
                main()
        else:
            main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.YELLOW}Game interrupted. Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error : {e}{Colors.RESET}")
        handle_error()
    
collect_feedback(player=player)
print(f"\n{Colors.CYAN}Thanks for playing Treasure Hunter !{Colors.RESET}")
print(f"{Colors.UNDERLINE}Made by {Colors.BOLD}Dragondefer{Colors.RESET}")
