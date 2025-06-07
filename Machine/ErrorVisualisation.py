import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the predictions CSV
df = pd.read_csv("Machine/test_predictions_preperi.csv")

# Ensure output folder exists
os.makedirs("Machine/plots", exist_ok=True)

# Add a correctness column
df["correct"] = df["predicted_label"] == df["true_label"]

# Sort by predicted probability for nicer plots
df_sorted = df.sort_values("predicted_probability").reset_index(drop=True)

# --- Plot 1: Predicted probabilities with true vs predicted labels ---
plt.figure(figsize=(10, 4))
colors = df_sorted["correct"].map({True: "green", False: "red"})
plt.scatter(df_sorted.index, df_sorted["predicted_probability"], c=colors, alpha=0.7)

plt.axhline(y=0.5, color='gray', linestyle='--', label="Threshold = 0.5")
plt.title("Predicted Probabilities (Green = Correct, Red = Incorrect)")
plt.xlabel("Sorted Case Index")
plt.ylabel("Predicted Probability")
plt.legend()
plt.tight_layout()
plt.savefig("Machine/plots/predicted_probs_scatter.png")
plt.show()

# --- Plot 2: Misclassified cases only ---
df_misclassified = df[df["correct"] == False]
plt.figure(figsize=(10, 4))
sns.barplot(data=df_misclassified, x="caseid", y="predicted_probability", hue="true_label", dodge=False)
plt.axhline(y=0.5, color='gray', linestyle='--', label="Threshold = 0.5")
plt.title("Misclassified Cases")
plt.ylabel("Predicted Probability")
plt.xticks(rotation=90)
plt.legend(title="True Label")
plt.tight_layout()
plt.savefig("Machine/plots/misclassified_cases.png")
plt.show()

