import pandas as pd

# Load the CSV file
file_path = 'Preprocessing/Data/Data_vasoactivedrugs.csv'
df = pd.read_csv(file_path)

# Check if the column exists
if 'value_phe' in df.columns:
    # Count the number of 1's and 0's
    counts = df['value_phe'].value_counts()

    # Print the results
    print(f"Number of 1's: {counts.get(1, 0)}")
    print(f"Number of 0's: {counts.get(0, 0)}")
else:
    print("The column 'value_phe' was not found in the dataset.")
