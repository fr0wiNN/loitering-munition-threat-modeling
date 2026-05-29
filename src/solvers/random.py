import random
import time
import numpy as np
from typing import List

from .wta_model import WTAModel
from .base import BaseSolver, SolverResult


class RandomSolver(BaseSolver):
    def __init__(self, n_trials=2500, seed=420):
        """
        n_trials defaults to 2500 to match an NSGA-II run with pop_size=50 and n_gen=50.
        """
        super().__init__(name="RandomSearch")
        self.n_trials = n_trials
        self.seed = seed

    def _generate_random_matrix(self, model: WTAModel) -> np.ndarray:
        """Generates a perfectly legal random assignment matrix."""
        W = model.num_weapons
        T = model.num_threats

        X_matrix = np.zeros((W, T), dtype=int)

        for i in range(W):
            cap = int(model.weapon_capacities[i])
            for _ in range(cap):
                # Target IDs go from 0 to T-1.
                # 'T' acts as the dummy "Hold Fire" target.
                target_idx = random.randint(0, T)

                if target_idx < T:
                    X_matrix[i, target_idx] += 1

        return X_matrix

    def solve(self, model: WTAModel, seed_matrix: np.ndarray = None) -> List[SolverResult]:
        start_time = time.time()

        if self.seed is not None:
            np.random.seed(self.seed)
            random.seed(self.seed)

        all_trials = []

        # 1. Generate and evaluate all random trials
        for i in range(self.n_trials):
            if i == 0 and seed_matrix is not None:
                X_matrix = seed_matrix.copy()
            else:
                X_matrix = self._generate_random_matrix(model)

            cost = model.evaluate_engagement_cost(X_matrix)
            loss = model.evaluate_expected_asset_loss(X_matrix)

            all_trials.append(SolverResult(
                solver_name=self.name,
                decision_matrix=X_matrix,
                engagement_cost=float(cost),
                expected_asset_loss=float(loss),
                execution_time_s=0.0  # We'll stamp the final execution time at the end
            ))

        # 2. Extract the Pareto Front natively (no pymoo required)
        # Step A: Sort by Objective 1 (cost, ascending), then Objective 2 (loss, ascending)
        all_trials.sort(key=lambda r: (r.engagement_cost, r.expected_asset_loss))

        pareto_front = []
        min_loss_seen = float('inf')

        # Step B: Sweep through to find non-dominated solutions.
        # Since they are sorted by cost, a new solution is only non-dominated
        # if its loss is strictly better than the lowest loss seen so far.
        for result in all_trials:
            if result.expected_asset_loss < min_loss_seen:
                pareto_front.append(result)
                min_loss_seen = result.expected_asset_loss

        # 3. Finalize execution time
        execution_time = time.time() - start_time
        for res in pareto_front:
            res.execution_time_s = execution_time

        return pareto_front