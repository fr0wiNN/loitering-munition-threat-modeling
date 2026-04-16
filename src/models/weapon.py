from .entity import Entity


class Weapon(Entity):
    def __init__(self, name: str, x: float, y: float, usage_cost: float, kill_prob: float, engage_range: float, capacity: int):
        super().__init__(name, x, y)
        self.usage_cost = usage_cost
        self.kill_prob = kill_prob
        self.engage_range = engage_range
        self.capacity = capacity
