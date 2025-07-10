__version__ = "14.0"
__creation__ = "28-05-2025"

# Dung​e​on​ ​H​u​n​te​r​ ​-​ ​(​c)​ ​Dra​gondef​er​ ​2​02​5
# Li​c​ense​d​ ​und​er​ ​C​C​-​B​Y​-NC​ 4.​0

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

class FireResistance(StatusEffect):
    def __init__(self, duration=2):
        super().__init__("Fire Resistance", duration, effect_type="buff")

    def apply(self, target):
        # Increase burn resistance to grant fire resistance
        if hasattr(target, "resistances") and "burn" in target.resistances:
            target.resistances["burn"] += 1
            print(f"{target.name}'s burn resistance increased by 1 for {self.duration} turns.")
        else:
            print(f"{target.name} gains fire resistance for {self.duration} turns.")

class AttackBoost(StatusEffect):
    def __init__(self, duration=3, boost_amount=5):
        super().__init__("Attack Boost", duration, effect_type="buff")
        self.boost_amount = boost_amount

    def apply(self, target):
        if not hasattr(target.stats, "temporary_stats"):
            target.stats.temporary_stats = {}
        target.stats.temporary_stats["attack"] = target.stats.temporary_stats.get("attack", 0) + self.boost_amount
        print(f"{target.name}'s attack increased by {self.boost_amount} for {self.duration} turns.")

class DefenseBoost(StatusEffect):
    def __init__(self, duration=3, boost_amount=5):
        super().__init__("Defense Boost", duration, effect_type="buff")
        self.boost_amount = boost_amount

    def apply(self, target):
        if not hasattr(target.stats, "temporary_stats"):
            target.stats.temporary_stats = {}
        target.stats.temporary_stats["defense"] = target.stats.temporary_stats.get("defense", 0) + self.boost_amount
        print(f"{target.name}'s defense increased by {self.boost_amount} for {self.duration} turns.")

class LuckBoost(StatusEffect):
    def __init__(self, duration=3, boost_amount=3):
        super().__init__("Luck Boost", duration, effect_type="buff")
        self.boost_amount = boost_amount

    def apply(self, target):
        if not hasattr(target.stats, "temporary_stats"):
            target.stats.temporary_stats = {}
        target.stats.temporary_stats["luck"] = target.stats.temporary_stats.get("luck", 0) + self.boost_amount
        print(f"{target.name}'s luck increased by {self.boost_amount} for {self.duration} turns.")

class HealingEffect(StatusEffect):
    def __init__(self, heal_amount):
        super().__init__("Healing", duration=0, effect_type="buff")
        self.heal_amount = heal_amount

    def apply(self, target):
        old_hp = target.stats.hp
        target.heal(self.heal_amount)
        print(f"{target.name} healed for {target.stats.hp - old_hp} HP.")

from typing import Type, Callable

EFFECT_MAP: dict[str, Callable[..., StatusEffect]] = {
    "Poison": Poison,
    "Burn": Burn,
    "Freeze": Freeze,
    "Fire Resistance": FireResistance,
    "Attack Boost": AttackBoost,
    "Defense Boost": DefenseBoost,
    "Luck Boost": LuckBoost,
    "Healing": HealingEffect,
}

def status_effect_from_dict(data):
    cls = EFFECT_MAP.get(data["name"])
    if cls:
        # Pass all data keys except 'name' as arguments, fallback to update for extra fields
        args = {k: v for k, v in data.items() if k != "name"}
        instance = cls(**args)
        instance.__dict__.update(data)
        return instance
    return None

