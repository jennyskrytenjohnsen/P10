import pandas as pd

# Load the CSV file
file_path = 'Preprocessing/Data/NewData/Data_Compliance.csv'
df = pd.read_csv(file_path)

# Display the number of missing values per column
missing_values = df.isnull().sum()
print("Missing values per column:")
print(missing_values)
import pandas as pd

filtered_rows = df[df['Compliance_w15minMV'].isna() & df['Compliance_w15min'].notna()]
print(filtered_rows)

