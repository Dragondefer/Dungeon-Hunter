class StatusEffect:
    def __init__(self, name, duration, damage_per_turn=0, effect_type="debuff"):
        self.name = name
        self.duration = duration
        self.damage_per_turn = damage_per_turn
        self.effect_type = effect_type  # "buff", "debuff", "control"...

    def apply(self, target):
        """Effet immédiat (ex: gel = skip le tour)."""
        pass

    def on_turn_start(self, target):
        """Effet au début de chaque tour (ex: poison)."""
        if self.damage_per_turn > 0:
            target.stats.hp -= self.damage_per_turn
            print(f"{target.name} suffers {self.damage_per_turn} damage from {self.name}.")

        self.duration -= 1

    def is_expired(self):
        return self.duration <= 0

    def __str__(self):
        return f"{self.name} ({self.duration} turns)"

    def __repr__(self):
        return f"<StatusEffect: {self.name}, Duration: {self.duration}>"


class Poison(StatusEffect):
    def __init__(self, duration=3, damage_per_turn=5):
        super().__init__("Poison", duration, damage_per_turn, "debuff")

class Burn(StatusEffect):
    def __init__(self, duration=2, damage_per_turn=8):
        super().__init__("Burn", duration, damage_per_turn, "debuff")

class Freeze(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Freeze", duration, effect_type="control")

    def apply(self, target):
        target.stats.can_act = False  # à ajouter dans Stats si besoin


EFFECT_MAP = {
    "Poison": Poison,
    "Burn": Burn,
    "Freeze": Freeze,
    # ...
}

def status_effect_from_dict(data):
    cls = EFFECT_MAP.get(data["name"])
    if cls:
        instance = cls()
        instance.__dict__.update(data)
        return instance
    return None