import pandas as pd
import numpy as np

# Load the datasets
sysbp_df = pd.read_csv("Preprocessing/Data/Data_AvgSysBP.csv")
diabp_df = pd.read_csv("Preprocessing/Data/Data_AvgDiaBP.csv")

# Merge on 'caseid'
merged_df = pd.read_csv("test_mergedPP.csv")
# merged_df = pd.merge(sysbp_df, diabp_df, on='caseid', how='outer', suffixes=('AvgSysBP', 'AvgDiaBP'))
# merged_df.to_csv('test_merged.csv', index=False)
# Calculate Pulse Pressure (PP) as SysBP - DiaBP
merged_df['PP'] = merged_df['AvgSysBP'] - merged_df['AvgDiaBP']

# Keep only caseid and PP
result_df = merged_df[['caseid', 'PP']]

# Save the result
result_df.to_csv("Preprocessing/Data/Data_AvgPP.csv", index=False)
