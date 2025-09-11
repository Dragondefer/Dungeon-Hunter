# Du​n​g​e​o​n​ ​H​u​n​te​r​ ​-​ ​(​c)​ ​Dr​a​g​o​n​de​f​e​r​ ​20​2​5
# L​i​ce​n​s​e​d​ ​un​d​e​r​ ​C​C​-​B​Y​-N​C​ ​4​.​0


class Resource:
    def __init__(self, name, rarity, description, value=0):
        self.name = name
        self.rarity = rarity  # "common", "rare", etc.
        self.description = description
        self.value = value

    def __str__(self):
        return f"{self.name} ({self.rarity}) - {self.description}"

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            rarity=data.get("rarity", "common"),
            description=data.get("description", ""),
            value=data.get("value", 0)
        )
