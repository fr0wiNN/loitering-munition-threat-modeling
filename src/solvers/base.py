from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from models import Weapon, Threat
from scenario import Scenario


class SolverResult:
    def __init__(self):
        # Which weapon shoots at which target
        self.assignments: List[Tuple[Weapon, Threat]] = []

        # Financial metrics
        self.total_engagement_cost: float = 0.0
        self.expected_asset_loss: float = 0.0

        # Compute time metric
        self.execution_time_seconds: float = 0.0


class BaseSolver(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(self, scenario: Scenario) -> SolverResult:
        """
        Part of strategy pattern.
        Run the optimization and
        return a standardized SolverResult.
        """
        pass
