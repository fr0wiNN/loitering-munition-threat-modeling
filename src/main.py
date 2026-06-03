import pandas as pd
import numpy as np
import random
from pymoo.indicators.hv import Hypervolume
from visualization import plot_scenario, plot_pareto_comparison
from scipy import stats
from solvers import WTAModel, WeightedGreedyMMRSolver, NSGAIISolver, RandomSolver
from scenario import build_parametric_scenario

def run_demo():

    # === INITIALIZE SCENARIO ===
    scenario = build_parametric_scenario(50, 0.25, "Uniform")

    plot_scenario(scenario, display_range=False)

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === CONVERT SCENARIO TO A MODEL ===
    model = WTAModel.from_scenario(scenario)

    # === CONFIGURE SOLVERS ===
    configs = {
        "Fast GA (100x200)": NSGAIISolver(pop_size=20, n_gen=20, seed=420),
        "Medium GA (50x50)": NSGAIISolver(pop_size=50, n_gen=50, seed=420),
        "Heavy GA (100x200)": NSGAIISolver(pop_size=100, n_gen=200, seed=420),
        "Greedy": WeightedGreedyMMRSolver([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
        "Random": RandomSolver(100*200)
    }

    # === RUN EXPERIMENTS ===
    pareto_fronts = {}

    for label, solver in configs.items():
        print(f"--- Running {label} ---")
        pareto_fronts[label] = solver.solve(model=model)

    # === VISUALIZE ===
    plot_pareto_comparison(pareto_fronts)
    plot_scenario(scenario)

def run_rq_1(n_runs, configs):
    print("=== STARTING RQ1 ===")

    threat_sizes = [50, 100, 500, 1000]
    rq_1_results_data = []
    fixed_rho_ratio = 0.25

    for size in threat_sizes:
        for run in range(n_runs):
            print(f"\r  [Swarm: {size:<4}] Processing Run {run + 1}/{n_runs}")

            scenario = build_parametric_scenario(size, fixed_rho_ratio, "Uniform", run)
            model = WTAModel.from_scenario(scenario)

            for label, solver in configs.items():
                pareto_front = solver.solve(model)

                exec_time = pareto_front[0].execution_time_s

                rq_1_results_data.append({
                    "swarm_size": size,
                    "algorithm": label,
                    "run_id": run,
                    "exec_time_s": exec_time
                })

    pd.DataFrame(rq_1_results_data).to_csv(f"data/rq1.csv", index=False)

def run_rq_2(n_runs, configs):
    # === RQ2 ===
    print("=== STARTING RQ2 ===")

    rho_values = [0.25, 0.50, 0.80]
    rq_2_results_data = []
    fixed_swarm_size = 500

    for rho in rho_values:
        for run in range(n_runs):
            print(f"\r  [Rho: {rho:<4.2f}] Processing Run {run + 1}/{n_runs}")

            scenario = build_parametric_scenario(fixed_swarm_size, rho, "Uniform", run)
            model = WTAModel.from_scenario(scenario)

            # Define the Worst-Case Reference Point for HV
            max_possible_cost = sum(model.weapon_costs[i] * model.weapon_capacities[i] for i in range(model.num_weapons))
            max_possible_loss = sum(model.asset_values)

            ref_point = np.array([max_possible_cost * 1.01, max_possible_loss * 1.01])
            hv_calculator = Hypervolume(ref_point=ref_point)

            for label, solver in configs.items():
                pareto_front = solver.solve(model)

                objective_points = np.array([
                    [res.engagement_cost, res.expected_asset_loss] for res in pareto_front
                ])

                hv_score = hv_calculator.do(objective_points)

                rq_2_results_data.append({
                    "scarcity_rho": rho,
                    "algorithm": label,
                    "run_id": run,
                    "hv_score": hv_score
                })

    pd.DataFrame(rq_2_results_data).to_csv(f"data/rq2.csv", index=False)

def run_rq_3(n_runs, configs):
    # === RQ3 ===
    print("=== STARTING RQ3 ===")

    distributions = ["Uniform", "Concentrated"]
    rq_3_results_data = []
    fixed_swarm_size = 500
    fixed_rho_ratio = 0.50

    for dist in distributions:
        for run in range(n_runs):
            print(f"\r  [Dist: {dist:<12}] Processing Run {run + 1}/{n_runs}")

            scenario = build_parametric_scenario(fixed_swarm_size, fixed_rho_ratio, dist, run)
            model = WTAModel.from_scenario(scenario)

            true_values = model.asset_values

            for label, solver in configs.items():
                pareto_front = solver.solve(model)

                sorted_front = sorted(pareto_front, key=lambda res: res.engagement_cost)

                samples_to_test = {}
                if "Greedy" in label:
                    traditional_greedy_result = sorted_front[-1]
                    samples_to_test["Deterministic_Greedy"] = traditional_greedy_result
                elif "Random" in label:
                    samples_to_test["Random_Baseline"] = random.choice(sorted_front)
                else:
                    samples_to_test["Median_Pareto"] = sorted_front[len(sorted_front) // 2]
                    samples_to_test["Random_Pareto"] = random.choice(sorted_front)

                for sample_label, result in samples_to_test.items():
                    X = result.decision_matrix

                    estimated_values = np.zeros(model.num_assets)

                    for k, targeted_threats in model.target_map.items():
                        cost_spent_on_k = 0
                        for j in targeted_threats:
                            for i in range(model.num_weapons):
                                cost_spent_on_k += X[i, j] * model.weapon_costs[i]
                        estimated_values[k] = cost_spent_on_k

                    tv_array = np.asarray(true_values, dtype=float).flatten()
                    ev_array = np.asarray(estimated_values, dtype=float).flatten()

                    if np.all(tv_array == tv_array[0]) or np.all(ev_array == ev_array[0]):
                        # If the solver fired 0 interceptors (or spent the exact same on everything),
                        # the adversary learns nothing. Correlation is 0.
                        correlation = 0.0
                    else:
                        # 3. Safe calculation
                        correlation, p_value = stats.spearmanr(tv_array, ev_array)

                        # Fallback for any other weird math edge cases
                        if np.isnan(correlation):
                            correlation = 0.0

                    rq_3_results_data.append({
                        "targeting_dist": dist,
                        "algorithm": label,
                        "strategy_sampled": sample_label,
                        "run_id": run,
                        "spearman_rs": correlation,
                    })

    pd.DataFrame(rq_3_results_data).to_csv("data/rq3.csv", index=False)

if __name__ == '__main__':

    # === RUN DEMO ===
    run_demo()

    # === RUN EXPERIMENTS ===
    # n_runs = 5

    #configs = {
    #    "Fast GA (100x200)": NSGAIISolver(pop_size=20, n_gen=20, seed=420),
    #    "Medium GA (50x50)": NSGAIISolver(pop_size=50, n_gen=50, seed=420),
    #    "Heavy GA (100x200)": NSGAIISolver(pop_size=100, n_gen=200, seed=420),
    #    "Greedy": WeightedGreedyMMRSolver([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
    #    "Random": RandomSolver(100 * 200)
    #}

    # run_rq_1(n_runs, configs)
    # run_rq_2(n_runs, configs)
    # run_rq_3(n_runs, configs)