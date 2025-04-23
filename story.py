from colors import Colors
from datetime import datetime
import time

from game_utility import typewriter_effect
def display_title():
    title = """
████████╗██████╗ ███████╗ █████╗ ███████╗██╗   ██╗██████╗ ███████╗
╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║   ██║██╔══██╗██╔════╝
   ██║   ██████╔╝█████╗  ███████║███████╗██║   ██║██████╔╝█████╗  
   ██║   ██╔══██╗██╔══╝  ██╔══██║╚════██║██║   ██║██╔══██╗██╔══╝  
   ██║   ██║  ██║███████╗██║  ██║███████║╚██████╔╝██║  ██║███████╗
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
                                                                   
██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ ███████╗       
██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝       
███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝███████╗       
██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗╚════██║       
██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║███████║       
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝       
                                                                    
 ██████╗  █████╗ ███╗   ███╗██████╗ ██╗████████╗                   
██╔════╝ ██╔══██╗████╗ ████║██╔══██╗██║╚══██╔══╝                   
██║  ███╗███████║██╔████╔██║██████╔╝██║   ██║                      
██║   ██║██╔══██║██║╚██╔╝██║██╔══██╗██║   ██║                      
╚██████╔╝██║  ██║██║ ╚═╝ ██║██████╔╝██║   ██║                      
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝                      
        """
    print(Colors.gradient_text(title, (0, 175, 75), (30, 125, 125)))
    print(f"{Colors.CYAN}A roguelike dungeon crawler where your luck determines your fate{Colors.RESET}")
    print(f"{Colors.YELLOW}Created on {datetime.now().strftime('%Y-%m-%d')}{Colors.RESET}")

def display_intro():
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