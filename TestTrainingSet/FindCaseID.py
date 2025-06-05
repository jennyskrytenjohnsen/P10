# import pandas as pd

# # Load the CSV file
# file_path = r'C:\Users\mariah\Documents\GitHub\P10\TestTrainingSet\test_ids_pre&peri.csv'
# df = pd.read_csv(file_path)

# # Filter for cases in Urology or Gynecology
# filtered_df = df[(df['Gynecology'] == 1) | (df['Urology'] == 1)].copy()

# # Create a new column to indicate the department
# def get_department(row):
#     if row['Gynecology'] == 1 and row['Urology'] == 1:
#         return 'Both'
#     elif row['Gynecology'] == 1:
#         return 'Gynecology'
#     elif row['Urology'] == 1:
#         return 'Urology'
#     else:
#         return 'Unknown'

# filtered_df['Department'] = filtered_df.apply(get_department, axis=1)

# # Show caseid and department
# result = filtered_df[['caseid', 'Department']]

# # Print the result
# print(result)

# # Optional: Save to a CSV
# # result.to_csv('gynecology_urology_caseids_with_labels.csv', index=False)


import pandas as pd

# Load the test set
test_file_path = r'C:\Users\mariah\Documents\GitHub\P10\TestTrainingSet\train_ids_pre&peri.csv'
df_test = pd.read_csv(test_file_path)

# Load the labels
label_file_path = r'C:\Users\mariah\Documents\GitHub\P10\For_machinelearning\number_of_days_in_ICU.csv'
df_labels = pd.read_csv(label_file_path)

# Strip column names of whitespace
df_labels.columns = df_labels.columns.str.strip()

# Ensure matching types
df_test['caseid'] = df_test['caseid'].astype(str)
df_labels['caseid'] = df_labels['caseid'].astype(str)

# Merge
df_merged = df_test.merge(df_labels[['caseid', 'icu_days_binary']], on='caseid', how='left')

# Check if column exists
print(df_merged.columns)

# Calculate percentage distribution
percentage_distribution = df_merged['icu_days_binary_y'].value_counts(normalize=True) * 100

# Print the result
print(percentage_distribution)
