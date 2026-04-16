# TODO:
# - standardize location measure units and relate to real world.

class Entity:
    def __init__(self, name: str, x: float, y: float):
        self.name = name
        self.x = x
        self.y = y