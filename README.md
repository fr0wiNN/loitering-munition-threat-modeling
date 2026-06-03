# Multi-Objective AB-WTA Simulation Framework

BSc Computer Science Thesis Repository  
Author: Maksymilian Gach
Institution: Maastricht University, Department of Advanced Computing Sciences

This repository contains the simulation framework and optimization codebase for the thesis: "Multi-Objective Asset-Based Weapon-Target Assignment Modeling For Cost-Effective Defense Against Loitering Munition Swarms".

It provides a modular, object-oriented Python environment to evaluate algorithms for optimizing air defense resource allocation during asymmetric saturation attacks.

## Code Architecture

Framework strictly isolates the physical battlefield simulation from the optimization logic. The execution pipeline follows a strict object transition: Scenario -> Model -> Solver.

### Execution Pipeline
Every experiment in this codebase follows this core paradigm. A physical scenario is generated, compiled into a mathematical model, and passed to a solver:
```python
from scenario import build_odesa_scenario
from solvers import WTAModel, NSGAIISolver
from visualization import plot_scenario

# 1. GENERATE SCENARIO
# Load the predefined geographical scenario (e.g., Odesa)
scenario = build_odesa_scenario()

# 2. COMPILE MATHEMATICAL MODEL
model = WTAModel.from_scenario(scenario)

# 3. SOLVE
nsga_solver = NSGAIISolver(pop_size=100, n_gen=200)
pareto_front = nsga_solver.solve(model)

# 4. VISUALIZE
example_decision_matrix = pareto_front[0].decision_matrix
plot_scenario(scenario, example_decision_matrix)
```

### Available Solvers
All solvers inherit from a base `Solver` class and implement the `solve(model)` method, returning a list of `Result` objects (the Pareto front).

- `NSGAIISolver`: The primary genetic algorithm, configurable by population size and generations (Fast, Medium, Heavy configurations)
- `WeightedGreedyMMRSolver`: The deterministic baseline that evaluates a discrete spectrum of preference weights ($w \in [0, 1]$) to maximize marginal kinetic returns
- `RandomSolver`: Generates perfectly legal stochastic matrices to establish a non-learning computational baseline.

### Running the Experiments
The `src/main.py` script houses the test suites corresponding to the Research Questions (RQs) in the thesis:
- run_rq_1(): Benchmarks execution latency across scaling swarm sizes (up to 1,000 threats)
- run_rq_2(): Calculates the Hypervolume metrics of the objective space under varying scarcity constraints
- run_rq_3(): Executes the "Informed Observer" model to calculate the Spearman's rank correlation and evaluate strategic obfuscation.

Before executing any of the `run_rq_*` functions, the `data/` folder needs to be manually created in the root of the project. 