import pandas as pd

# Load the CSV file
df = pd.read_csv("TestTrainingSet/train_ids_pre&peri.csv")

# Ensure 'has_aline' is numeric
df['has_aline'] = pd.to_numeric(df['has_aline'], errors='coerce')

# Select only numeric columns
numeric_df = df.select_dtypes(include='number')

# Calculate Spearman correlation
aline_corr_spearman = numeric_df.corr(method='spearman')['has_aline'].drop('has_aline')

# Sort correlations for better readability
aline_corr_spearman_sorted = aline_corr_spearman.sort_values(ascending=False)

# Print the result
print(aline_corr_spearman_sorted)

# Optionally save to a CSV
# aline_corr_spearman_sorted.to_csv("aline_spearman_correlation.csv", header=["Spearman Correlation"])
