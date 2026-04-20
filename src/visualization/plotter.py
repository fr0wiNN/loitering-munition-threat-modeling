import matplotlib.pyplot as plt
from scenario import Scenario

ICON_SIZE = 20
FONT_SIZE = 7

def plot_scenario(scenario: Scenario):
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

        target = threat.target
        plt.plot([threat.x, target.x], [threat.y, target.y], 'r--', alpha=0.3)

    for weapon in scenario.weapons:
        plt.scatter(weapon.x, weapon.y, color='green', marker='^', s=ICON_SIZE, label='Weapon')
        plt.text(weapon.x, weapon.y + 5, weapon.name, fontsize=FONT_SIZE, ha='center')

    # Remove duplicate labels in the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.show()
