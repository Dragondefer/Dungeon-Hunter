from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.entity import Entity
from core.status_effects import *
# Special attacks

def flaming_strike(user: Entity, target: Entity):
    dmg = 30 + user.stats.attack
    target.stats.take_damage(dmg)
    target.try_apply_status("burn")

def frost_slam(user: Entity, target: Entity):
    dmg = 25
    target.stats.take_damage(dmg)
    target.try_apply_status(Freeze(2))

def lightning_strike(user: Entity, target: Entity):
    dmg = 35 + user.stats.attack
    target.stats.take_damage(dmg)
    target.try_apply_status("shock")

def arcane_explosion(user: Entity, target: Entity):
    dmg = 40 + user.stats.attack
    target.stats.take_damage(dmg)
    user.try_apply_status("mana_boost")

def earth_shatter(user: Entity, target: Entity):
    dmg = 50 + user.stats.attack
    target.stats.take_damage(dmg)
    target.try_apply_status("stunned")

special_attacks_dict = {
    "flaming_strike": flaming_strike,
    "frost_slam": frost_slam,
    "lightning_strike": lightning_strike,
    "arcane_explosion": arcane_explosion,
    "earth_shatter": earth_shatter
}

# Map weapon set names to their special attacks (list of tuples: attack name, attack function)
weapon_special_attacks = {
    "Goblin Dagger": [("Flaming Strike", flaming_strike)],
    "Undead Blade": [("Frost Slam", frost_slam)],
    "Wolf Claws": [("Lightning Strike", lightning_strike)],
    "Orcish Battle Axe": [("Earth Shatter", earth_shatter)],
    "Bone Crusher": [("Earth Shatter", earth_shatter)],
    "Phantom Scythe": [("Arcane Explosion", arcane_explosion)],
    "Twin Shadow Blades": [("Shadow Bind", None)],  # Shadow Bind not in special_attacks_dict
    "Wraithblade": [("Frost Slam", frost_slam), ("Earth Shatter", earth_shatter)],
    "Earthshatter Maul": [("Earth Shatter", earth_shatter)],
    "Hellfire Sword": [("Flaming Strike", flaming_strike)],
    "Dragon Slayer": [("Flaming Strike", flaming_strike), ("Lightning Strike", lightning_strike)],
    "Void Staff": [("Arcane Explosion", arcane_explosion)],
}
