import random
import time
import numpy as np
from typing import List

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from .wta_model import WTAModel
from .base import BaseSolver, SolverResult


class _WTAProblem(ElementwiseProblem):
    def __init__(self, model: WTAModel):
        self.model = model
        self.W = model.num_weapons
        self.T = model.num_threats

        # 1. New DNA Length: Total number of interceptors available across all batteries
        self.n_var = int(np.sum(model.weapon_capacities))

        # 2. Map each slot in the DNA back to its parent weapon battery
        # Example: if capacities are [4, 4, 4], the map is [0,0,0,0, 1,1,1,1, 2,2,2,2]
        self.weapon_type_map = []
        for i, cap in enumerate(model.weapon_capacities):
            self.weapon_type_map.extend([i] * int(cap))

        # 3. Bounds: Each gene is a Target ID (0 to T-1).
        # The upper bound is exactly 'T', which acts as the "Hold Fire" dummy target.
        xl = np.zeros(self.n_var)
        xu = np.full(self.n_var, self.T)

        # Pure blackbox: No constraints (n_ieq_constr is gone).
        super().__init__(n_var=self.n_var, n_obj=2, xl=xl, xu=xu, vtype=int)

    def decode_chromosome(self, x: np.ndarray) -> np.ndarray:
        """Translates the 1D missile array back into the 2D assignment matrix."""
        X_matrix = np.zeros((self.W, self.T), dtype=int)
        x_int = np.round(x).astype(int)

        for k, target_idx in enumerate(x_int):
            if target_idx < self.T:  # If it is NOT the "Hold Fire" dummy target
                w_type = self.weapon_type_map[k]

                # === THE FEASIBILITY MASK FIX ===
                # Only assign the interceptor if the threat is strictly within range
                if self.model.kill_probs[w_type, target_idx] > 0.0:
                    X_matrix[w_type, target_idx] += 1

        return X_matrix

    def encode_matrix(self, X_matrix: np.ndarray) -> np.ndarray:
        """Translates a 2D Greedy assignment matrix into the 1D missile array for seeding."""
        chromosome = np.full(self.n_var, self.T, dtype=int)  # Default all genes to 'Hold Fire'

        missile_offset = 0
        for i in range(self.W):
            cap = int(self.model.weapon_capacities[i])
            current_missile = 0

            for j in range(self.T):
                shots = int(X_matrix[i, j])
                for _ in range(shots):
                    if current_missile < cap:
                        chromosome[missile_offset + current_missile] = j
                        current_missile += 1

            missile_offset += cap

        return chromosome

    def _evaluate(self, x, out, *args, **kwargs):
        # Decode the 100% legal chromosome back into a matrix format for the WTAModel
        X_matrix = self.decode_chromosome(x)

        cost = self.model.evaluate_engagement_cost(X_matrix)
        loss = self.model.evaluate_expected_asset_loss(X_matrix)

        out["F"] = [cost, loss]

class NSGAIISolver(BaseSolver):
    def __init__(self, pop_size=50, n_gen=50, seed=420):
        super().__init__(name="NSGA-II")
        self.pop_size = pop_size
        self.n_gen = n_gen
        self.seed = seed

    def solve(self, model: WTAModel, seed_matrix: np.ndarray = None) -> List[SolverResult]:
        start_time = time.time()

        if self.seed is not None:
            np.random.seed(self.seed)
            random.seed(self.seed)

        problem = _WTAProblem(model)

        # === THE HEURISTIC SEEDING ===
        X_init = np.zeros((self.pop_size, problem.n_var))
        for i in range(problem.n_var):
            X_init[:, i] = np.random.randint(problem.xl[i], problem.xu[i] + 1, size=self.pop_size)

        # Inject the Greedy baseline into slot 0
        if seed_matrix is not None:
            X_init[0] = problem.encode_matrix(seed_matrix)

        # Notice: No Repair Operator needed!
        algorithm = NSGA2(
            pop_size=self.pop_size,
            sampling=X_init
        )

        res = minimize(
            problem,
            algorithm,
            ('n_gen', self.n_gen),
            seed=self.seed,
            verbose=False
        )

        execution_time = time.time() - start_time
        pareto_results = []

        if res.X is None:
            return pareto_results

        front_x = [res.X] if res.X.ndim == 1 else res.X

        for x in front_x:
            # Decode the final outputs
            X_matrix = problem.decode_chromosome(x)

            final_cost = model.evaluate_engagement_cost(X_matrix)
            final_loss = model.evaluate_expected_asset_loss(X_matrix)

            pareto_results.append(SolverResult(
                solver_name=self.name,
                decision_matrix=X_matrix,
                engagement_cost=float(final_cost),
                expected_asset_loss=float(final_loss),
                execution_time_s=execution_time
            ))

        pareto_results.sort(key=lambda r: r.engagement_cost)

        return pareto_results