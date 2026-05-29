from pyproj import Geod
from .entity import Entity

geod = Geod(ellps="WGS84")


class Weapon(Entity):
    NAME: str = "GenericWeapon"

    def __init__(self, name: str, lat: float, lon: float, usage_cost: float, kill_prob: float, engage_range: float,
                 capacity: int):
        super().__init__(name, lat, lon)
        self.usage_cost = usage_cost
        self.kill_prob = kill_prob
        self.engage_range = engage_range  # Kept in meters
        self.capacity = capacity

    def is_in_range(self, target: Entity) -> bool:
        # inv returns (forward_azimuth, back_azimuth, distance_in_meters)
        _, _, distance_m = geod.inv(self.lon, self.lat, target.lon, target.lat)
        return self.engage_range > distance_m