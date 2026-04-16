from .entity import Entity


class Asset(Entity):
    def __init__(self, name: str, value: float, x: float, y: float):
        super().__init__(name, x, y)
        self.name = name
        self.value = value