# streamlit run c:/Users/mariah/Documents/GitHub/P10/StreamlitGUI/SurgiCare_Front_page.py
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
st.markdown("### An ICU prediction tool")
st.markdown("A machine learning based decision support tool to predict certainty of ICU need using a selection of variables. Never solely rely on this recommendation, always include you own assessment.")

if "current" not in st.session_state:
    st.session_state.current = None
    st.session_state.patient_option = None

col1_options = ["Åge Sørensen 020859-1447", "Børge Holm 241268-1337", "Ida Jensen 040464-1688"]
col2_options = ["Mona Due Bak 161055-9446"]
col3_options = ["Hanne Holmegård 091288-8446"]
col4_options = ["Ib Bentsen 081168-6757"]
all_options = col1_options + col2_options + col3_options + col4_options

def display_buttons(col, options):
    for option in options:
        if col.button(option):
            st.session_state.current = option
# Surgical specialties side by side (4 columns)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### General")
    # Radio buttons for selecting a patient under General
    # st.session_state.patient_option = st.radio("## Select a patient", ("Åge Sørensen 020859-1447", "Børge Holm 241268-1337", "Ida Jensen 040464-1688"))
    # st.write(f"Selected: {st.session_state.patient_option}")

with col2:
    st.markdown("### Thoracic")
    # Add any content or widgets you want for thoracic here

with col3:
    st.markdown("### Gynecology")
    # Add any content or widgets you want for gynecology here

with col4:
    st.markdown("### Urology")
    # Add any content or widgets you want for urology here

display_buttons(col1, col1_options)
display_buttons(col2, col2_options)
display_buttons(col3, col3_options)
display_buttons(col4, col4_options)
# Display current selection
if st.session_state.current:
    st.success(f"Selected patient: {st.session_state.current}")
    st.session_state.patient_option = st.session_state.current