import multiprocessing
import pandas as pd
import requests
import io
import numpy as np

# track identifier (den konkrete patients konktere måling)
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url) #Skriv tracklist_url inne i parantesen

#Variables we would like to check for missing variables is written here

#The travks we would like to save will be saved in this list/array


def worker(subset):
    import os  # Import os to get the process ID
    process_name = multiprocessing.current_process().name
    subset = subset.reset_index(drop=True)
    index_len = len(subset)
    print("Processing subset of size:", index_len)
    save_numerical_tracks = []
    special_variables = {
    'Solar8000/PLETH_HR', 'Orchestra/NEPI_VOL', 'Orchestra/EPI_VOL', 'Orchestra/PHEN_VOL', 'Orchestra/VASO_VOL',
    'Orchestra/DOPA_VOL', 'Orchestra/DOBU_VOL', 'Orchestra/MRN_VOL', 'Solar8000/NIBP_SBP', 'Solar8000/NIBP_DBP', 
    'Solar8000/ART_MBP', 'Solar8000/NIBP_MBP', 'Solar8000/HR', 'CardioQ/HR', 'Vigilance/HR_AVG',
    'Vigileo/CO', 'EV1000/CO', 'Vigilance/CO', 'CardioQ/CO', 'Solar8000/PLETH_SPO2', 'Vigilance/SVO2',
    'Solar8000/FIO2', 'Primus/FIO2', 'Solar8000/RR', 'Primus/PEEP_MBAR', 'Solar8000/VENT_TV', 'Primus/TV',
    'Solar8000/VENT_MEAS_PEEP', 'Solar8000/VENT_PIP', 'Primus/PIP_MBAR', 'Solar8000/FEM_MBP', 'Solar8000/RR_CO2', 
    'Primus/COMPLIANCE' 
    }
    for index, row in subset.iterrows(): # For loop which runs over every row in the df_trackist
        if row['tname'] in special_variables: #Evaluates if the name in the row a special variable
            trackid= row['tid'] #Saves track id as trackid
            caseid = row['caseid'] #Saves caseid as in variable
            print('Caseid', caseid, 'TrackName:', row['tname']) #For testing reasons
            
            #Extracts the numerical track form the API
            trackdata_url = f"https://api.vitaldb.net/{trackid}" 
            response = requests.get(trackdata_url)
            trackdata = pd.read_csv(io.StringIO(response.text))

            #Tries to find minimal samplingfrequency: Takes the 20 first sampels form the Time array, differatiates it 
            # and find the minimal value
            min_gap = trackdata.iloc[:500]['Time'].diff().min()
            # print('Min Gap:', min_gap) #Prints for testing reasons

            last_value_of_array = trackdata['Time'].iloc[-1] #Get the last value of the array, 
            # print('Last value of the array (time when case stops)', last_value_of_array)

            how_many_samples_should_there_be=last_value_of_array/min_gap #Calculatio of how many samples should actually be in the signal 

            # print('How many samples should there be', how_many_samples_should_there_be) #Print for tesing
            total_length_of_singal = len(trackdata['Time']) #Calculates how many samples are in the numerical track
            # print('How many sammples are there:',total_length_of_singal)

            samples_missing = how_many_samples_should_there_be-total_length_of_singal #Calcuation of how many samples are actually missing
            precentage_of_signal_is_there = (total_length_of_singal/how_many_samples_should_there_be)*100 # A precentage calcuation of how many sampels are missing

            #times_missing_a_sample = sum(x > min_gap for x in sampled_times[1:])
            #print("Times there is missing a sample", times_missing_a_sample)

            if how_many_samples_should_there_be > 1.2 * total_length_of_singal:
                print(process_name, ' No index: ', index," of ",index_len, 'There is', total_length_of_singal, 'samples', 
                      'but there should be', how_many_samples_should_there_be, 'samples', 
                      'This precentage of the signal is precent', precentage_of_signal_is_there, '%')
                save_numerical_tracks.append([row['caseid'], row['tname'], row['tid'], how_many_samples_should_there_be, total_length_of_singal, min_gap, samples_missing, precentage_of_signal_is_there ])
            else:
                # print(f"[{process_name}] Saving case {caseid}, {row['tname']} - {percentage_of_signal_present:.2f}% complete")
                print(process_name,' Yes index: ', index," of ",index_len, 'There is', total_length_of_singal, 'samples', 'but there should be', how_many_samples_should_there_be, 'samples', 'This precentage of the signal is precent', precentage_of_signal_is_there, '%')
                save_numerical_tracks.append([row['caseid'], row['tname'], row['tid'], how_many_samples_should_there_be, total_length_of_singal, min_gap, samples_missing, precentage_of_signal_is_there ])

    return save_numerical_tracks

def parallel_for_loop(df, num_workers=None):
    """Splits the for loop workload across multiple CPU cores."""
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()  # Use all available cores

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a DataFrame.")

    chunks = np.array_split(df, num_workers)

    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(worker, chunks)

    return [item for sublist in results for item in sublist]

if __name__ == "__main__":
    
    result = parallel_for_loop(df_tracklist)
    if result:
        df_saved_tracks = pd.DataFrame(result, columns=["caseid", "tname", "tid", "how_many_samples_should_there_be","total_samples_of_singal", "min_gap", "samples_missing", "precentage_of_signal_is_there"])
        df_saved_tracks.to_csv("saved_tracks_numerical_MC_below100trialtest2.csv", index=False)
        print("CSV file 'saved_tracks_numerical_MC_below100trial.csv' has been saved.")
    else:
        print("No tracks met the criteria for saving.:()")
    print(result)