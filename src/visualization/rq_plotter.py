import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_rq_2(csv_path):
    # 1. Load the data
    df = pd.read_csv(csv_path)

    # 2. THE FIX for flat boxes: Transform data to Log10 mathematically
    df['hv_log10'] = np.log10(df['hv_score'])

    # 3. Set up the visual style
    plt.figure(figsize=(10, 6))

    # 4. THE FIX for the crash: These MUST match the CSV strings exactly
    algo_order = [
        "Random",
        "Fast GA (100x200)",
        "Medium GA (50x50)",
        "Heavy GA (100x200)",
        "Greedy"
    ]
    custom_colors = ["gray", "blue", "green", "purple", "red"]

    # 5. Draw the grouped boxplot using the Log10 column
    sns.boxplot(
        data=df,
        x="scarcity_rho",
        y="hv_log10",
        hue="algorithm",
        hue_order=algo_order,  # Now matches the CSV perfectly
        palette=custom_colors,
        showfliers=False
    )

    # 6. Formatting
    plt.title("Statistical Distribution of Hypervolume Scores", fontsize=14, weight='bold')
    plt.legend(title=None)
    plt.xlabel(r"Resource Scarcity ($\rho$)", fontsize=12)
    plt.ylabel("Hypervolume (Log10 Scale)", fontsize=12)

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Ensure this points to your file
    plot_rq_2(r"C:\Users\Max\Desktop\thesis\loitering-munition-threat-modeling\data\rq2.csv")