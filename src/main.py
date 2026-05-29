from scenario import Scenario, ScenarioGenerator
from models import Threat
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import random
from pymoo.indicators.hv import Hypervolume
from visualization import plot_scenario, plot_pareto_comparison
from models.threat_collection import SHA
from models.asset_collection import HQ, OilRefinery
from models.weapon_collection import Patriot, Strela
from solvers import WTAModel, GreedyMMRSolver, NSGAIISolver, RandomSolver
from scenario import build_odesa_scenario, build_parametric_scenario

def run_testing():
    # === INITIALIZE SCENARIO ===
    scenario = build_odesa_scenario()
    #scenario = build_parametric_scenario(500, 0.25, "Uniform")

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === CONVERT SCENARIO TO A MODEL ===
    model = WTAModel.from_scenario(scenario)

    # === SOLVE WITH GREEDY ===
    print("\n--- Running Greedy Baseline ---")
    greedy_solver = GreedyMMRSolver()
    greedy_result = greedy_solver.solve(model)[0]

    # === CONFIGURE GA SOLVERS ===
    ga_configs = {
        # "Fast GA (20x20)": NSGAIISolver(pop_size=20, n_gen=20, seed=420),
        f"Fast GA (100x200)": NSGAIISolver(pop_size=20, n_gen=20, seed=420),
        "Medium GA (50x50)": NSGAIISolver(pop_size=50, n_gen=50, seed=420),
        "Heavy GA (100x200)": NSGAIISolver(pop_size=100, n_gen=200, seed=420)
        # "Super Heavy GA (200x400)": NSGAIISolver(pop_size=200, n_gen=400, seed=420),
        # "Random (200x400)": RandomSolver(n_trials=200 * 400, seed=420)
    }

    # === RUN EXPERIMENTS ===
    pareto_fronts = {}

    for label, solver in ga_configs.items():
        print(f"--- Running {label} ---")
        pareto_fronts[label] = solver.solve(model=model)

    # === VISUALIZE ===
    plot_pareto_comparison(pareto_fronts)

    # plot_scenario(scenario, decision_matrix=pareto_fronts.get("Super Heavy GA (200x400)")[0].decision_matrix)
    # plot_scenario(scenario, decision_matrix=pareto_fronts.get("Super Heavy GA (200x400)")[8].decision_matrix)
    # plot_scenario(scenario, decision_matrix=pareto_fronts.get("Super Heavy GA (200x400)")[-1].decision_matrix)
    print(f"Pareto points: {len(pareto_fronts.get(f"Fast GA 0 (100x200)"))}")
    for i in pareto_fronts.get(f"Fast GA 0 (100x200)"):
        print(i)
        print(i.decision_matrix)
        plot_scenario(scenario, display_map=False, display_names=True,
                      decision_matrix=i.decision_matrix)
    # plot_scenario(scenario, display_map=False, display_names=True, decision_matrix=pareto_fronts.get("Fast GA 0 (100x200)")[4].decision_matrix)


def run_parametric_study():
    # Variables
    swarm_sizes = [50, 100, 500, 1000]
    scarcity_ratios = [0.25, 0.50, 0.80]
    distributions = ["Uniform", "Concentrated"]

    # Set to 30 for final thesis data
    num_runs = 2

    # Ensure output directory exists
    output_dir = "data/raw_matrices"
    os.makedirs(output_dir, exist_ok=True)

    registry_data = []

    for run_seed in range(num_runs):
        print(f"\n{'=' * 15} RUN {run_seed + 1} / {num_runs} {'=' * 15}")

        for size in swarm_sizes:
            for ratio in scarcity_ratios:
                for dist in distributions:
                    print(f"Generating: Size={size}, Ratio={ratio}, Dist={dist}, Seed={run_seed}")

                    # Build Environment
                    scenario = build_parametric_scenario(
                        target_drones=size,
                        ammo_ratio=ratio,
                        distribution=dist
                    )
                    model = WTAModel.from_scenario(scenario)

                    # Configure Solvers
                    solvers = {
                        "Greedy": GreedyMMRSolver(),
                        "Random_Fast": RandomSolver(n_trials=400, seed=run_seed),
                        "NSGA_Fast": NSGAIISolver(pop_size=20, n_gen=20, seed=run_seed),
                        "NSGA_Medium": NSGAIISolver(pop_size=50, n_gen=50, seed=run_seed),
                        "NSGA_Heavy": NSGAIISolver(pop_size=100, n_gen=200, seed=run_seed)
                    }

                    scenario_raw_results = {}
                    scenario_id = f"S{size}_R{ratio}_D{dist}_Seed{run_seed}"

                    # Execute Solvers
                    for solver_name, solver in solvers.items():
                        start_time = time.time()
                        front = solver.solve(model)
                        exec_time = time.time() - start_time

                        # Store the raw SolverResult objects (which contain the matrices)
                        scenario_raw_results[solver_name] = front

                        # Log the metadata and execution time to our registry
                        registry_data.append({
                            "Scenario_ID": scenario_id,
                            "Swarm_Size": size,
                            "Ammo_Ratio": ratio,
                            "Distribution": dist,
                            "Seed": run_seed,
                            "Solver": solver_name,
                            "Execution_Time_s": exec_time,
                            "Pareto_Length": len(front)
                        })

                    # Dump the raw matrices to disk via pickle
                    with open(f"{output_dir}/{scenario_id}.pkl", "wb") as f:
                        pickle.dump(scenario_raw_results, f)

    # Export the registry DataFrame to CSV
    print("\nSaving simulation registry...")
    pd.DataFrame(registry_data).to_csv(f"{output_dir}/simulation_registry.csv", index=False)

    print("Raw Data Generation Complete!")


