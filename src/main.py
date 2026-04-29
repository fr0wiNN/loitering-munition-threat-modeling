from scenario import Scenario
from models import Asset, Threat
from visualization import plot_scenario
from models.weapon_collection import Patriot, Strela
from solvers.greedy import GreedyMMRSolver

if __name__ == '__main__':
    # === INITIALIZE SCENARIO ===
    scenario = Scenario(name="Example Scenario", width=450.0, height=200.0)

    # === CREATE ENTITIES ===
    hq_1 = Asset(name="HQ-1", x=160.0, y=25.0, value=500_000)
    hq_2 = Asset(name="HQ-2", x=180.0, y=20.0, value=600_000)

    drone_1 = Threat(name="SHA-136-1", x=100.0, y=150.0, target=hq_1)
    drone_2 = Threat(name="SHA-136-2", x=115.0, y=130.0, target=hq_2)

    patriot = Patriot(x=250.0, y=25)
    strela = Strela(x=220.0, y=20)

    # === PACK ENTITIES INTO SCENARIO ===
    scenario.add_assets(hq_1, hq_2)
    scenario.add_threats(drone_1, drone_2)
    scenario.add_weapons(patriot, strela)

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
    plot_scenario(scenario, assignments=result.assignments, display_range=True)