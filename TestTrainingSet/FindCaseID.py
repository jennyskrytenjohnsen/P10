import pandas as pd

# Load the CSV file
file_path = r'C:\Users\mariah\Documents\GitHub\P10\TestTrainingSet\test_ids_pre&peri.csv'
df = pd.read_csv(file_path)

# Filter for cases in Urology or Gynecology
filtered_df = df[(df['Gynecology'] == 1) | (df['Urology'] == 1)].copy()

# Create a new column to indicate the department
def get_department(row):
    if row['Gynecology'] == 1 and row['Urology'] == 1:
        return 'Both'
    elif row['Gynecology'] == 1:
        return 'Gynecology'
    elif row['Urology'] == 1:
        return 'Urology'
    else:
        return 'Unknown'

filtered_df['Department'] = filtered_df.apply(get_department, axis=1)

# Show caseid and department
result = filtered_df[['caseid', 'Department']]

# Print the result
print(result)

# Optional: Save to a CSV
# result.to_csv('gynecology_urology_caseids_with_labels.csv', index=False)
