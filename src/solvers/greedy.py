import time
import numpy as np
from typing import List
from .wta_model import WTAModel
from .base import BaseSolver, SolverResult


class GreedyMMRSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="Greedy MMR")

    def solve(self, model: WTAModel) -> List[SolverResult]:
        start_time = time.time()

        W = model.num_weapons
        T = model.num_threats

        # Decision init
        X = np.zeros((W, T), dtype=int)

        # Dynamic states
        capacities = model.weapon_capacities.copy()
        survival_probs = np.ones(T)

        # Calculate threat values
        threat_values = np.zeros(T)
        for k, targeted_threats in model.target_map.items():
            for j in targeted_threats:
                threat_values[j] = model.asset_values[k]

        # Greedy loop
        while True:
            best_i, best_j = -1, -1
            max_marginal_return = 0.0  # Changed variable name for clarity

            for i in range(W):
                if capacities[i] <= 0:
                    continue

                for j in range(T):
                    kill_prob = model.kill_probs[i, j]
                    if kill_prob == 0.0:
                        continue  # Out of range

                    expected_value_saved = threat_values[j] * survival_probs[j] * kill_prob

                    marginal_return = expected_value_saved / (model.weapon_costs[i] + 1e-9)

                    if marginal_return > max_marginal_return:
                        max_marginal_return = marginal_return
                        best_i = i
                        best_j = j

            if best_i == -1 or max_marginal_return <= 0.0001:
                break

            X[best_i, best_j] += 1
            capacities[best_i] -= 1
            survival_probs[best_j] *= (1.0 - model.kill_probs[best_i, best_j])

        # Stop the benchmark
        execution_time = time.time() - start_time

        # Get the results
        final_cost = model.evaluate_engagement_cost(X)
        final_loss = model.evaluate_expected_asset_loss(X)

        # Return
        return [SolverResult(
            solver_name=self.name,
            decision_matrix=X,
            engagement_cost=final_cost,
            expected_asset_loss=final_loss,
            execution_time_s=execution_time
        )]