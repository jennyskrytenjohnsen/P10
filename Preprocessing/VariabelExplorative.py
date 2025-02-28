import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases" #trks
df_clinical = pd.read_csv(clinical_data_url)

# Display an overview of the dataset
print("Dataset Overview:")
print(df_clinical.info())  # Shows column names, data types, and missing values

# Select two variables for visualization
var1 = "age"  # Example variable: patient age
var2 = "height"  # Example variable: patient height
icu_var = "icu_days"  # ICU stay duration variable

# Drop rows with missing values for selected variables
df_plot = df_clinical[[var1, var2, icu_var]].dropna()

# Define ICU and non-ICU groups
df_no_icu = df_plot[df_plot[icu_var] == 0]  # Patients with ICU_DAYS = 0
df_icu = df_plot[df_plot[icu_var] > 0]  # Patients who had an ICU stay

# --- Scatter Plot ---
plt.figure(figsize=(8, 5))
plt.scatter(df_no_icu[var1], df_no_icu[var2], color='red', alpha=0.5, label='No ICU')
plt.scatter(df_icu[var1], df_icu[var2], color='blue', alpha=0.5, label='ICU')
plt.xlabel(var1)
plt.ylabel(var2)
plt.title(f"Scatter Plot of {var1} vs {var2}")
plt.grid(True)

# Add legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Red: No ICU'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Blue: ICU')
]
plt.legend(handles=legend_elements, loc="upper right")

# Show scatter plot
plt.show()

# --- Histogram of var1 ---
plt.figure(figsize=(8, 5))
plt.hist(df_no_icu[var1], bins=20, color='red', alpha=0.7, label='No ICU')
plt.hist(df_icu[var1], bins=20, color='blue', alpha=0.7, label='ICU')
plt.xlabel(var1)
plt.ylabel("Frequency")
plt.title(f"Histogram of {var1}")
plt.grid(True)

# Add legend
plt.legend()

# Show histogram
plt.show()


