import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime  # Add this import

st.set_page_config(page_title="Prediction", page_icon="🩺")

# Main content
st.markdown("# Certainty of ICU need")

# Display the selected patient's name
patient_name = st.session_state.patient_option
st.markdown(f"### Selected patient: {patient_name}")

# Default probability
probability = 0.8  # fallback if patient not matched

# Map patient names to case IDs
patient_case_map = {
    "Åge Sørensen 020865-1448": 5,
    "Børge Holm 241279-1337": 16,
    "Ida Jensen 040499-1688": 706,
}

# If selected patient is in the map, try to read the corresponding probability
if patient_name in patient_case_map:
    case_id = patient_case_map[patient_name]
    try:
        df = pd.read_csv("Machine/test_predictions_preperi.csv")
        prob = df.loc[df["caseid"] == case_id, "predicted_probability"].values
        if len(prob) > 0:
            probability = float(prob[0])
    except Exception as e:
        st.error(f"Error loading prediction: {e}")

# Convert probability to percentage text
percent_text = f"{int(round(probability * 100))}%"

# Display timestamp above the circle
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Timestamp for prediction:** {current_time}")

st.markdown("This is a machine learning based prediction. Always include your own professional assessment. ")

st.markdown("**Color Scale:** Green: < 40%, Orange: 40–60%, Red: > 60%")

# Determine circle color based on probability
if probability <= 0.40:
    circle_color = 'green'  # 1% - 40% green
elif probability <= 0.60:
    circle_color = 'orange'  # 40% - 60% orange
else:
    circle_color = 'red'  # 60% - 100% red

# Create a circle with the probability text
fig, ax = plt.subplots(figsize=(2, 2))
circle = plt.Circle((0, 0.5), 0.4, color=circle_color)
ax.add_patch(circle)
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_aspect('equal')
ax.axis('off')

# Add text inside the circle
ax.text(0, 0.3, percent_text, fontsize=16, ha='center', va='bottom', fontweight='bold', color='black')

st.pyplot(fig)



