# This file was part of the dungeon.py so the __version__ and __creation__ is the same as dungeon.py
# Note: The use of the dev tools can easely break / spoil game

from interface.colors import Colors
from items.items import generate_random_item
from engine.logger import logger
from engine.dungeon import Dungeon, generate_dungeon, generate_enemy, generate_random_room
from engine.game_utility import handle_error, choose_difficulty
from core.entity import Player, load_player

def debug_menu(player: Player, dungeon: Dungeon):
    """
    Opens a debug menu to modify player stats, give items, change dungeon level, or test game mechanics.
    
    Parameters:
        player (Player): The current player instance.
        dungeon (Dungeon): The current dungeon instance.
    
    Options:
        1. Give Item
        2. Modify Player Stats
        3. Set Dungeon Level
        4. Teleport to Room
        5. Spawn Enemies in Current Room
        6. Instantly Complete a Quest
        7. Heal Player
        8. Save Game
        9. Load Game
        10. Choose Difficulty
        11. Reload Dungeon
        12. Give Armor Set
        0. Exit Debug Menu
    """

    while True:
        print(f"\n{Colors.MAGENTA}=== DEBUG MENU ==={Colors.RESET}")
        print(f"{Colors.YELLOW}1.{Colors.RESET} Give Item")
        print(f"{Colors.YELLOW}2.{Colors.RESET} Modify Player Stats")
        print(f"{Colors.YELLOW}3.{Colors.RESET} Set Dungeon Level")
        print(f"{Colors.YELLOW}4.{Colors.RESET} Teleport to Room")
        print(f"{Colors.YELLOW}5.{Colors.RESET} Spawn Enemies in Current Room")
        print(f"{Colors.YELLOW}6.{Colors.RESET} Instantly Complete a Quest")
        print(f"{Colors.YELLOW}7.{Colors.RESET} Heal Player")
        print(f"{Colors.YELLOW}8.{Colors.RESET} Save Game")
        print(f"{Colors.YELLOW}9.{Colors.RESET} Load Game")
        print(f"{Colors.YELLOW}10.{Colors.RESET} Choose difficulty")
        print(f"{Colors.YELLOW}11.{Colors.RESET} Reload dungeon")
        print(f"{Colors.YELLOW}12.{Colors.RESET} Give Armor Set")
        print(Colors.gradient_text("99.", (100, 0, 200), (200, 0, 100)), "Execute Python Command")
        print(f"{Colors.RED}0. Exit Debug Menu{Colors.RESET}")

        choice = input("\nEnter choice: ")
        logger.info(f"Debug Menu choice: {choice}")

        if choice == "1":
            try:
                # Give Item
                enemy_type = input(f"{Colors.CYAN}Enter enemy name (Goblin/Sqeleton/Wolf/Orc...): {Colors.RESET}")
                item_type = input(f"{Colors.CYAN}Enter item type (weapon/armor/potion/all): {Colors.RESET}").lower()
                rarity = input(f"{Colors.CYAN}Enter rarity (common/uncommon/rare/epic/legendary/divine/??? or 'random'): {Colors.RESET}").lower()
                item_name = input(f"{Colors.CYAN}Enter specific item name (or 'random' to pick a random one): {Colors.RESET}").title()
                rarity_boost = float(input(f"{Colors.CYAN}Enter rarity boost (1.0 = normal, higher = better items): {Colors.RESET}"))
                level_boost = int(input(f"{Colors.CYAN}Enter rarity boost (level = dungeon_level + level_boost) /!\\ HAS TO BE AN INT /!\\: {Colors.RESET}"))

                # Convert inputs to proper values
                item_type = None if item_type == "all" else item_type
                rarity = None if rarity == "random" else rarity
                item_name = None if item_name.lower() == "random" else item_name

                # Generate item with specified parameters
                item = generate_random_item(player=player, enemy_type=enemy_type.capitalize(), item_type=item_type, rarity=rarity, item_name=item_name, rarity_boost=rarity_boost, level_boost=level_boost)
                logger.info(f"Generated item: {item}")
            except ValueError as e:
                logger.warning(f"ValueError in give item input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
                item = None
            except Exception as e:
                logger.warning(f"Exception in give item input: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()
                item = None
            finally:
                if item:
                    player.inventory.append(item)
                    print(f"{Colors.GREEN}Added item: {item.name}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Failed to generate item! Check your input.{Colors.RESET}")

        elif choice == "2":
            try:
                # Modify Player Stats
                player.stats.permanent_stats["hp"] = int(input(f"{Colors.CYAN}Set HP: {Colors.RESET}") or player.stats.hp)
                player.stats.permanent_stats["max_hp"] = int(input(f"{Colors.CYAN}Set Max HP: {Colors.RESET}") or player.stats.max_hp)
                player.stats.permanent_stats["attack"] = int(input(f"{Colors.CYAN}Set Attack: {Colors.RESET}") or player.stats.attack)
                player.stats.permanent_stats["defense"] = int(input(f"{Colors.CYAN}Set Defense: {Colors.RESET}") or player.stats.defense)
                player.stats.permanent_stats["luck"] = int(input(f"{Colors.CYAN}Set Luck: {Colors.RESET}") or player.stats.luck)
                player.xp = int(input(f"{Colors.CYAN}Set XP: {Colors.RESET}") or player.xp)
                player.gold = int(input(f"{Colors.CYAN}Set Gold: {Colors.RESET}") or player.gold)
                for i in range(int(input(f"{Colors.CYAN}Set Level: {Colors.RESET}") or 0)):
                    player.level_up()
                logger.info(f"Modified player stats: {player.stats}")
                print(f"{Colors.GREEN}Player stats updated!{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in modify player stats input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()

        elif choice == "3":
            try:
                # Set Dungeon Level
                new_level = int(input(f"{Colors.CYAN}Set new dungeon level: {Colors.RESET}"))
                player.dungeon_level = new_level
                print(f"{Colors.GREEN}Dungeon level set to {new_level}{Colors.RESET}")
                logger.info(f"Set dungeon level to {new_level}")
            except ValueError as e:
                logger.warning(f"ValueError in set dungeon level input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
                handle_error()
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")
                handle_error()

        elif choice == "4":
            if input('Generate or Teleport ? (G/T)').upper() == "G":
                try:
                    lvl = int(input('Level room: '))
                except ValueError as e:
                    logger.warning(f"ValueError in teleport input: {e}")
                    print('Invalid input')
                    continue
                except TypeError as e:
                    logger.warning(f"TypeError in teleport input: {e}")
                    print('Invalid input')
                    continue
                rtype = input('Room type ("combat", "treasure", "shop", "rest", "puzzle", "inter_level"): ') or None
                if rtype not in ["combat", "treasure", "shop", "rest", "puzzle", "inter_level"]:
                    print('Room type not in list, Room Type = None (random room)')
                if input('Boss Room (y/n): ') == "y":
                    isboss = True
                else:
                    isboss = False
                rtype = rtype if rtype else "combat"  # Default to combat if None
                dungeon.rooms.insert(len(dungeon.rooms), generate_random_room(player=player, room_type=rtype, is_boss_room=isboss))
            else: # Display rooms to select them:
                print(f"{Colors.YELLOW}Available rooms:{Colors.RESET}")
                for i, room in enumerate(dungeon.rooms):
                    room_name = f"the Boss Chamber" if room.room_type == "boss" else f"a {room.room_type.capitalize()} Room"
                    print(f"{Colors.CYAN}{i+1}. Go to {room_name}{Colors.RESET}")
                room_choice = int(input(f"{Colors.CYAN}Enter room number to teleport to: {Colors.RESET}")) - 1
                if 0 <= room_choice < len(dungeon.rooms):
                    dungeon.current_room = room_choice
                    print(f"{Colors.GREEN}Teleported to {dungeon.rooms[room_choice].room_type} room.{Colors.RESET}")
            # Teleport to a Room
            rooms = [r for r in dungeon.rooms if r.room_type == room_type]
            print("rooms:", rooms)
            room_type = input(f"{Colors.CYAN}Enter room type (combat/shop/treasure/boss/puzzle/trap): {Colors.RESET}")
            if rooms:
                dungeon.current_room = dungeon.rooms.index(rooms[0])  # Set current room to the index of the first room of requested type
                logger.info(f"Teleporting to room type: {room_type}")
                print(f"{Colors.GREEN}Teleported to {room_type} room.{Colors.RESET}")
            else:
                print(f"{Colors.RED}No room of that type found.{Colors.RESET}")

        elif choice == "5":
            try:
                # Spawn Enemies in Current Room
                num_enemies = int(input(f"{Colors.CYAN}Enter number of enemies to spawn: {Colors.RESET}"))
                for _ in range(num_enemies):
                    # ask for enemy level:
                    enemy_level = int(input(f"{Colors.CYAN}Enter enemy level: {Colors.RESET}"))
                    # ask if enemy a boss:
                    is_boss = input(f"{Colors.CYAN}Is enemy a boss (y/n): {Colors.RESET}").lower() == 'y'
                    enemy = generate_enemy(enemy_level, is_boss, player)
                    dungeon.rooms[dungeon.current_room].enemies.append(enemy)
                    print(f"{Colors.RED}Spawned enemy: {enemy.name}{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in spawn enemies input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")

        elif choice == "6":
            try:
                # Complete a Quest Instantly
                if player.quests:
                    for i, quest in enumerate(player.quests):
                        print(f"{Colors.YELLOW}{i+1}. {quest.title}{Colors.RESET}")
                    quest_choice = int(input(f"{Colors.CYAN}Enter quest number to complete: {Colors.RESET}")) - 1
                    if 0 <= quest_choice < len(player.quests):
                        player.quests[quest_choice].completed = True
                        player.completed_quests.append(player.quests.pop(quest_choice))
                        print(f"{Colors.GREEN}Quest completed!{Colors.RESET}")
                        logger.info(f"Completed quest: {player.completed_quests[-1].title}")
                    else:
                        print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}No active quests.{Colors.RESET}")
            except ValueError as e:
                logger.warning(f"ValueError in complete quest input: {e}")
                print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught: {e}")
                print(f"{Colors.RED}Error : {e}{Colors.RESET}")

        elif choice == "7":
            # Heal Player
            player.stats.hp = player.stats.max_hp
            logger.info("Player healed to max HP with debug menu")
            print(f"{Colors.GREEN}Player fully healed!{Colors.RESET}")

        elif choice == "8":
            try:
                # Save Game
                save_name = input(f"{Colors.YELLOW}Enter save name: {Colors.RESET}")
                player.save_player(save_name)
                print(f"{Colors.GREEN}Game saved!{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught during save game: {e}")
                print(f"{Colors.RED}Error saving game: {e}{Colors.RESET}")

        elif choice == "9":
            try:
                # Load Game
                loaded_player = load_player()
                if loaded_player:
                    player = loaded_player
                    print(f"{Colors.GREEN}Game loaded!{Colors.RESET}")
            except Exception as e:
                logger.warning(f"Exception caught during load game: {e}")
                print(f"{Colors.RED}Error loading game: {e}{Colors.RESET}")

        elif choice == "10":
            if input(f'Unlock all difficulties ? (y/n): ') == "y":
                # Set all player.unlocked_difficulties value to True:
                logger.info("Unlocking all difficulties")
                for key, val in player.unlocked_difficulties.items():
                    print(f"{Colors.YELLOW}Unlocking difficulty: {key}{Colors.RESET}")
                    player.unlocked_difficulties[key] = True
            choose_difficulty(player)
        
        elif choice == "11":
            # Reload Dungeon
            for rm in dungeon:
                print(rm)
            logger.info("Reloading dungeon")
            print(f"{Colors.YELLOW}Reloading dungeon...{Colors.RESET}")
            rooms = generate_dungeon(player)
            dungeon = Dungeon(rooms)
            player.current_room_number = 0
            logger.info("Dungeon reloaded")
            print(f"{Colors.GREEN}Dungeon reloaded!{Colors.RESET}")
            for rm in dungeon:
                print(rm)

        elif choice == "12":
            # Give Armor Set
            from data.data import armor_sets, enemy_sets
            from items.items import create_armor, create_weapon, Weapon
            armor_set_name = input(f"{Colors.CYAN}Enter armor set name (e.g., Brigand, Cursed Bone, Hunter, etc.): {Colors.RESET}")
            if armor_set_name not in armor_sets:
                print(f"{Colors.RED}Armor set '{armor_set_name}' not found!{Colors.RESET}")
            else:
                armor_pieces = ["Helmet", "Chestplate", "Gauntlets", "Leggings", "Boots", "Shield"]
                for piece in armor_pieces:
                    armor_item = create_armor(
                        level=player.dungeon_level,
                        rarity="legendary",
                        prefix="Given",
                        armor_type=piece,
                        value_base=2500,
                        rarity_data={
                            "multipliers": {"legendary": 5},
                            "colors": {"legendary": lambda text: f"{Colors.YELLOW}{text}{Colors.RESET}"},
                            "prefixes": {"legendary": [armor_set_name]}
                        },
                        armor_set_type=armor_set_name
                    )
                    player.inventory.append(armor_item)
                    logger.info(f"Added armor item: {armor_item.name}")
                    print(f"{Colors.GREEN}Added {armor_item.name} to inventory.{Colors.RESET}")
                
                # Also give the weapon of the set
                # Find the enemy type that has this armor set to get the weapon name
                weapon_name = None
                for enemy_type, sets in enemy_sets.items():
                    if sets.get("armor") == armor_set_name:
                        weapon_name = sets.get("weapon")
                        break
                if weapon_name:
                    # Create weapon with special attacks if any
                    from data.data import weapon_special_attacks
                    special_attacks = weapon_special_attacks.get(weapon_name, None)
                    weapon_item = create_weapon(
                        level=player.dungeon_level,
                        rarity="legendary",
                        prefix="Given",
                        weapon_type=weapon_name,
                        value_base=3000,
                        rarity_data={
                            "multipliers": {"legendary": 5},
                            "colors": {"legendary": lambda text: f"{Colors.YELLOW}{text}{Colors.RESET}"},
                            "prefixes": {"legendary": [weapon_name]}
                        },
                        special_attacks=special_attacks
                    )
                    player.inventory.append(weapon_item)
                    logger.info(f"Added weapon item: {weapon_item.name}")
                    print(f"{Colors.GREEN}Added {weapon_item.name} to inventory.{Colors.RESET}")

        elif choice == "99":
            logger.warning("EXECUTING PYTHON COMMAND")
            print(f"{Colors.RED}Ctrl + c or 'exit' to exit")
            while True:
                try:
                    cmd = input(f"{Colors.GREEN}> {Colors.RESET}")
                    logger.info(f"Executing command: {cmd}")
                    if cmd.lower() == "exit":
                        break
                    result = eval(cmd, globals(), locals())
                    logger.info(f"Command result: {result}")
                    print({result})
                except SyntaxError:
                    try:
                        exec(cmd, globals(), locals())
                    except Exception as e:
                        print(f"{Colors.RED}Erreur exec: {e}{Colors.RESET}")
                except KeyboardInterrupt:
                    print(f"{Colors.RED}Exiting python commands{Colors.RESET}")
                    break
                except Exception as e:
                    print(f"{Colors.RED}Erreur eval: {e}{Colors.RESET}")

        elif choice == "0":
            # Exit Debug Menu
            print(f"{Colors.RED}Exiting Debug Menu...{Colors.RESET}")
            break

        else:
            print(f"{Colors.RED}Invalid choice! Try again.{Colors.RESET}")
