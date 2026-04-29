import random
from typing import Type
from models import Asset, Threat
from models.weapon import Weapon


class ScenarioGenerator:
    def __init__(self, seed: int = 420):
        if seed is not None:
            random.seed(seed)

    def generate_weapon_cluster(self, center_x: float, center_y: float, radius: float, amount: int, weapon_class: Type[Weapon]) -> list[Weapon]:
        cluster = []
        for i in range(amount):
            offset_x = random.uniform(-radius, radius)
            offset_y = random.uniform(-radius, radius)

            weapon = weapon_class(
                x=center_x + offset_x,
                y=center_y + offset_y,
                name=f"{weapon_class.__name__}-{i}"
            )

            cluster.append(weapon)

        return cluster

    def generate_asset_cluster(self, center_x: float, center_y: float, radius: float, amount: int, asset_class: Type[Asset]) -> list[Asset]:

        cluster = []
        for i in range(amount):
            offset_x = random.uniform(-radius, radius)
            offset_y = random.uniform(-radius, radius)

            asset = asset_class(
                x=center_x + offset_x,
                y=center_y + offset_y,
                name=f"{asset_class.__name__}-{i}"
            )

            cluster.append(asset)

        return cluster

    def generate_threat_cluster(self, center_x: float, center_y: float, radius: float, amount: int, threat_class: Type[Threat], target_pool: list[Asset]) -> list[Threat]:

        cluster = []
        for i in range(amount):
            offset_x = random.uniform(-radius, radius)
            offset_y = random.uniform(-radius, radius)

            assigned_target = random.choice(target_pool)

            threat = threat_class(
                x=center_x + offset_x,
                y=center_y + offset_y,
                target=assigned_target,
                name=f"{threat_class.__name__}-{i}"
            )

            cluster.append(threat)

        return cluster