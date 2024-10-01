def generate_study_plan(available_time, subjects, priority_subject, include_breaks=True, pomodoro_duration=25):
    """
    Generates a study plan based on the user's input with dynamic time allocation and optional break periods.

    Parameters:
    - available_time: Total hours available for study per day.
    - subjects: List of subjects to study.
    - priority_subject: Subject that should be prioritized.
    - include_breaks: Boolean to determine if breaks should be included in the plan.
    - pomodoro_duration: Duration of a single study session in minutes (default is 25 minutes).

    Returns:
    - A dictionary representing the study plan.
    """
    if not subjects:
        return {"Error": "No subjects provided"}

    study_plan = {}
    total_subjects = len(subjects)

    # Basic time allocation per subject
    base_time_per_subject = available_time / total_subjects

    # Adjust time for priority subject (50% more time)
    adjusted_time_per_subject = {}
    total_time_allocation = 0

    for subject in subjects:
        if subject == priority_subject:
            adjusted_time_per_subject[subject] = round(base_time_per_subject * 1.5, 2)
        else:
            adjusted_time_per_subject[subject] = round(base_time_per_subject, 2)

        total_time_allocation += adjusted_time_per_subject[subject]

    # Check if allocated time exceeds available time
    if total_time_allocation > available_time:
        scale_factor = available_time / total_time_allocation
        for subject in adjusted_time_per_subject:
            adjusted_time_per_subject[subject] = round(adjusted_time_per_subject[subject] * scale_factor, 2)

    # Include Pomodoro Technique
    for subject, hours in adjusted_time_per_subject.items():
        sessions = []
        time_left = hours * 60  # Convert hours to minutes
        while time_left > 0:
            if time_left >= pomodoro_duration:
                sessions.append(f"{pomodoro_duration} min study")
                time_left -= pomodoro_duration
                if include_breaks and time_left > 0:
                    sessions.append("5 min break")
                    time_left -= 5  # Add a 5-minute break
            else:
                sessions.append(f"{int(time_left)} min study")
                break

        study_plan[subject] = sessions

    return study_plan   