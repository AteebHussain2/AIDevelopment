import streamlit as st
import json
from utils.scheduler import generate_study_plan

# Load sample data from file
def load_sample_data(file_path="data/sample_data.json"):
    with open(file_path, "r") as file:
        return json.load(file)

# Load sample data
sample_data = load_sample_data()

# Title of the application
st.title("📚 Smart Study Planner")

st.sidebar.header("📝 Input Your Study Preferences")

# Option to use sample data
use_sample_data = st.sidebar.checkbox("Use Sample Data")

if use_sample_data:
    # Select a sample user scenario
    selected_username = st.sidebar.selectbox("Select a sample user", [user["username"] for user in sample_data])
    
    # Find the selected user's data
    selected_user = next((user for user in sample_data if user["username"] == selected_username), None)

    if selected_user:
        # Pre-fill fields with sample data
        available_time = selected_user["available_time"]
        subjects = selected_user["subjects"]
        priority_subject = selected_user["priority_subject"]
        goal = selected_user["goal"]
        include_breaks = selected_user["include_breaks"]
        pomodoro_duration = selected_user["pomodoro_duration"]
    else:
        st.error("User data not found.")
else:
    # Regular user input
    available_time = st.sidebar.slider("How many hours per day can you dedicate to study?", 1, 12, 2)
    subjects = st.sidebar.multiselect("Select the subjects you want to study:", 
                                      ["Math", "Science", "History", "Computer Science", "Languages"])
    priority_subject = st.sidebar.selectbox("Which subject do you want to prioritize?", subjects)
    goal = st.sidebar.text_input("What's your study goal for this period? (e.g., Finish Chapter 3)")
    include_breaks = st.sidebar.checkbox("Include Breaks (Pomodoro Technique)", value=True)
    pomodoro_duration = st.sidebar.slider("Pomodoro Session Duration (minutes)", 15, 60, 25)

# Button to generate the study plan
if st.sidebar.button("Generate Study Plan"):
    if subjects:
        # Generate the study plan using the function
        study_plan = generate_study_plan(available_time, subjects, priority_subject, include_breaks, pomodoro_duration)
        
        if "Error" in study_plan:
            st.warning(study_plan["Error"])
        else:
            # Enhanced Display
            st.markdown("### 📅 Your Study Plan")
            st.markdown("---")  # Add a horizontal line for separation
            
            for subject, sessions in study_plan.items():
                st.markdown(f"#### **{subject}**")
                
                # Create columns for a more organized view
                col1, col2, col3 = st.columns(3)

                for i, session in enumerate(sessions):
                    if i % 3 == 0:
                        col1.markdown(f"- ⏳ {session}")
                    elif i % 3 == 1:
                        col2.markdown(f"- ⏳ {session}")
                    else:
                        col3.markdown(f"- ⏳ {session}")
                    
                st.markdown("---")  # Add a horizontal line after each subject
    else:
        st.warning("Please select at least one subject to study.")
