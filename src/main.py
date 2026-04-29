from scenario import Scenario, ScenarioGenerator
from models import Threat
from visualization import plot_scenario
from models.threat_collection import SHA
from models.asset_collection import HQ
from models.weapon_collection import Patriot
from solvers.greedy import GreedyMMRSolver

if __name__ == '__main__':
    # === INITIALIZE SCENARIO ===
    scenario = Scenario(name="Example Scenario", width=450.0, height=200.0)
    generator = ScenarioGenerator()

    # === CREATE ENTITIES ===
    assets = generator.generate_asset_cluster(
        center_x=150.0,
        center_y=30.0,
        radius=10.0,
        amount=3,
        asset_class=HQ
    )

    threats = generator.generate_threat_cluster(
        center_x=100.0,
        center_y=130.0,
        radius=30.0,
        amount=10,
        threat_class=SHA,
        target_pool=assets
    )

    weapons = generator.generate_weapon_cluster(
        center_x=250.0,
        center_y=40.0,
        radius=20.0,
        amount=5,
        weapon_class=Patriot
    )

    # === PACK ENTITIES INTO SCENARIO ===
    scenario.add_assets(*assets)
    scenario.add_threats(*threats)
    scenario.add_weapons(*weapons)

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === SOLVE AND PRINT THE METRICS ===
    greedy_solver = GreedyMMRSolver()
    result = greedy_solver.solve(scenario)

    print("=== GREEDY SOLVER RESULTS ===")
    print(f"Total Cost: ${result.total_engagement_cost:,.2f}")
    print(f"Asset Loss: ${result.expected_asset_loss:,.2f}")
    print(f"Compute Time: {result.execution_time_seconds:.4f}s")

    # === VISUALIZE ===
    plot_scenario(scenario, display_range=True, display_targeting=True, assignments=result.assignments)