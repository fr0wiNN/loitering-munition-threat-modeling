from .asset import Asset

class HQ(Asset):
    # HQ
    def __init__(self, x: float, y: float, name: str):
        super().__init__(
            name=name,
            x=x,
            y=y,
            value=500_000
        )