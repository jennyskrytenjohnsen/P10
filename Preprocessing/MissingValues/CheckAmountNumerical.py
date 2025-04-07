import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
data = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")

# Filter data where 'tname' is 'Primus/FIO2'
data = data[data["tname"] == "Solar8000/ART_SBP"]

# Print rows where 'precentage_of_signal_is_there' is greater than 100
outliers = data[data["precentage_of_signal_is_there"] < 75]
if not outliers.empty:
    print("Rows where 'precentage_of_signal_is_there' is less than 75:")
    print(outliers)

# Plot the distribution of 'percentage_of_signal_is_there'
plt.figure(figsize=(8, 5))
plt.hist(data["precentage_of_signal_is_there"], bins=20, edgecolor='black', alpha=0.7)
plt.xlabel("Percentage of Data Available")
plt.ylabel("Number of Patients")
plt.title("Distribution of Data Availability for 'Primus/FIO2'")
plt.grid(True)
plt.show()
