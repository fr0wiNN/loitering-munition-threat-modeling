import numpy as np
import matplotlib.pyplot as plt
import contextily as cx
from scenario import Scenario
from typing import List, Tuple

ICON_SIZE = 19
FONT_SIZE = 6

def plot_scenario(scenario: Scenario, decision_matrix: np.ndarray = None, display_range: bool = True,
                  display_targeting: bool = True, display_map: bool = False, display_names:bool = True):
    sw_lat, sw_lon = scenario.sw_latlon
    ne_lat, ne_lon = scenario.ne_latlon

    # Calculate the exact aspect ratio of the geographic data
    width_deg = ne_lon - sw_lon
    height_deg = ne_lat - sw_lat
    aspect_ratio = width_deg / height_deg

    # Set the figure size dynamically (e.g., base height of 7 inches, scaled width)
    plt.figure(figsize=(7 * aspect_ratio, 7))
    plt.title(f"Scenario: {scenario.name}")

    # Longitude is the X-axis, Latitude is the Y-axis
    plt.xlim(sw_lon, ne_lon)
    plt.ylim(sw_lat, ne_lat)

    # Calculate a tiny dynamic offset for text labels (2% of the map height)
    y_offset = (ne_lat - sw_lat) * 0.02

    for asset in scenario.assets:
        plt.scatter(asset.lon, asset.lat, color='blue', marker='s', s=ICON_SIZE, label='Asset')
        if display_names:
            plt.text(asset.lon, asset.lat + y_offset, asset.name, fontsize=FONT_SIZE, ha='center')

    for threat in scenario.threats:
        plt.scatter(threat.lon, threat.lat, color='red', marker='o', s=ICON_SIZE, label='Threat')
        if display_names:
            plt.text(threat.lon, threat.lat + y_offset, threat.name, fontsize=FONT_SIZE, ha='center')

        if display_targeting:
            plt.plot(
                [threat.lon, threat.target.lon],
                [threat.lat, threat.target.lat],
                color='red',
                linestyle=':',
                alpha=0.3,
                linewidth=1.0,
                label='Threat Targeting'
            )

    for weapon in scenario.weapons:
        plt.scatter(weapon.lon, weapon.lat, color='green', marker='^', s=ICON_SIZE, label='Weapon')
        if display_names:
            plt.text(weapon.lon, weapon.lat + y_offset, weapon.name, fontsize=FONT_SIZE, ha='center')

        if display_range:
            # Convert the radius from meters to degrees for the plot
            # (1 degree of latitude is roughly 111,320 meters)
            radius_deg = weapon.engage_range / 111320.0

            range_circle = plt.Circle(
                (weapon.lon, weapon.lat),
                radius=radius_deg,
                color='green',
                fill=False,
                alpha=1,
                linestyle='-',
                linewidth=0.2
            )
            plt.gca().add_patch(range_circle)

    if decision_matrix is not None:
        for i, weapon in enumerate(scenario.weapons):
            for j, threat in enumerate(scenario.threats):
                shots_fired = int(decision_matrix[i, j])

                if shots_fired > 0:
                    plt.plot(
                        [weapon.lon, threat.lon],
                        [weapon.lat, threat.lat],
                        color='blue',
                        linestyle='-',
                        alpha=0.5,
                        linewidth=1.0,
                        label='Engagement'
                    )

                    if shots_fired > 1:
                        mid_lon = (weapon.lon + threat.lon) / 2
                        mid_lat = (weapon.lat + threat.lat) / 2
                        plt.text(
                            mid_lon, mid_lat,
                            f"{shots_fired}x",
                            color='blue',
                            fontsize=FONT_SIZE,
                            weight='bold',
                            ha='center'
                        )

    # Remove duplicate labels in the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    if labels:
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.grid(True, linestyle=':', alpha=0.6)

    plt.gca().set_aspect('equal', adjustable='box')

    if display_map:
        cx.add_basemap(
            plt.gca(),
            crs="EPSG:4326",
            source=cx.providers.OpenStreetMap.Mapnik,
            alpha=0.5,
            zoom_adjust=1
        )

    plt.tight_layout()
    plt.show()

def plot_pareto_comparison(pareto_fronts: dict, baseline=None):
    """
    Plots an arbitrary number of Pareto fronts for easy comparison.

    :param pareto_fronts: Dictionary mapping labels to a list of SolverResults
                          e.g., {"Fast GA": results_1, "Heavy GA": results_2}
    :param baseline: A single SolverResult to plot as the starting point (e.g., Greedy)
    """
    plt.figure(figsize=(10, 6))

    # A color/marker palette to cycle through dynamically
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan']
    markers = ['o', 's', '^', 'D', 'v', '<']

    # Loop through whatever dictionary of results the user passes in
    for i, (label, results) in enumerate(pareto_fronts.items()):
        if not results:
            continue

        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]

        costs = [r.engagement_cost for r in results]
        losses = [r.expected_asset_loss for r in results]

        plt.plot(costs, losses, color=color, linestyle='--', alpha=0.4)
        plt.scatter(costs, losses, color=color, marker=marker, label=label, s=60, alpha=0.8, zorder=5)

    # Plot the Baseline/Seed if provided
    if baseline:
        plt.scatter(
            [baseline.engagement_cost],
            [baseline.expected_asset_loss],
            color='gold',
            marker='*',
            s=300,
            edgecolors='black',
            label=f'{baseline.solver_name} (Baseline)',
            zorder=10
        )

    plt.title("NSGA-II Hyperparameter Comparison vs Baseline", fontsize=14, weight='bold')
    plt.xlabel("Engagement Cost ($)", fontsize=12)
    plt.ylabel("Expected Asset Loss ($)", fontsize=12)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))

    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(fontsize=11, loc='upper right')
    plt.tight_layout()
    plt.show()
