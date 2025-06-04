__version__ = "10.0"
__creation__ = "29-05-2025"

class Mastery:
    def __init__(self, name, xp=0, level=1):
        self.name = name
        self.xp = xp
        self.level = level

    def __str__(self):
        return f"{self.name}: Lvl {self.level} ({self.xp}/{self.xp_to_next()})"

    def to_dict(self):
        return {"name": self.name, "xp": self.xp, "level": self.level}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["xp"], data["level"])

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1

    def xp_to_next(self):
        return 100 + 50 * self.level  # simple formule
