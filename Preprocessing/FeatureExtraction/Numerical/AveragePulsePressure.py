import pandas as pd
import numpy as np

# Load the datasets
sysbp_df = pd.read_csv("Preprocessing/Data/NewData/Data_SysBP.csv")
diabp_df = pd.read_csv("Preprocessing/Data/NewData/Data_DiaBP.csv")

# Merge on 'caseid'
merged_df = pd.merge(sysbp_df, diabp_df, on='caseid', how='inner')

# Calculate average PP over the entire operation
merged_df['PP_total'] = merged_df['SysBP_total'] - merged_df['DiaBP_total']
avg_pp_total = merged_df['PP_total'].mean()

# Calculate average PP over the last 15 minutes
merged_df['PP_w15min'] = merged_df['SysBP_w15min'] - merged_df['DiaBP_w15min']
avg_pp_w15min = merged_df['PP_w15min'].mean()

# Calculate PP over the last 15 minutes with 'MV' (Mean Value)
merged_df['PP_w15minMV'] = merged_df['SysBP_w15minMV'] - merged_df['DiaBP_w15minMV']
avg_pp_w15minMV = merged_df['PP_w15minMV'].mean()

# Save selected outputs
result_df = merged_df[['caseid', 'PP_total', 'PP_w15min', 'PP_w15minMV']]
result_df.to_csv("Preprocessing/Data/NewData/Data_PP.csv", index=False)

# Optional: print summary stats
print(f"Average PP (entire operation): {avg_pp_total:.2f}")
print(f"Average PP (last 15 minutes): {avg_pp_w15min:.2f}")
print(f"Average PP (last 15 minutes with MV): {avg_pp_w15minMV:.2f}")
