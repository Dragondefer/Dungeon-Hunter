import time
from functools import lru_cache

from data import ascii_art_data as art_data
from engine.game_utility import clear_screen, get_terminal_size

class AsciiArt:
    """
      Generates and displays ASCII art from pixel data.
      Allows you to animate the gradual appearance of the art by adjusting the brightness.
      Uses a cache to store pre-generated ASCII sprites.

    Attributes:

        - CHARS: string of characters used to represent grayscale levels.
        - size: size of the art (1: small, 2: medium, 3: large).
        - pixels: 2D list of brightness values (0-255).
        - height: height of the art in lines.
        - width: width of the art in columns.

      Methods:

        - get(name): returns the ASCII sprite according to name and size.
        - _center(line, width): centers a line horizontally.
        - to_ascii(brightness): converts pixels to ASCII art with the given brightness.
        - display(art_lines): displays the ASCII art centered in the terminal.
        - animate_light(duration, fps, step): animates the gradual appearance of the art.
    """
    
    char_type = 'simple'  # 'simple' or 'max'
    CHARS = " .:-=+*#%@"
    CHARS_MAX = ['Ý', '§', 'Ÿ', 'S', 'U', 'ž', '9', 'e', 'û', '®', 'µ', '6', 'T', 'O', '3', '–', '·', '¨', '`', ' ', '²', '¢', 'Ì', 'ú', '5', 'a', 'ä', 'à', 'š', 'Z', 'Ó', 'h', 'ë', 'Ü', 'Ú', 'é', 'ð', 'Ð', 'H', 'À', 'Ä', 'E', 'K', 'R', 'Ž', 'X', 'N', 'g', 'ê', 'Š', 'Õ', 'Ô', 'A', 'Û', 'œ', 'þ', 'x', '¾', 'Î', 'y', 'ô', 'ù', '©', 'V', '@', 'ö', 'ç', '0', 'å', 'Ò', '&', '£', 'Y', 'o', '/', '‘', 'Ï', '!', '¸', 'ˆ', '‚', '´', '7', 'f', 'ý', '8', 'Ù', 'ñ', 'J', '*', 'ª', '“', 'ò', 'á', 'ß', 'ø', '¶', '€', '°', '³', ')', '(', '»', '•', '×', ':', '?', '¿', '”', '­', '½', 'u', '>', 'P', 'ã', '[', '¼', 'v', '˜', '—', '’', 'i', '±', '¦', 'r', '‹', 'n', '<', 'C', ';', '¡', '™', 'ÿ', 'd', '†', '#', '¬', 'º', '¥', 'â', '$', 'ï', 'j', 'õ', 'k', 'Á', 'q', 'w', 'ó', 'L', 'ü', 'í', '4', 'Ö', 'm', 'Í', 'p', '¯', '¤', '+', 't', '…', 'l', 'D', '›', 'Þ', '%', 'G', '‡', 'F', 'Ç', 'æ', '2', '‰', 'î', 'c', 'è', '|', '}', '1', 'I', 'ƒ', '«', 'b', 'z', 's', '=', 'ì', 'Å', 'B', '÷', '¹', 'Q', 'W', 'Â', '^', 'Ã', '{', '„', '~', 'Ë', 'Ñ']
    size = 1  # 1: small, 2: medium, 3: large

    def __init__(self, pixels):
        """
        pixels : list[list[int]] contenant des valeurs de 0 à 255
        """
        self.pixels = pixels
        self.height = len(pixels)
        self.width = len(pixels[0]) if pixels else 0

    @classmethod
    @lru_cache(maxsize=None)
    def get(cls, name: str):
        """Returns the ASCII sprite based on name and size."""
        size_map = {1: "_small", 2: "_medium", 3: "_large"}
        attr = name + size_map.get(cls.size, "_small")
        return getattr(art_data, attr, [f"[Missing art: {attr}]"])

    @staticmethod
    def _center(line: str, width: int) -> str:
        """Center a line horizontally."""
        return " " * max((width - len(line)) // 2, 0) + line

    def to_ascii(self, brightness=1.0):
        if self.char_type == 'max':
            chars = self.CHARS_MAX
        else:
            chars = self.CHARS
        art_lines = []
        for row in self.pixels:
            line = ""
            for val in row:
                v = int(min(max(val * brightness, 0), 255))
                idx = int(v / 255 * (len(chars) - 1))
                line += chars[idx]
            art_lines.append(line)
        return art_lines

    def display(self, art_lines):
        clear_screen()
        cols, rows = get_terminal_size()
        y_offset = max((rows - len(art_lines)) // 2, 0)
        for _ in range(y_offset):
            print()
        for line in art_lines:
            x_offset = max((cols - len(line)) // 2, 0)
            print(" " * x_offset + line)

    def _resample_pixels(self, target_width: int, target_height: int):
        """Resample self.pixels (grayscale 0-255) to target size using simple nearest-neighbour.

        Returns a new 2D list of ints with dimensions (target_height x target_width).
        """
        if self.width == 0 or self.height == 0:
            return [[]]
        if target_width <= 0 or target_height <= 0:
            return [[]]

        new_pixels = [[0 for _ in range(target_width)] for _ in range(target_height)]
        x_ratio = self.width / target_width
        y_ratio = self.height / target_height

        for y in range(target_height):
            src_y = min(int(y * y_ratio), self.height - 1)
            for x in range(target_width):
                src_x = min(int(x * x_ratio), self.width - 1)
                new_pixels[y][x] = self.pixels[src_y][src_x]

        return new_pixels

    def to_ascii_scaled(self, brightness=1.0, margin=0):
        """Convert pixels to ASCII but first scale to terminal size minus optional margin.

        margin: number of character columns/rows to leave free as border around the art.
                If an int is provided it is used for both horizontal and vertical margins.
                If a tuple (h_margin, v_margin) is provided, it is (cols_margin, rows_margin).
        """
        # Normalize margin
        if isinstance(margin, tuple) or isinstance(margin, list):
            h_margin, v_margin = int(margin[0]), int(margin[1])
        else:
            h_margin = v_margin = int(margin)

        cols, rows = get_terminal_size()
        target_w = max(cols - 2 * max(h_margin, 0), 1)
        target_h = max(rows - 2 * max(v_margin, 0), 1)

        # Preserve aspect ratio of source pixels. Characters are taller than wide in many terminals,
        # but we'll keep a 2:1 height correction factor as a reasonable default so images don't look squashed.
        aspect_correction = 0.5  # treat pixels as twice as wide as tall

        # compute scaled dimensions that preserve source aspect ratio
        src_aspect = (self.width / max(self.height, 1))
        # desired aspect considers char aspect
        desired_w = int(min(target_w, max(1, target_h * src_aspect / aspect_correction)))
        desired_h = int(min(target_h, max(1, target_w * aspect_correction / max(src_aspect, 1e-6))))

        # choose the one that fits both constraints
        if desired_w <= target_w:
            final_w = desired_w
            final_h = max(1, int(final_w / max(src_aspect, 1e-6) * aspect_correction))
            if final_h > target_h:
                final_h = target_h
        else:
            final_h = desired_h
            final_w = max(1, int(final_h * src_aspect / aspect_correction))
            if final_w > target_w:
                final_w = target_w

        # safety clamps
        final_w = max(1, min(final_w, target_w))
        final_h = max(1, min(final_h, target_h))

        scaled_pixels = self._resample_pixels(final_w, final_h)

        # convert scaled pixels to ascii
        if self.char_type == 'max':
            chars = self.CHARS_MAX
        else:
            chars = self.CHARS

        art_lines = []
        for row in scaled_pixels:
            line = ""
            for val in row:
                v = int(min(max(val * brightness, 0), 255))
                idx = int(v / 255 * (len(chars) - 1))
                line += chars[idx]
            art_lines.append(line)

        return art_lines

    def animate_light(self, duration=2.0, fps=30, step=0.05, margin=0, scaled=True):
        frames = int(duration * fps)
        brightness = 0.0
        for _ in range(frames):
            if scaled:
                art = self.to_ascii_scaled(brightness, margin=margin)
            else:
                art = self.to_ascii(brightness)
            self.display(art)
            time.sleep(1 / fps)
            brightness = min(brightness + step, 1.0)

# Exemple : "image" fictive → un carré lumineux au centre
pixels = [
    [30,30,30,30,30,30,30,30,30,30],
    [30,80,80,80,80,80,80,80,80,30],
    [30,80,150,150,150,150,150,150,80,30],
    [30,80,150,200,200,200,200,150,80,30],
    [30,80,150,200,255,255,200,150,80,30],
    [30,80,150,200,255,255,200,150,80,30],
    [30,80,150,200,200,200,200,150,80,30],
    [30,80,150,150,150,150,150,150,80,30],
    [30,80,80,80,80,80,80,80,80,30],
    [30,30,30,30,30,30,30,30,30,30]
]

if __name__ == '__main__':
    art = AsciiArt(pixels)
    # Example: animate scaled to terminal with a small margin of 2 columns/rows
    art.animate_light(duration=3, fps=20, step=0.03, margin=2, scaled=True)
