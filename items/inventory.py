__version__ = "24.0"
__creation__ = "08-05-2025"

# D​un​g​e​o​n​ ​H​un​te​r​ ​-​ ​(​c​)​ ​D​ra​g​on​d​ef​e​r​ ​2​02​5
# Li​c​en​s​e​d​ ​un​de​r​ ​C​C-​B​Y​-​NC​ ​4​.​0


class Inventory(list):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def append(self, item):
        """
        Adds an item to the inventory and updates player's collected items count.
        """
        super().append(item)
        self.player.items_collected += 1

    def remove(self, item):
        if item in self:
            super().remove(item)
            # self.player.items_collected = max(0, self.player.items_collected - 1)

    def clear(self) -> None:
        return super().clear()

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __iter__(self):
        return super().__iter__()

    def __getattr__(self, attr):
        # Délègue aux méthodes de la liste si besoin
        return getattr(list, attr)

    def __str__(self):
        if not self:
            return "Inventory is empty."
        return "Inventory:\n" + "\n".join(f"• {item.name}" for item in self)

    def find_by_name(self, name):
        return next((item for item in self if getattr(item, "name", None) == name), None)

