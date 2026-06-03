import time
import numpy as np
from typing import List
from .wta_model import WTAModel
from .base import BaseSolver, SolverResult


class WeightedGreedyMMRSolver(BaseSolver):
    def __init__(self, w: List[float]):
        """
        Dynamically adjust the weights in score calculation logic:
        Score = (w * Asset Loss) + ((1 - w) * Interceptor Cost)
        :param w: List of weights (e.g., [0.0, 0.25, 0.5, 0.75, 1.0]).
        """
        super().__init__(name="Greedy MMR")
        self.w = w

    def solve(self, model: WTAModel) -> List[SolverResult]:
        W = model.num_weapons
        T = model.num_threats

        # Calculate threat values once (doesn't change between weight iterations)
        threat_values = np.zeros(T)
        for k, targeted_threats in model.target_map.items():
            for j in targeted_threats:
                threat_values[j] = model.asset_values[k]

        results = []

        # Run the greedy algorithm for EACH weight to generate a Pareto curve
        for current_w in self.w:
            start_time = time.time()

            # Decision init for this specific weight
            X = np.zeros((W, T), dtype=int)
            capacities = model.weapon_capacities.copy()
            survival_probs = np.ones(T)

            # Greedy loop
            while True:
                best_i, best_j = -1, -1
                max_improvement = 0.0  # We want strictly positive improvement

                for i in range(W):
                    if capacities[i] <= 0:
                        continue

                    for j in range(T):
                        kill_prob = model.kill_probs[i, j]
                        if kill_prob == 0.0:
                            continue  # Out of range

                        # The raw asset value this specific interceptor is expected to save
                        expected_value_saved = threat_values[j] * survival_probs[j] * kill_prob

                        # The cost of firing this interceptor
                        cost = model.weapon_costs[i]

                        # The Weighted Improvement logic
                        # We want to minimize: w * Loss + (1-w) * Cost
                        # So we maximize the reduction: w * (Value Saved) - (1-w) * (Cost Incurred)
                        improvement = (current_w * expected_value_saved) - ((1.0 - current_w) * cost)

                        # If this is the best valid move so far, save it
                        if improvement > max_improvement:
                            max_improvement = improvement
                            best_i = i
                            best_j = j

                # If no assignment improves the weighted score, stop firing
                # (e.g., the interceptor costs more than the weighted asset value it saves)
                if best_i == -1 or max_improvement <= 1e-9:
                    break

                # Apply the best move
                X[best_i, best_j] += 1
                capacities[best_i] -= 1
                survival_probs[best_j] *= (1.0 - model.kill_probs[best_i, best_j])

            # Stop the benchmark for this weight iteration
            execution_time = time.time() - start_time

            # Evaluate final states
            final_cost = model.evaluate_engagement_cost(X)
            final_loss = model.evaluate_expected_asset_loss(X)

            # Append to our list of Pareto solutions
            results.append(SolverResult(
                solver_name=f"{self.name} (w={current_w:.2f})",
                decision_matrix=X,
                engagement_cost=final_cost,
                expected_asset_loss=final_loss,
                execution_time_s=execution_time
            ))

        return results