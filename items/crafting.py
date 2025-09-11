# D​u​n​g​eo​n​ ​H​un​t​e​r​ ​-​ ​(​c​)​ ​D​ra​g​o​n​de​f​e​r​ ​20​2​5
# L​i​ce​ns​e​d​ ​u​nd​e​r​ C​C​-​B​Y-​NC​ ​4.​0


class Recipe:
    def __init__(self, name, ingredients: dict[str, int], result: str):
        self.name = name
        self.inputs = ingredients  # {"iron_ore": 2, "magic_essence": 1}
        self.output = result  # item_id (ex: "iron_sword")

    def can_craft(self, inventory: dict):
        """
        Check if the inventory has enough resources to craft the recipe.
        inventory: dict of resource_id to quantity
        """
        return all(inventory.get(res, 0) >= qty for res, qty in self.inputs.items())

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

