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

program_pct_complete = float(get_value_by_label(df, '% Completed (Program Days)'))
days_completed = int(get_value_by_label(df, 'Days Completed'))
total_days = int(get_value_by_label(df, 'Total Days'))

total_required_days = int(get_value_by_label(df, 'Total Days (Courses)'))
total_completed_days = int(get_value_by_label(df, 'Days Completed (Courses)'))
courses_day_pct = float(get_value_by_label(df, '% Completed (Course Days)'))

completed_courses = float(get_value_by_label(df, 'Number of Completed Courses'))
total_courses = int(get_value_by_label(df, 'Total Number of Courses'))
completed_courses_pct = float(get_value_by_label(df, 'Completed Courses %'))

total_books = int(get_value_by_label(df, 'Total Books'))
total_pages = int(get_value_by_label(df, 'Total Pages'))

theses_total = int(get_value_by_label(df, 'Total'))
theses_completed = int(get_value_by_label(df, 'Completed'))
theses_pct = float(get_value_by_label(df, 'Theses Completed %'))

comps_total = int(get_value_by_label(df, 'Total.1'))
comps_completed = int(get_value_by_label(df, 'Completed.1'))
comps_pct = float(get_value_by_label(df, '% Completed'))

# --- Filter only the 10 curriculum courses ---
curriculum_courses = [
    "Foundations of Strategy",
    "Foundations of Military Theory",
    "Air Power in the Age of Total War",
    "Foundations of Int'l Politics",
    "Air Power in the Age of Limited War",
    "Coercion in Theory and Practice",
    "Irregular Warfare",
    "Information and Cyber Power",
    "Space Power",
    "Technology and Military Innovation"
]
df = df[df['Course'].isin(curriculum_courses)].copy()

# --- Convert numeric columns ---
numeric_cols = ['Required Days', 'Completed Days', 'Completed Books', 'Book Pages']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- Add Status column ---
def determine_status(row):
    if row['Completed Days'] >= row['Required Days'] and row['Required Days'] > 0:
        return '✅ Completed'
    elif row['Completed Days'] == 0:
        return '🚫 Not Started'
    else:
        return '⏳ In Progress'

df['Status'] = df.apply(determine_status, axis=1)

# --- Display Course Completion Status ---
st.markdown("### 📏 Course Completion Status")
st.progress(courses_day_pct / 100)
st.caption(f"{total_completed_days} of {total_required_days} course days completed ({courses_day_pct}%)")

# --- Display Overall Program Progress ---
st.markdown("### 📅 Overall Program Progress")
st.progress(program_pct_complete / 100)
st.caption(f"{days_completed} of {total_days} calendar days completed ({program_pct_complete}%)")

# --- KPI Display ---
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

# --- Bar Chart of Progress ---
st.markdown("### 📚 Course Completion Status")
df_chart = df[df['Status'] != '🚫 Not Started'].copy()
df_chart['Progress %'] = (df_chart['Completed Days'] / df_chart['Required Days']).clip(0, 1) * 100

bar = alt.Chart(df_chart).mark_bar().encode(
    x=alt.X('Course', sort='-y'),
    y=alt.Y('Progress %', title="Progress", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(format='%')),
    color=alt.Color('Status', legend=alt.Legend(title="Status")),
    tooltip=['Course', 'Completed Days', 'Required Days', 'Status']
).properties(width=800, height=400)

st.altair_chart(bar, use_container_width=True)

# --- Horizontal Progress Bars Section ---
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

# --- Raw Table ---
st.markdown("### 🧾 Raw Course Table")
visible_cols = ['Course', 'Course Number', 'Required Days', 'Completed Days', 'Completed Books', 'Book Pages', 'Status']
existing_cols = [col for col in visible_cols if col in df.columns]
if existing_cols:
    df_display = df[existing_cols].copy()
    df_display.index = range(1, len(df_display) + 1)
    st.dataframe(df_display)
else:
    st.warning("⚠️ None of the expected columns were found in the data.")
