import numpy as np
from dataclasses import dataclass
from typing import List, Dict

from scenario import Scenario


@dataclass
class WTAModel:
    # Dimensions
    num_weapons: int
    num_threats: int
    num_assets: int

    # Parameter Arrays (1D)
    asset_values: np.ndarray
    weapon_costs: np.ndarray
    weapon_capacities: np.ndarray

    # Probability Matrix (2D)
    kill_probs: np.ndarray

    # Targeting Mapping (What indexes of assets are being targeted by which threats)
    target_map: Dict[int, List[int]]

    @classmethod
    def from_scenario(cls, scenario: Scenario) -> 'WTAModel':
        """Builds the math model from a Scenario"""
        W = len(scenario.weapons)
        T = len(scenario.threats)
        A = len(scenario.assets)

        # 1D Parameters
        asset_values = np.array([a.value for a in scenario.assets])
        weapon_costs = np.array([w.usage_cost for w in scenario.weapons])
        weapon_capacities = np.array([w.capacity for w in scenario.weapons])

        # Build Target Map
        target_map = {k: [] for k in range(A)}
        for j, threat in enumerate(scenario.threats):
            if hasattr(threat, 'target') and threat.target in scenario.assets:
                k = scenario.assets.index(threat.target)
                target_map[k].append(j)

        # Build Probability Matrix
        kill_probs = np.zeros((W, T))
        for i, weapon in enumerate(scenario.weapons):
            for j, threat in enumerate(scenario.threats):
                if weapon.is_in_range(threat):
                    kill_probs[i, j] = weapon.kill_prob

        return cls(
            num_weapons=W,
            num_threats=T,
            num_assets=A,
            asset_values=asset_values,
            weapon_costs=weapon_costs,
            weapon_capacities=weapon_capacities,
            kill_probs=kill_probs,
            target_map=target_map
        )

    def evaluate_engagement_cost(self, X: np.ndarray) -> float:
        """
        Calculates the engagement cost.

        :param X: Decision matrix of shape (num_weapons, num_threats)
        :return: Total engagement costs of executing the assignment
        """
        engagement_cost = np.sum(self.weapon_costs[:, np.newaxis] * X)
        return float(engagement_cost)

    def evaluate_expected_asset_loss(self, X: np.ndarray) -> float:
        """
        Calculates the expected asset loss.

        :param X: Decision matrix of shape (num_weapons, num_threats)
        :return: Expected asset loss in dollars
        """

        expected_loss = 0.0

        for k in range(self.num_assets):
            asset_value = self.asset_values[k]

            # Use .get() just in case an asset has no threats mapped to it yet
            attacking_threats = self.target_map.get(k, [])

            if not attacking_threats:
                continue

            asset_survival_prob = 1.0

            for j in attacking_threats:
                threat_survival_prob = np.prod((1.0 - self.kill_probs[:, j]) ** X[:, j])
                threat_destroyed_prob = 1.0 - threat_survival_prob
                asset_survival_prob *= threat_destroyed_prob

            asset_destroyed_prob = 1.0 - asset_survival_prob
            expected_loss += asset_value * asset_destroyed_prob

        return float(expected_loss)