import pandas as pd

test_fil = 'C:/Users/johns/Documents/10semester/Kode/VitalDB_Tracks.csv'
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url) 

save_number_of_count = []
total_patients = df_tracklist['caseid'].nunique() 

special_variables = {
    'Solar8000/PLETH_HR', 'Orchestra/NEPI_VOL', 'Orchestra/EPI_VOL', 'Orchestra/PHEN_VOL', 'Orchestra/VASO_VOL',
    'Orchestra/DOPA_VOL', 'Orchestra/DOBU_VOL', 'Orchestra/MRN_VOL', 'Solar8000/NIBP_SBP', 'Solar8000/NIBP_DBP', 
    'Solar8000/ART_MBP', 'Solar8000/NIBP_MBP', 'Solar8000/HR', 'CardioQ/HR', 'Vigilance/HR_AVG',
    'Vigileo/CO', 'EV1000/CO', 'Vigilance/CO', 'CardioQ/CO', 'Solar8000/PLETH_SPO2', 'Vigilance/SVO2',
    'Solar8000/FIO2', 'Primus/FIO2', 'Solar8000/RR', 'Primus/PEEP_MBAR', 'Solar8000/VENT_TV', 'Primus/TV',
    'Solar8000/VENT_MEAS_PEEP', 'Solar8000/VENT_PIP', 'Primus/PIP_MBAR', 'EV1000/ART_MBP', 'Solar8000/RR_CO2', 'Primus/COMPLIANCE', 'Solar8000/BT' 
}

def count_tracks():

    how_many_times_is_patient_precent = df_tracklist['tname'].value_counts()
    print('how_many_times_is_patient_precent', how_many_times_is_patient_precent)
    
    new_dataframe = pd.DataFrame({'how_many_times_is_patient_precent': how_many_times_is_patient_precent}).reset_index()

    for index, row in new_dataframe.iterrows():
        if row['tname'] in special_variables:
            precentage_recorded_of_total_patients = (row['how_many_times_is_patient_precent']/total_patients)*100 
            save_number_of_count.append((row['tname'],row['how_many_times_is_patient_precent'],precentage_recorded_of_total_patients))

    if save_number_of_count:
        df_saved_tracks = pd.DataFrame(save_number_of_count, columns=["tname",'how_many_times_is_patient_precent', 'precentage_recorded_of_total_patients'])
        df_saved_tracks.to_csv("howmanypatiensisrecordedforeachtrack_withallvalues.csv", index=False)
        print("CSV file has been saved.")

    else:
        print("No tracks met the criteria for saving.:(")   

count_tracks()
print('Hej')

