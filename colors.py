# Terminal colors and formatting
class Colors:
    """
    Provides ANSI escape codes for colored text output in the terminal.
    
    Attributes:
        Standard Colors:
            BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
        
        Bright Colors:
            BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, 
            BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
        
        Text Formatting:
            BOLD, UNDERLINE, BLINK, REVERSE, RESET

    Methods:
        rainbow_text(text: str) -> str:
            Returns a string with a rainbow-colored effect.
        
        gradient_text(text: str, start_color: tuple, end_color: tuple, reset_color: bool = False) -> str:
            Returns a string with a smooth color gradient effect from `start_color` to `end_color`.
    """
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    RESET = '\033[0m'
    TEST = '\033'

    @staticmethod
    def rainbow_text(text):
        colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
        colored_text = ""
        for i, char in enumerate(text):
            if char != ' ':
                colored_text += colors[i % len(colors)] + char
            else:
                colored_text += char
        return colored_text + Colors.RESET

    @staticmethod
    def gradient_text(text, start_color, end_color):
        # Simple linear interpolation between RGB values
        sr, sg, sb = start_color
        er, eg, eb = end_color
        
        colored_text = ""
        for i, char in enumerate(text):
            if char != ' ':
                # Calculate percentage through the string
                p = i / max(1, len(text) - 1)
                # Interpolate RGB values
                r = int(sr + (er - sr) * p)
                g = int(sg + (eg - sg) * p)
                b = int(sb + (eb - sb) * p)
                # Convert to ANSI escape code and append character
                colored_text += f'\033[38;2;{r};{g};{b}m{char}'
            else:
                colored_text += char
        
        return colored_text + Colors.RESET
    

if __name__ == '__main__':
    print(Colors.rainbow_text('Hello, World!'))
    print(Colors.gradient_text('Hello, World!', (255, 0, 0), (0, 255, 0)) + Colors.RESET)  # Red to Green gradient
    print(Colors.BOLD + 'Bold text' + Colors.RESET)
    print(Colors.UNDERLINE + 'Underlined text' + Colors.RESET)
    print(Colors.BLINK + 'Blinking text' + Colors.RESET)
    print(Colors.REVERSE + 'Reversed text' + Colors.RESET)
    print(f"{Colors.TEST}TEST{Colors.RESET}")