def process_metrics():
    print("Loading simulation registry...")
    registry_path = "data/raw_matrices/simulation_registry.csv"
    if not os.path.exists(registry_path):
        print("Error: Registry not found. Run Phase 1 first.")
        return

    registry_df = pd.read_csv(registry_path)
    os.makedirs("data/results", exist_ok=True)

    unique_scenarios = registry_df.drop_duplicates(subset=["Scenario_ID"])

    run_stats = []
    pareto_points = []
    observer_stats = []

    print(f"Processing metrics for {len(unique_scenarios)} unique scenarios...")

    for _, row in unique_scenarios.iterrows():
        scenario_id = row["Scenario_ID"]
        size, ratio, dist, run_seed = row["Swarm_Size"], row["Ammo_Ratio"], row["Distribution"], row["Seed"]

        # 1. Rebuild exact model to calculate metrics
        np.random.seed(run_seed)
        random.seed(run_seed)
        scenario = build_parametric_scenario(target_drones=size, ammo_ratio=ratio, distribution=dist)
        model = WTAModel.from_scenario(scenario)

        max_cost = sum(model.weapon_capacities[i] * model.weapon_costs[i] for i in range(model.num_weapons))
        max_loss = sum(model.asset_values)
        hv_metric = Hypervolume(ref_point=np.array([max_cost, max_loss]))

        # 2. Load the raw generated matrices
        with open(f"data/raw_matrices/{scenario_id}.pkl", "rb") as f:
            scenario_results = pickle.load(f)

        # 3. Extract Metrics per Solver
        for solver_name, front in scenario_results.items():
            # Get execution time from registry
            exec_time = registry_df[(registry_df["Scenario_ID"] == scenario_id) &
                                    (registry_df["Solver"] == solver_name)]["Execution_Time_s"].values[0]

            hv_score = 0.0
            if len(front) > 0:
                F = np.array([[res.engagement_cost, res.expected_asset_loss] for res in front])
                if np.all(F <= np.array([max_cost, max_loss])):
                    hv_score = hv_metric.do(F)

                for point in front:
                    pareto_points.append({
                        "Swarm_Size": size, "Ammo_Ratio": ratio, "Distribution": dist,
                        "Seed": run_seed, "Solver": solver_name,
                        "Engagement_Cost": point.engagement_cost, "Expected_Loss": point.expected_asset_loss
                    })

            run_stats.append({
                "Swarm_Size": size, "Ammo_Ratio": ratio, "Distribution": dist,
                "Seed": run_seed, "Solver": solver_name,
                "Execution_Time_s": exec_time, "Pareto_Length": len(front),
                "Hypervolume": hv_score
            })

        # 4. Calculate RQ3 MSE (Only for Concentrated)
        if dist == "Concentrated":
            # Greedy
            greedy_front = scenario_results.get("Greedy", [])
            if greedy_front:
                mse = calculate_informed_observer_mse(model, greedy_front[0].decision_matrix)
                observer_stats.append(
                    {"Strategy": "Greedy (Deterministic)", "MSE": mse, "Swarm_Size": size, "Ratio": ratio})

            # NSGA-II Heavy Samples
            nsga_front = scenario_results.get("NSGA_Heavy", [])
            if nsga_front:
                sorted_front = sorted(nsga_front, key=lambda x: x.engagement_cost)

                # Median
                mse_median = calculate_informed_observer_mse(model,
                                                             sorted_front[len(sorted_front) // 2].decision_matrix)
                observer_stats.append(
                    {"Strategy": "NSGA-II (Median Sample)", "MSE": mse_median, "Swarm_Size": size, "Ratio": ratio})

                # Random
                random_idx = random.randint(0, len(sorted_front) - 1)
                mse_random = calculate_informed_observer_mse(model, sorted_front[random_idx].decision_matrix)
                observer_stats.append(
                    {"Strategy": "NSGA-II (Random Sample)", "MSE": mse_random, "Swarm_Size": size, "Ratio": ratio})

    # Save final CSVs
    print("Saving final results...")
    pd.DataFrame(run_stats).to_csv("data/results/experiment_stats.csv", index=False)
    pd.DataFrame(pareto_points).to_csv("data/results/pareto_points.csv", index=False)
    pd.DataFrame(observer_stats).to_csv("data/results/observer_mse_stats.csv", index=False)
    print("Data processing complete! Check data/results/ folder.")


def calculate_informed_observer_mse(model: WTAModel, X: np.ndarray) -> float:
    """Calculates the MSE for Strategic Ambiguity (RQ3)"""
    V = model.asset_values
    E = np.zeros(model.num_assets)

    for k in range(model.num_assets):
        threats_k = model.target_map.get(k, [])
        if not threats_k:
            continue
        cost_matrix = model.weapon_costs[:, np.newaxis] * X[:, threats_k]
        E[k] = np.sum(cost_matrix)

    def normalize(arr):
        min_val, max_val = np.min(arr), np.max(arr)
        if max_val - min_val == 0:
            return np.zeros_like(arr) if max_val == 0 else np.ones_like(arr)
        return (arr - min_val) / (max_val - min_val)

    V_norm = normalize(V)
    E_norm = normalize(E)
    return float(np.mean((V_norm - E_norm) ** 2))


def get_table_1_execution_times(df_exp):
    print("\n" + "=" * 50)
    print("TABLE 1 & SECTION 4.1: EXECUTION LATENCY")
    print("=" * 50)

    # Pivot table to get average execution time by Solver and Swarm Size
    exec_pivot = df_exp.pivot_table(
        index="Solver",
        columns="Swarm_Size",
        values="Execution_Time_s",
        aggfunc="mean"
    )

    # Reorder rows to match your LaTeX table
    row_order = ["Greedy", "Random_Fast", "NSGA_Fast", "NSGA_Medium", "NSGA_Heavy"]
    exec_pivot = exec_pivot.reindex(row_order)

    print("--- Table 1 Data (Seconds) ---")
    print(exec_pivot.round(2).to_string())

    print("\n--- Section 4.1 Text Placeholders ---")
    try:
        fast_1000 = exec_pivot.loc["NSGA_Fast", 1000]
        heavy_1000 = exec_pivot.loc["NSGA_Heavy", 1000]
        print(f"NSGA-II Fast at |T|=1000:  {fast_1000:.2f}")
        print(f"NSGA-II Heavy at |T|=1000: {heavy_1000:.2f}")
    except KeyError:
        print("Data for |T|=1000 not found yet.")


def process_section_4_2():
    df = pd.read_csv("data/results/experiment_stats.csv")

    # 2. Get the average Pareto length for all NSGA runs
    avg_pareto = df[df["Solver"].str.contains("NSGA")]["Pareto_Length"].mean()
    print(f"[INSERT NUMBER] Average unique solutions: {avg_pareto:.0f}")

    # 3. Filter for the specific scenario you are writing about (T=500, ratio=0.25)
    df_500 = df[(df["Swarm_Size"] == 500) & (df["Ammo_Ratio"] == 0.25)]

    # 4. Get the average Hypervolume for Fast and Heavy
    hv_fast = df_500[df_500["Solver"] == "NSGA_Fast"]["Hypervolume"].mean()
    hv_heavy = df_500[df_500["Solver"] == "NSGA_Heavy"]["Hypervolume"].mean()

    # 5. Calculate the % improvement
    improvement = ((hv_heavy - hv_fast) / hv_fast) * 100 if hv_fast > 0 else 0

    print(f"[X.XX] Fast Configuration HV:  {hv_fast:.2e}")
    print(f"[X.XX] Heavy Configuration HV: {hv_heavy:.2e}")
    print(f"[X.X]% Mathematical Improvement: {improvement:.1f}%")

if __name__ == '__main__':
    #run_parametric_study()
    #process_metrics()
    run_testing()
    #df_exp = pd.read_csv("data/results/pareto_points.csv")
    #process_section_4_2()