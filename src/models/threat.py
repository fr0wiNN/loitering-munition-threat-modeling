from .entity import Entity
from .asset import Asset


class Threat(Entity):
    def __init__(self, target: Asset, name: str, x: float, y: float):
        super().__init__(name, x, y)
        self.target = target