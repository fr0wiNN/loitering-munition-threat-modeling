from scenario import Scenario, ScenarioGenerator
from models import Threat
from visualization import plot_scenario
from models.threat_collection import SHA
from models.asset_collection import HQ, OilRefinery
from models.weapon_collection import Patriot, Strela
from solvers.greedy import GreedyMMRSolver

if __name__ == '__main__':
    # === INITIALIZE SCENARIO ===
    scenario = Scenario(name="Example Scenario", width=450.0, height=250.0)
    generator = ScenarioGenerator()

    # === CREATE ENTITIES ===

    weapons = generator.generate_weapon_cluster(
        center_x=250.0,
        center_y=40.0,
        radius=20.0,
        amount=3,
        weapon_class=Patriot
    )

    # HQ's each worth 500,000
    assets_1 = generator.generate_asset_cluster(
        center_x=150.0,
        center_y=30.0,
        radius=10.0,
        amount=3,
        asset_class=HQ
    )

    # 1st swarm
    threats_1 = generator.generate_threat_cluster(
        center_x=100.0,
        center_y=130.0,
        radius=30.0,
        amount=12,
        threat_class=SHA,
        target_pool=assets_1
    )

    # Oil refinery plant
    assets_2 = generator.generate_asset_cluster(
        center_x=350.0,
        center_y=50.0,
        radius=30.0,
        amount=3,
        asset_class=OilRefinery
    )

    # 2nd swarm targeting the plant
    threats_2 = generator.generate_threat_cluster(
        center_x=330.0,
        center_y=175.0,
        radius=30.0,
        amount=12,
        threat_class=SHA,
        target_pool=assets_2
    )

    threats_2 = []

    # === PACK ENTITIES INTO SCENARIO ===
    scenario.add_assets(*assets_1, *assets_2)
    scenario.add_threats(*threats_1, *threats_2)
    scenario.add_weapons(*weapons)

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === SOLVE AND PRINT THE METRICS ===
    greedy_solver = GreedyMMRSolver()
    result = greedy_solver.solve(scenario)

    print("=== GREEDY SOLVER RESULTS ===")
    print(f"Total Cost: ${result.total_engagement_cost:,.2f}")
    print(f"Expected Asset Loss: ${result.expected_asset_loss:,.2f}")
    print(f"Compute Time: {result.execution_time_seconds:.4f}s")

    # === VISUALIZE ===
    plot_scenario(scenario, display_range=True, display_targeting=True, assignments=result.assignments)