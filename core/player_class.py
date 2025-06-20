__version__ = "10.0"
__creation__ = "06-06-2025"


class PlayerClass:
    def __init__(self, name:str, bonuses:dict, skill_name:str):
        self.name = name
        self.bonuses = bonuses  # dict of stat bonuses
        self.skill_name = skill_name

    def apply_to_player(self, player):
        # Apply bonuses to player's stats
        for stat, value in self.bonuses.items():
            player.stats.modify_stat(stat, value)
        # Add skill to player if available
        from data.skills_data import skills_dict
        from core.skills import Skill
        if self.skill_name in skills_dict:
            skill_data = skills_dict[self.skill_name]
            skill_instance = Skill.from_dict(skill_data)
            player.skills.append(skill_instance)
        else:
            print(f"Warning: Skill {self.skill_name} not found in skills_dict.")

    def to_dict(self):
        return {
            "name": self.name,
            "bonuses": self.bonuses,
            "skill_name": self.skill_name
        }

    @classmethod
    def from_dict(cls, data):
        name = data.get("name", "Novice")
        bonuses = data.get("bonuses", {})
        skill_name = data.get("skill_name", "")
        return cls(name, bonuses, skill_name)
