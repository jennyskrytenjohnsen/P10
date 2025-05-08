import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Prediction", page_icon="🩺")

# Main content (completely empty screen to start with)
st.markdown("# Risk of ICU Admission")

# Display the selected patient's name
patient_name = st.session_state.patient_option
st.markdown(f"## Selected: {patient_name}")

# Default probability
probability = 0.8  # fallback

# Check if it's the specified patient
if patient_name == "Åse Sørensen 020865-1448":
    try:
        df = pd.read_csv("Machine/test_predictions.csv")
        # Extract probability for case ID 20
        prob = df.loc[df["caseid"] == 20, "predicted_probability"].values
        if len(prob) > 0:
            probability = float(prob[0])
    except Exception as e:
        st.error(f"Error loading prediction: {e}")

# Convert to percentage integer
percent_text = f"{int(round(probability * 100))}%"

# Creating a fully colored circle
fig, ax = plt.subplots(figsize=(2, 2))
circle = plt.Circle((0, 0.5), 0.4, color='orange')
ax.add_patch(circle)
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_aspect('equal')
ax.axis('off')

# Add dynamic probability text
ax.text(0, 0.3, percent_text, fontsize=16, ha='center', va='bottom', fontweight='bold', color='black')

st.pyplot(fig)
