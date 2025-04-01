import streamlit as st

# Set up the page
st.set_page_config(
    page_title="SurgiCare",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Main content
st.markdown("# SurgiCare")
st.markdown("### An ICU admission risk prediction tool")
st.markdown("A machine learning based decision support tool to predict risk of ICU admission using a selection of variables. Never solely rely on this recommendation, always include you own assessment.")

# Surgical specialties side by side (4 columns)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### General")
    # Radio buttons for selecting a patient under General
    st.session_state.patient_option = st.radio("Select a patient", ("Åse Sørensen 020865-1448", "Børge Holm 241279-1337", "Ida Jensen 040499-1688"))
    st.write(f"Selected: {st.session_state.patient_option}")

with col2:
    st.markdown("### Thoracic")
    # Add any content or widgets you want for thoracic here

with col3:
    st.markdown("### Gynecology")
    # Add any content or widgets you want for gynecology here

with col4:
    st.markdown("### Urology")
    # Add any content or widgets you want for urology here
