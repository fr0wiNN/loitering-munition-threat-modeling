import matplotlib.pyplot as plt
from scenario import Scenario
from typing import List, Tuple
from solvers.base import SolverResult

ICON_SIZE = 20
FONT_SIZE = 7

def plot_scenario(scenario: Scenario, assignments = None, display_range: bool = False, display_targeting:bool = False):
    plt.figure(figsize=(10, 6))
    plt.title(f"Scenario: {scenario.name}")

    plt.xlim(0, scenario.width)
    plt.ylim(0, scenario.height)

    for asset in scenario.assets:
        plt.scatter(asset.x, asset.y, color='blue', marker='s', s=ICON_SIZE, label='Asset')
        plt.text(asset.x, asset.y + 5, asset.name, fontsize=FONT_SIZE, ha='center')

    for threat in scenario.threats:
        plt.scatter(threat.x, threat.y, color='red', marker='o', s=ICON_SIZE, label='Threat')
        plt.text(threat.x, threat.y + 5, threat.name, fontsize=FONT_SIZE, ha='center')

        if display_targeting:
            plt.plot(
                [threat.x, threat.target.x],
                [threat.y, threat.target.y],
                color='red',
                linestyle=':',
                alpha=0.4,
                linewidth=1.0,
                label='Threat Targeting'
            )

    for weapon in scenario.weapons:
        plt.scatter(weapon.x, weapon.y, color='green', marker='^', s=ICON_SIZE, label='Weapon')
        plt.text(weapon.x, weapon.y + 5, weapon.name, fontsize=FONT_SIZE, ha='center')

        if display_range:
            range_circle = plt.Circle(
                (weapon.x, weapon.y),
                radius=weapon.engage_range,
                color='green',
                fill=False,
                alpha=1,
                linestyle='-',
                linewidth=0.2
            )
            plt.gca().add_patch(range_circle)

    if assignments is not None:
        for weapon, threat in assignments:
            plt.plot(
                [weapon.x, threat.x],
                [weapon.y, threat.y],
                color='blue',
                linestyle='-',
                alpha=0.5,
                linewidth=1.0,
                label='Engagement'
            )

    # Remove duplicate labels in the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
