from .weapon import Weapon


class Patriot(Weapon):
    # MIM-104 Patriot System
    # NATO code name: MIM-104 Patriot
    # Interceptor: PAC-2
    # https://en.wikipedia.org/wiki/MIM-104_Patriot
    def __init__(self, x: float, y: float, name: str):
        super().__init__(
            name=name,
            x=x,
            y=y,
            usage_cost=100_000.0,
            kill_prob=0.85,
            engage_range=200.0,
            capacity=4
        )


class Strela(Weapon):
    # 9K35 Strela-10 System
    # NATO code name: SA-13 "Gopher"
    # Interceptor: 9M333
    # https://en.wikipedia.org/wiki/9K35_Strela-10
    NAME = "SA-13"
    def __init__(self, x: float, y: float, name: str):
        super().__init__(
            name=name,
            x=x,
            y=y,
            usage_cost=60_000.0,
            kill_prob=0.55,
            engage_range=5.00,
            capacity=4
        )
