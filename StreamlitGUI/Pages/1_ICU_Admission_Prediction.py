import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Prediction", page_icon="🩺")

# Main content (completely empty screen to start with)
st.markdown("# Risk of ICU Admission")

# Display the selected patient's name
st.markdown(f"Selected: {st.session_state.patient_option}")

# Creating a fully colored red circle
fig, ax = plt.subplots(figsize=(2, 2))
circle = plt.Circle((0, 0.5), 0.4, color='orange')
ax.add_patch(circle)
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_aspect('equal')
ax.axis('off')

# Adding the text 80% directly on top of the circle (adjust the y position)
ax.text(0, 0.3, "80%", fontsize=16, ha='center', va='bottom', fontweight='bold', color='black')

st.pyplot(fig)
