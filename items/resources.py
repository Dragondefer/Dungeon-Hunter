# Du​n​g​e​o​n​ ​H​u​n​te​r​ ​-​ ​(​c)​ ​Dr​a​g​o​n​de​f​e​r​ ​20​2​5
# L​i​ce​n​s​e​d​ ​un​d​e​r​ ​C​C​-​B​Y​-N​C​ ​4​.​0

import random

from data.resources_data import resources_data_raw, ResourceType
from data import resources_data

class Resource:
    def __init__(self, name, type, rarity, description, value=0):
        self.name = name
        self.type = type
        self.rarity = rarity  # "common", "rare", etc.
        self.description = description
        self.value = value

    def __str__(self):
        return f"{self.name} ({self.rarity}) - {self.description}"

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ResourceType.ORE),
            rarity=data.get("rarity", "common"),
            description=data.get("description", ""),
            value=data.get("value", 0)
        )

def get_resource_by_key(key: str) -> Resource | None:
    return resources_data.get(key, None)


def generate_random_resource(resource_type: ResourceType | None = None):
    """
    Generate a random resource from the available resources.
    
    Args:
        resource_type (ResourceType | None): Filter resources by type, or None for any type.
    
    Returns:
        Resource: A randomly selected resource object.
    """
    # Lazy import to avoid circular imports
    from data import resources_data
    
    if resource_type is None:
        # Get all resources
        pool = list(resources_data.values())
    else:
        # Filter resources by type
        pool = [r for r in resources_data.values() if r.type == resource_type]

        if not pool:
            raise ValueError(f"No resources found for type {resource_type}")

    return random.choice(pool)
