from .asset import Asset

class HQ(Asset):
    # HQ
    def __init__(self, lat: float, lon: float, name: str):
        super().__init__(
            name=name,
            lat=lat,
            lon=lon,
            value=500_000
        )

class OilRefinery(Asset):
    # Oil Refinery
    def __init__(self, lat: float, lon: float, name: str):
        super().__init__(
            name=name,
            lat=lat,
            lon=lon,
            value=1_500_000
        )