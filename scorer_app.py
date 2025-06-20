import streamlit as st
import pandas as pd
from datetime import date

st.title("🐭 WRAM Scorer Tool — Multi-Animal Tracker")

# Sidebar input
st.sidebar.header("Session Info")
tester_name = st.sidebar.text_input("Tester Name", value="Ishmeet")
test_date = st.sidebar.date_input("Test Date", value=date.today())
animal_name = st.sidebar.text_input("Animal Name / Subject ID", value="Mouse001")

baited_arms = st.sidebar.multiselect(
    "Select baited arms for this trial:",
    list(range(1, 9)),
    help="Pick 4 arms where platforms were present"
)

# Main trial input
entry_input = st.text_input("Enter sequence of arm entries (comma-separated):", "1,4,5,2,3,6")
trial_time = st.text_input("Enter time taken for this trial (in seconds):", "45")

# Session state for all scores
if "all_scores" not in st.session_state:
    st.session_state.all_scores = []

# Count existing trials for the animal to auto-assign trial number
animal_trials = [entry for entry in st.session_state.all_scores if entry["Animal"] == animal_name]
next_trial_number = len(animal_trials) + 1

# Show auto-trial assignment
st.markdown(f"### Trial Number: `{next_trial_number}` (auto-assigned)")

if st.button("Score Trial"):
    if len(baited_arms) != 4:
        st.warning("Please select exactly 4 baited arms.")
    else:
        entries = [int(x.strip()) for x in entry_input.split(',')]
        visited = set()
        ref_errors = 0
        wm_incorrect = 0
        wm_correct = 0

        current_baited = baited_arms.copy()
        never_baited = set(range(1, 9)) - set(current_baited)

        scoring = []
        for arm in entries:
            if arm in current_baited:
                scoring.append((arm, "No Error"))
                current_baited.remove(arm)
            elif arm in never_baited and arm not in visited:
                ref_errors += 1
                scoring.append((arm, "REF Error"))
            elif arm in never_baited and arm in visited:
                wm_incorrect += 1
                scoring.append((arm, "WMI Error"))
            elif arm not in baited_arms and arm in visited:
                wm_correct += 1
                scoring.append((arm, "WMC"))
            else:
                scoring.append((arm, "Unclassified"))
            visited.add(arm)

        df = pd.DataFrame(scoring, columns=["Arm", "Scoring Result"])
        st.write("### Scoring Breakdown:")
        st.dataframe(df)

        total_errors = wm_correct + wm_incorrect + ref_errors

        # Save all trial data
        st.session_state.all_scores.append({
            "Tester": tester_name,
            "Date": test_date.strftime("%Y-%m-%d"),
            "Animal": animal_name,
            "Trial": next_trial_number,
            "Time": trial_time,
            "WM CORR": wm_correct,
            "REF MEM": ref_errors,
            "WM INC": wm_incorrect,
            "Total Error": total_errors
        })

# Display full session summary
if st.session_state.all_scores:
    all_df = pd.DataFrame(st.session_state.all_scores)
    st.write("## 📊 Full Trial Summary")
    st.dataframe(all_df)

    csv = all_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Summary (All Animals)", csv, "WRAM_all_summary.csv", "text/csv")
