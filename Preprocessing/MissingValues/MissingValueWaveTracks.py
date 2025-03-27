# DENNE FUNGERER NÅ!!!!!!!!!!!!!!!!  Til maria

#Denne koden henter EEG- og fysiologiske signaler fra en API, analyserer dem for datakvalitet, 
#og lagrer relevant informasjon i en CSV-fil hvis signalene oppfyller gitte kriterier.


import vitaldb
import pandas as pd
import requests
import json
import io
import time  # Importer time-modulet
import numpy as np

# track identifier (den konkrete patients konktere måling)
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url) #Skriv tracklist_url inne i parantesen



# Liste for spesielle variabler
special_variables = {
    "SNUADC/ART", "SNUADC/CVP", "SNUADC/ECG_II", "SNUADC/ECG_V5",
    "SNUADC/FEM", "SNUADC/PLETH", "Primus/AWP", "Primus/CO2",
    "BIS/EEG1_WAV", "BIS/EEG2_WAV", "CardioQ/ABP", "CardioQ/FLOW"
}

# Liste for å lagre data som skal skrives til CSV
saved_tracks = []


# trackdata_url = f"https://api.vitaldb.net/0aa685df768489a18a5e9f53af0d83bf60890c73"
# response = requests.get(trackdata_url, timeout = 10)
# trackdata = pd.read_csv(io.StringIO(response.text)) 
# trackdata.to_csv("data/test.csv", index=False)


def collect_track_null_checker():
    # Hent hver trackidentifierverdi
    for index, row in df_tracklist.iterrows():
        if row['tname'] in special_variables:
            trackidentifier = row["tid"]
            trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"
            
            # Handles API error

            try:
            
                response = requests.get(trackdata_url, timeout = 10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print(f"Timeout-error: Can not get {row['tname']} ({trackdata_url})")
                continue # Go to next signal

            try:
                # Konverter API-respons til en pandas DataFrame
                trackdata = pd.read_csv(io.StringIO(response.text)) 
                if trackdata.empty:
                    continue
            except:
                continue


            data_column = trackdata.columns[1]  # Velger den andre kolonnen (indeks 1)

            # Tell antall nullverdier, nanveridr, totalt antall missing verdier, og find samplingsperiode
            zero_count = (trackdata[data_column] == 0).sum().sum()
            nan_count_per_column = trackdata[data_column].isna().sum().sum()
            total_non_value = zero_count+nan_count_per_column
            size = trackdata[data_column].size
            samplingperiode = trackdata.iloc[0,1]

            # Sjekk om mer enn 20% av verdiene er null
            
            if total_non_value >= 0.2 * size:
                print(f"index: {index} ,NO.This track, {trackdata.columns[1]}, has {zero_count} 0s, {nan_count_per_column} NAN, combined {total_non_value} non informatory values out of {size} samples")
            else:
                print(f"index: {index} ,Saved.This track, {trackdata.columns[1]}, has {zero_count} 0s, {nan_count_per_column} NAN, combined {total_non_value} non informatory values out of {size} samples")
                # Lagre caseid, tname og tid
                saved_tracks.append([row["caseid"], row["tname"], row["tid"], nan_count_per_column, zero_count, size, samplingperiode])
                trackdata.to_csv(f"data/{trackidentifier}.csv",index=False)
            # Vent 2 sekunder før neste forespørsel
            # time.sleep(2)
        else:
            print(f"index: {index} ,Did not have special_variables")

    # Konverter listen til en DataFrame og lagre som CSV
    if saved_tracks:
        df_saved_tracks = pd.DataFrame(saved_tracks, columns=["caseid", "tname", "tid", "nan_count_per_column","zero_count", "size", "samplingperiode"])
        df_saved_tracks.to_csv("saved_tracks.csv", index=False)
        print("CSV file 'saved_tracks.csv' has been saved.")
    else:
        print("No tracks met the criteria for saving.")

# Kjør funksjonen
collect_track_null_checker()

