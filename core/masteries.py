__version__ = "19.0"
__creation__ = "29-05-2025"

class Mastery:
    def __init__(self, name, xp=0, level=1):
        self.name = name
        self.xp = xp
        self.max_xp = 100
        self.level = level

    def __str__(self):
        return f"{self.name}: Lvl {self.level} ({self.xp}/{self.xp_to_next()})"

    def to_dict(self):
        return {"name": self.name, "xp": self.xp, "level": self.level}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["xp"], data["level"])

    def xp_to_next(self):
        return self.max_xp * 1.5  # simple formule
    
    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1

    def get_bonus(self) -> dict:
        """
        Retourne un dict de bonus/malus à appliquer selon self.level.
        - level 0 : malus (ex : -10% d’accuracy)
        - level 1 : neutre (0 bonus)
        - level >=2 : bonus croissant
        Exemple renvoyé : {"damage_multiplier": 1.1, "accuracy": 0.05}
        """
        if self.level == 0:
            return {"damage_multiplier": 0.9, "accuracy": -0.10}
        elif self.level == 1:
            return {}  # pas de bonus le niveau de base
        else:
            # chaque niveau au-dessus de 1 confère +5% dégâts et +2% précision
            bonus_dmg = 1 + 0.05 * (self.level - 1)
            bonus_acc = 0.02 * (self.level - 1)
            return {"damage_multiplier": bonus_dmg, "accuracy": bonus_acc}

