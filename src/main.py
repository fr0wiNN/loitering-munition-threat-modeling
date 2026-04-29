from scenario import Scenario, ScenarioGenerator
from models import Threat
from visualization import plot_scenario
from models.asset_collection import HQ
from models.weapon_collection import Patriot, Strela
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

    drone_1 = Threat(name="SHA-136-1", x=100.0, y=150.0, target=assets[0])
    drone_2 = Threat(name="SHA-136-2", x=115.0, y=130.0, target=assets[1])

    weapons = generator.generate_weapon_cluster(
        center_x=250.0,
        center_y=40.0,
        radius=20.0,
        amount=5,
        weapon_class=Patriot
    )

    # === PACK ENTITIES INTO SCENARIO ===
    scenario.add_assets(*assets)
    scenario.add_threats(drone_1, drone_2)
    scenario.add_weapons(*weapons)

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === SOLVE AND PRINT THE METRICS ===
    #greedy_solver = GreedyMMRSolver()
    #result = greedy_solver.solve(scenario)
    #
    #print("=== GREEDY SOLVER RESULTS ===")
    #print(f"Total Cost: ${result.total_engagement_cost:,.2f}")
    #print(f"Asset Loss: ${result.expected_asset_loss:,.2f}")
    #print(f"Compute Time: {result.execution_time_seconds:.4f}s")

    # === VISUALIZE ===
    #plot_scenario(scenario, assignments=result.assignments, display_range=True)
    plot_scenario(scenario, display_range=True)