from .threat import Threat
from .asset import Asset

class SHA(Threat):
    # HQ
    def __init__(self, x: float, y: float, name: str, target: Asset):
        super().__init__(
            name=name,
            x=x,
            y=y,
            target=target
        )