import numpy as np
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Tuple
from models import Weapon, Threat
from .wta_model import WTAModel


@dataclass
class SolverResult:
    """
    Standardized output for WTA solvers
    """
    solver_name: str

    # Assignment (X matrix)
    decision_matrix: np.ndarray

    # Optimization objectives
    engagement_cost: float = 0.0
    expected_asset_loss: float = 0.0

    # Performance metrics
    execution_time_s : float = 0.0

    def __str__(self) -> str:
        """
        Prints the details for user
        """
        total_shots = int(np.sum(self.decision_matrix))
        total_system_cost = self.engagement_cost + self.expected_asset_loss

        lines = [
            f"\n=== {self.solver_name.upper()} RESULTS ===",
            f"Engagement Cost:     ${self.engagement_cost:,.2f}",
            f"Expected Asset Loss: ${self.expected_asset_loss:,.2f}",
            "-" * 40,
            f"Total System Cost:   ${total_system_cost:,.2f}",
            "-" * 40,
            f"Compute Time:        {self.execution_time_s:.4f}s",
            f"Interceptors Fired:  {total_shots} (Shape: {self.decision_matrix.shape})"
        ]

        return "\n".join(lines)



class BaseSolver(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(self, model: WTAModel) -> List[SolverResult]:
        """
        Part of strategy pattern.
        Run the optimization and return a standardized SolverResult.
        """
        pass
