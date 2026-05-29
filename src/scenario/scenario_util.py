import random
from typing import Type
from pyproj import Geod
from models import Asset, Threat
from models.weapon import Weapon

# Initialize the WGS84 ellipsoid model
geod = Geod(ellps="WGS84")


class ScenarioGenerator:
    def __init__(self, seed: int = 420):
        if seed is not None:
            random.seed(seed)

    def generate_weapon_cluster(self, center_lat: float, center_lon: float, radius: float, amount: int,
                                weapon_class: Type) -> list:
        cluster = []
        for i in range(amount):
            # Random direction (0 to 360 degrees) and random distance in meters
            azimuth = random.uniform(0, 360)
            distance = random.uniform(0, radius)

            # fwd calculates the new lon/lat given a starting point, direction, and distance
            new_lon, new_lat, _ = geod.fwd(center_lon, center_lat, azimuth, distance)

            weapon = weapon_class(
                lat=new_lat,
                lon=new_lon,
                name=f"{weapon_class.__name__}-{i}"
            )
            cluster.append(weapon)
        return cluster

    def generate_asset_cluster(self, center_lat: float, center_lon: float, radius: float, amount: int,
                               asset_class: Type[Asset]) -> list[Asset]:
        cluster = []
        for i in range(amount):
            azimuth = random.uniform(0, 360)
            distance = random.uniform(0, radius)
            new_lon, new_lat, _ = geod.fwd(center_lon, center_lat, azimuth, distance)

            asset = asset_class(
                lat=new_lat,
                lon=new_lon,
                name=f"{asset_class.__name__}-{i}"
            )
            cluster.append(asset)
        return cluster

    def generate_threat_cluster(self, center_lat: float, center_lon: float, radius: float, amount: int,
                                threat_class: Type, target_pool: list[Asset]) -> list:
        cluster = []
        for i in range(amount):
            azimuth = random.uniform(0, 360)
            distance = random.uniform(0, radius)
            new_lon, new_lat, _ = geod.fwd(center_lon, center_lat, azimuth, distance)

            assigned_target = random.choice(target_pool)

            threat = threat_class(
                lat=new_lat,
                lon=new_lon,
                target=assigned_target,
                name=f"{threat_class.__name__}-{i}"
            )
            cluster.append(threat)
        return cluster