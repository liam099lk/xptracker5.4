import streamlit as st
import pandas as pd
from datetime import datetime
from xp_tracker import XPTracker

# Page config
st.set_page_config(
    page_title="XP Tracker",
    page_icon="📊",
    layout="wide"
)

# Initialize session state variables
if 'tracker' not in st.session_state:
    st.session_state['tracker'] = XPTracker()
if hasattr(st.session_state, 'tracker'):
    st.session_state.tracker.load_data()

if 'show_add_challenge' not in st.session_state:
    st.session_state.show_add_challenge = False

# Header
st.title("XP Tracker")
st.markdown("Track your XP progress as you complete various challenges!")

# Sidebar
with st.sidebar:
    st.header("Actions")

    # XP Goal setting
    new_goal = st.number_input("XP Goal", 
                              min_value=1000, 
                              max_value=1000000, 
                              value=st.session_state.tracker.xp_goal,
                              step=1000)

    if st.button("Update Goal"):
        st.session_state.tracker.set_xp_goal(new_goal)
        st.success(f"Goal updated to {new_goal:,} XP")

    st.divider()

    # Challenge management
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Challenges"):
            st.session_state.show_add_challenge = True

    with col2:
        if st.button("Reset Progress"):
            st.session_state.tracker.reset_progress(keep_challenges=True)
            st.rerun()
    
    st.divider()
    if st.button("Clear All Challenges", type="secondary"):
        if st.session_state.tracker.challenges:
            st.session_state.tracker.clear_challenges()
            st.rerun()



# Main content
if st.session_state.show_add_challenge:
    st.header("Create New Challenges")

    initial_xp = st.number_input("Initial XP", min_value=0, value=0)

    with st.form("new_challenge_form"):
        name = st.text_input("Challenge Name")
        xp = st.number_input("XP Value", min_value=100, value=1000, step=100)
        required = st.number_input("Required Count", min_value=1, value=1)

        if st.form_submit_button("Add Challenge"):
            if name:
                st.session_state.tracker.create_new_challenges([{
                    'name': name,
                    'xp': xp,
                    'required': required
                }], initial_xp)
                st.session_state.show_add_challenge = False
                st.rerun()

# Display Challenges
if st.session_state.tracker.challenges:
    # Summary stats
    summary = st.session_state.tracker.get_summary()
    progress = summary['total_xp'] / summary['xp_goal']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total XP", f"{summary['total_xp']:,}")
    with col2:
        st.metric("Remaining XP", f"{summary['remaining_xp']:,}")
    with col3:
        st.metric("Progress", f"{progress:.1%}")

    st.progress(min(1.0, progress))

    # XP Controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Set Total XP
        total_xp = st.number_input("Set Total XP", min_value=0, value=summary['total_xp'], step=100)
        if st.button("Update Total XP"):
            st.session_state.tracker.total_xp = total_xp
            st.session_state.tracker.save_data()
            st.rerun()
    
    with col2:
        # Add/Subtract XP
        xp_amount = st.number_input("XP Amount", min_value=100, value=1000, step=100)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add XP"):
                st.session_state.tracker.total_xp += xp_amount
                st.session_state.tracker.save_data()
                st.rerun()
        with col2:
            if st.button("Subtract XP"):
                st.session_state.tracker.total_xp = max(0, st.session_state.tracker.total_xp - xp_amount)
                st.session_state.tracker.save_data()
                st.rerun()

    # Challenges
    st.subheader("Challenges")
    for name, ch in st.session_state.tracker.challenges.items():
        col1, col2, col3 = st.columns([2,6,2])
        with col1:
            st.write(f"**{name}**")
            st.caption(f"XP: {ch['xp']:,}")
        with col2:
            progress = ch['input'] / ch['required']
            st.progress(min(1.0, progress))
            st.caption(ch['progress'])
        with col3:
            col3a, col3b = st.columns(2)
            with col3a:
                if st.button("➕", key=f"inc_{name}"):
                    st.session_state.tracker.update_progress({name: 1})
                    st.rerun()
            with col3b:
                if st.button("➖", key=f"dec_{name}"):
                    st.session_state.tracker.update_progress({name: -1})
                    st.rerun()
else:
    st.info("No challenges yet. Add some challenges to get started!")
    if st.button("Use Default Challenges"):
        st.session_state.tracker.use_default_challenges()
        st.rerun()