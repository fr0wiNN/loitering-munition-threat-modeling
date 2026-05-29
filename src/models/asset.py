from .entity import Entity


class Asset(Entity):
    def __init__(self, name: str, value: float, lat: float, lon: float):
        super().__init__(name, lat, lon)
        self.name = name
        self.value = value
