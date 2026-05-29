from typing import List, Tuple
from pyproj import Geod

from models.asset import Asset
from models.threat import Threat
from models.weapon import Weapon

geod = Geod(ellps="WGS84")


class Scenario:
    def __init__(self, name: str, sw_anchor: Tuple[float, float], ne_anchor: Tuple[float, float]):
        self.name = name

        # Expected format: (latitude, longitude)
        self.sw_latlon = sw_anchor
        self.ne_latlon = ne_anchor

        self.assets: List[Asset] = []
        self.threats: List = []
        self.weapons: List = []

    def add_assets(self, *assets: Asset):
        self.assets.extend(assets)

    def add_threats(self, *threats: Threat):
        self.threats.extend(threats)

    def add_weapons(self, *weapons: Weapon):
        self.weapons.extend(weapons)

    def details(self) -> str:
        sw_lat, sw_lon = self.sw_latlon
        ne_lat, ne_lon = self.ne_latlon

        # Width = Distance between SW corner and SE corner (same latitude, different longitude)
        _, _, width_m = geod.inv(sw_lon, sw_lat, ne_lon, sw_lat)

        # Height = Distance between SW corner and NW corner (same longitude, different latitude)
        _, _, height_m = geod.inv(sw_lon, sw_lat, sw_lon, ne_lat)

        width_km = width_m / 1000.0
        height_km = height_m / 1000.0

        return (f"Scenario: {self.name}\n"
                f"Anchors: SW {self.sw_latlon} | NE {self.ne_latlon}\n"
                f"Physical Size: {width_km:.1f}km x {height_km:.1f}km\n"
                f"Assets: {len(self.assets)} | Threats: {len(self.threats)} | Weapons: {len(self.weapons)}\n")