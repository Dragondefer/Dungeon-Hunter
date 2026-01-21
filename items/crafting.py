# D​u​n​g​eo​n​ ​H​un​t​e​r​ ​-​ ​(​c​)​ ​D​ra​g​o​n​de​f​e​r​ ​20​2​5
# L​i​ce​ns​e​d​ ​u​nd​e​r​ C​C​-​B​Y-​NC​ ​4.​0

__version__ = "13.0"
__creation__ = "30-08-2025"

class Recipe:
    def __init__(self, name, ingredients: dict[str, int], result: str, category="generic"):
        self.name = name
        self.inputs = ingredients  # {"iron_ore": 2, "magic_essence": 1}
        self.output = result  # item_id (ex: "iron_sword")
        self.category = category

    def __repr__(self):
        return f"Recipe(name={self.name}, inputs={self.inputs}, output={self.output}, category={self.category})"
    
    def __eq__(self, other):
        if not isinstance(other, Recipe):
            return False
        return (self.name == other.name and
                self.inputs == other.inputs and
                self.output == other.output and
                self.category == other.category)
    
    def __hash__(self):
        return hash((self.name, frozenset(self.inputs.items()), self.output, self.category))

    def can_craft(self, resources: dict[str, int]) -> bool:
        """
        Check if the inventory has enough resources to craft the recipe.
        inventory: dict of resource_id to quantity
        """
        return all(resources.get(res, 0) >= qty for res, qty in self.inputs.items())

    def craft(self, inventory: dict):
        """
        Consume the required resources from inventory if can craft.
        Returns True if crafted successfully, False otherwise.
        """
        if not self.can_craft(inventory):
            return False
        for res, qty in self.inputs.items():
            inventory[res] -= qty
            if inventory[res] <= 0:
                del inventory[res]
        return True

    def to_dict(self):
        return {
            "name": self.name,
            "ingredients": self.inputs,
            "result": self.output
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            ingredients=data.get("ingredients", {}),
            result=data.get("result", "")
        )

