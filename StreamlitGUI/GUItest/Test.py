import streamlit as st

col1_options = ["Aassssasdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddsffdddddddddds\nPPS", "BsdffffffffffffffffffffffffffffffffffffffffffffffffffffffBBY", "CHPT", "CNC", "COUP", "DAL", "DDD", "FL", "FSLY", "GME"]
col2_options = ["GPS", "GRWG", "KSS", "LVS", "M", "MARA", "NVAX", "OKTA", "PENN"]
col3_options = ["PLUG", "RNG", "SHAK", "STEM", "STX", "UAL", "URBN", "YY", "ZS"]

all_options = col1_options + col2_options + col3_options

if "current" not in st.session_state:
    st.session_state.current = None

# Create columns
col1, col2, col3 = st.columns(3)

# Button display function
def display_buttons(col, options):
    for option in options:
        if col.button(option):
            st.session_state.current = option

# Render buttons in each column
display_buttons(col1, col1_options)
display_buttons(col2, col2_options)
display_buttons(col3, col3_options)

# Display current selection
if st.session_state.current:
    st.success(f"You picked: {st.session_state.current}")