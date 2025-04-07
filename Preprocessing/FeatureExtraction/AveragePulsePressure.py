import pandas as pd
import numpy as np

# Load the datasets
sysbp_df = pd.read_csv("Preprocessing/Data/Data_AvgSysBP.csv")
diabp_df = pd.read_csv("Preprocessing/Data/Data_AvgDiaBP.csv")

# Merge on 'caseid'
merged_df = pd.merge(sysbp_df, diabp_df, on='caseid', how='outer', suffixes=('_SysBP', '_DiaBP'))

# Calculate Pulse Pressure (PP) as SysBP - DiaBP
merged_df['PP'] = merged_df['SysBP'] - merged_df['DiaBP']

# Keep only caseid and PP
result_df = merged_df[['caseid', 'PP']]

# Save the result
result_df.to_csv("Preprocessing/Data/Data_AvgPP.csv", index=False)
