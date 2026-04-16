from typing import List
from .asset import Asset
from .threat import Threat
from .weapon import Weapon


class Scenario:
    def __init__(self, name: str, width: float, height: float):
        self.name = name
        self.width = width
        self.height = height

        self.assets: List[Asset] = []
        self.threats: List[Threat] = []
        self.weapons: List[Weapon] = []

    def get_name(self):
        return self.name

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def add_assets(self, *assets: Asset):
        self.assets.extend(assets)

    def add_threats(self, *threats: Threat):
        self.threats.extend(threats)

    def add_weapons(self, *weapons: Weapon):
        self.weapons.extend(weapons)

    def get_assets(self):
        return self.assets

    def get_threats(self):
        return self.threats

    def get_weapons(self):
        return self.weapons

    def details(self) -> str:
        return (f"Scenario: {self.name}\n"
                f"Size: ({self.width}x{self.height})\n"
                f"Assets: {len(self.assets)}\n"
                f"Threats: {len(self.threats)}\n"
                f"Weapons: {len(self.weapons)}\n")
