import time
from typing import Dict
from models import Weapon, Threat
from scenario import Scenario
from .base import BaseSolver, SolverResult


class GreedyMMRSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="Greedy MMR")

    def solve(self, scenario: Scenario) -> SolverResult:
        start_time = time.time()
        result = SolverResult()

        weapon_capacities: Dict[Weapon, int] = {w: w.capacity for w in scenario.weapons}
        threat_survival_probs: Dict[Threat, float] = {t: 1.0 for t in scenario.threats}

        while True:
            best_assignment = None
            max_net_benefit = 0.0

            for w in scenario.weapons:
                if weapon_capacities[w] <= 0:
                    continue

                for t in scenario.threats:
                    if w.is_in_range(t):
                        continue

                    expected_value_saved = t.value * threat_survival_probs[t] * w.kill_prob
                    net_benefit = expected_value_saved - w.usage_cost

                    if net_benefit > max_net_benefit:
                        max_net_benefit = net_benefit
                        best_assignment = (w, t)

            if best_assignment is None:
                break

            best_weapon, best_threat = best_assignment

            result.assignments.append((best_weapon, best_threat))
            result.total_engagement_cost += best_weapon.usage_cost

            weapon_capacities[best_weapon] -= 1
            threat_survival_probs[best_threat] *= (1.0 - best_weapon.kill_prob)

        for t in scenario.threats:
            result.expected_asset_loss += (t.value * threat_survival_probs[t])

        result.execution_time_seconds = time.time() - start_time
        return result
