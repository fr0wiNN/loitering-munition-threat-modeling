from .entity import Entity
from .asset import Asset


class Threat(Entity):
    def __init__(self, target: Asset, name: str, lat: float, lon: float):
        super().__init__(name, lat, lon)
        self.target = target

    @property
    def value(self) -> float:
        return self.target.value
