from .threat import Threat
from .asset import Asset

class SHA(Threat):
    # HQ
    def __init__(self, lat: float, lon: float, name: str, target: Asset):
        super().__init__(
            name=name,
            lat=lat,
            lon=lon,
            target=target
        )