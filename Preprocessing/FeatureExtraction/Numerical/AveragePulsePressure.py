import pandas as pd
import numpy as np

# Load the datasets
sysbp_df = pd.read_csv("Preprocessing/Data/Data_AvgSysBP.csv")
diabp_df = pd.read_csv("Preprocessing/Data/Data_AvgDiaBP.csv")

# Merge on 'caseid'
merged_df = pd.read_csv("test_mergedPP.csv")

# Calculate average PP over the entire operation
merged_df['PP_total'] = merged_df['SysBP_total'] - merged_df['DiaBP_total']
avg_pp_total = merged_df['PP_total'].mean()

# Calculate average PP over the last 15 minutes
merged_df['PP_w15min'] = merged_df['SysBP_w15min'] - merged_df['DiaBP_w15min']
avg_pp_w15min = merged_df['PP_w15min'].mean()

# Save selected outputs
result_df = merged_df[['caseid', 'PP_total', 'PP_w15min']]
result_df.to_csv("Preprocessing/Data/NewData/Data_PP.csv", index=False)
