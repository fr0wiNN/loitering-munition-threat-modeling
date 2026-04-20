import random
from typing import Type
from models import Asset, Threat
from models.weapon import Weapon
from models.weapon_collection import Patriot


class ScenarioUtil:
    def __init__(self, seed: int = 420):
        if seed is not None:
            random.seed(seed)

    def generate_weapon_cluster(self, center_x: float, center_y: float, radius: float, amount: int,
                                weapon_class: Type[Weapon]) -> list:
        cluster = []
        for i in range(amount):
            offset_x = random.uniform(-radius, radius)
            offset_y = random.uniform(-radius, radius)

            weapon = weapon_class(
                x=center_x + offset_x,
                y=center_y + offset_y
            )

            cluster.append(weapon)

        return cluster
