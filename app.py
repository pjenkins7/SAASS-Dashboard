import streamlit as st
import pandas as pd
import altair as alt
import datetime

st.set_page_config(page_title="SAASS Progress Dashboard", layout="wide")
st.title("\U0001F4D8 SAASS Progress Dashboard")
st.markdown("Auto-updating dashboard from Google Sheets — tracking books, courses, and program milestones.")

# --- Load Google Sheet Data ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUoPJRLuSRN1Y2GOSunfe0YtIECq2AeRzpVRoTVbDWbJ0Zw3J7VPUpKZjSDlKEYIeoELN39pBFUZJB/pub?gid=1897265951&single=true&output=csv"
df = pd.read_csv(sheet_url)

# --- Clean Columns and Header Row ---
df = df.dropna(how="all", axis=1)
df.columns = df.iloc[1].fillna("").str.strip()
df = df[2:].reset_index(drop=True)
df = df.rename(columns=lambda x: x.strip())

if 'Course Title' in df.columns:
    df = df.rename(columns={'Course Title': 'Course'})

df['Course'] = df['Course'].astype(str).str.strip()

# --- Extract reference data from known rows ---
def get_value_by_label(df, label):
    match = df[df.iloc[:, 1] == label]
    if not match.empty:
        return match.iloc[0, 2]
    return None

def safe_float(val, label):
    try:
        return float(val)
    except (ValueError, TypeError):
        st.warning(f"⚠️ Could not convert '{label}' to float. Value: {val}")
        return 0.0

def safe_int(val, label):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        st.warning(f"⚠️ Could not convert '{label}' to int. Value: {val}")
        return 0

program_pct_complete = safe_float(get_value_by_label(df, '% Completed (Program Days)'), '% Completed (Program Days)')
days_completed = safe_int(get_value_by_label(df, 'Days Completed'), 'Days Completed')
total_days = safe_int(get_value_by_label(df, 'Total Days'), 'Total Days')

total_required_days = safe_int(get_value_by_label(df, 'Total Days (Courses)'), 'Total Days (Courses)')
total_completed_days = safe_int(get_value_by_label(df, 'Days Completed (Courses)'), 'Days Completed (Courses)')
courses_day_pct = safe_float(get_value_by_label(df, '% Completed (Course Days)'), '% Completed (Course Days)')

completed_courses = safe_float(get_value_by_label(df, 'Number of Completed Courses'), 'Number of Completed Courses')
total_courses = safe_int(get_value_by_label(df, 'Total Number of Courses'), 'Total Number of Courses')
completed_courses_pct = safe_float(get_value_by_label(df, 'Completed Courses %'), 'Completed Courses %')

total_books = safe_int(get_value_by_label(df, 'Total Books'), 'Total Books')
total_pages = safe_int(get_value_by_label(df, 'Total Pages'), 'Total Pages')

theses_total = safe_int(get_value_by_label(df, 'Total'), 'Total')
theses_completed = safe_int(get_value_by_label(df, 'Completed'), 'Completed')
theses_pct = safe_float(get_value_by_label(df, 'Theses Completed %'), 'Theses Completed %')

comps_total = safe_int(get_value_by_label(df, 'Total.1'), 'Total.1')
comps_completed = safe_int(get_value_by_label(df, 'Completed.1'), 'Completed.1')
comps_pct = safe_float(get_value_by_label(df, '% Completed'), '% Completed')

# --- Visualizations and Summary ---
st.markdown("### 📏 Course Completion Status")
st.progress(courses_day_pct / 100)
st.caption(f"{total_completed_days} of {total_required_days} course days completed ({courses_day_pct}%)")

st.markdown("### 📅 Overall Program Progress")
st.progress(program_pct_complete / 100)
st.caption(f"{days_completed} of {total_days} calendar days completed ({program_pct_complete}%)")

st.markdown("### 📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Course Completion", f"{completed_courses} / {total_courses} ({completed_courses_pct}%)")
    st.metric("Course Days Completed", f"{total_completed_days} / {total_required_days} ({courses_day_pct}%)")
with col2:
    st.metric("Books Completed", f"{total_books}")
    st.metric("Pages Read", f"{total_pages}")
with col3:
    st.metric("Theses Completed", f"{theses_completed} / {theses_total} ({theses_pct}%)")
    st.metric("Comps Completed", f"{comps_completed} / {comps_total} ({comps_pct}%)")

# --- Course Completion Chart ---
st.markdown("### 📚 Course Completion Chart")
if 'Required Days' in df.columns and 'Completed Days' in df.columns:
    df['Required Days'] = pd.to_numeric(df['Required Days'], errors='coerce')
    df['Completed Days'] = pd.to_numeric(df['Completed Days'], errors='coerce')
    df['Progress %'] = (df['Completed Days'] / df['Required Days']).clip(0, 1) * 100
    df_chart = df[df['Required Days'] > 0].copy()

    bar = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Course', sort='-y'),
        y=alt.Y('Progress %', title="Progress", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(format='%')),
        tooltip=['Course', 'Completed Days', 'Required Days']
    ).properties(width=800, height=400)

    st.altair_chart(bar, use_container_width=True)

# --- Progress Overview Section ---
st.markdown("### 📏 Progress Overview")
col_bar1, col_bar2, col_bar3 = st.columns(3)
with col_bar1:
    st.subheader("📘 Courses")
    st.progress(completed_courses / total_courses)
    st.caption(f"{completed_courses} of {total_courses} courses completed ({completed_courses_pct}%)\n{total_completed_days} of {total_required_days} course days ({courses_day_pct}%)")
with col_bar2:
    st.subheader("🎓 Theses")
    st.progress(theses_completed / theses_total)
    st.caption(f"{theses_completed} of {theses_total} theses completed ({theses_pct}%)")
with col_bar3:
    st.subheader("🧠 Comps")
    st.progress(comps_completed / comps_total)
    st.caption(f"{comps_completed} of {comps_total} comps completed ({comps_pct}%)")
