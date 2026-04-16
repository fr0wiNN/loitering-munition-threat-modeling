from .entity import Entity


class Weapon(Entity):
    def __init__(self, name: str, x: float, y: float):
        super().__init__(name, x, y)