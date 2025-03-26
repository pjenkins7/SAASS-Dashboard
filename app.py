import streamlit as st
import pandas as pd
import altair as alt
import datetime

st.set_page_config(page_title="SAASS Progress Dashboard", layout="wide")
st.title("\U0001F4D8 SAASS Class XXXIV Progress Dashboard")
st.markdown("Auto-updating dashboard from Google Sheets — tracking books, courses, and program milestones.")

# --- Load Google Sheet Data ---
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUoPJRLuSRN1Y2GOSunfe0YtIECq2AeRzpVRoTVbDWbJ0Zw3J7VPUpKZjSDlKEYIeoELN39pBFUZJB/pub?gid=1897265951&single=true&output=csv"
df = pd.read_csv(url)

# --- Clean Columns and Header Row ---
df = df.dropna(how="all", axis=1)
df.columns = df.iloc[1].fillna("").str.strip()
df = df[2:].reset_index(drop=True)
df = df.rename(columns=lambda x: x.strip())

if 'Course Title' in df.columns:
    df = df.rename(columns={'Course Title': 'Course'})

df['Course'] = df['Course'].astype(str).str.strip()

# --- Filter only the 10 curriculum courses (safe match) ---
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
        return '🛑 Not Started'
    else:
        return '⏳ In Progress'

df['Status'] = df.apply(determine_status, axis=1)

# --- Program Date Logic ---
program_start = datetime.datetime(2024, 7, 1)
program_end = datetime.datetime(2025, 6, 4)
current_date = datetime.datetime.today()

total_days = (program_end - program_start).days
completed_days = (current_date - program_start).days
program_pct_complete = round((completed_days / total_days) * 100, 2)

# --- KPI Calculations ---
total_courses = len(df)
completed_courses = (df['Status'] == '✅ Completed').sum()
completed_courses_pct = round((completed_courses / total_courses) * 100, 1)

total_books = int(df['Completed Books'].sum())
total_pages = int(df['Book Pages'].sum())
total_required_days = df['Required Days'].sum()
total_completed_days = df['Completed Days'].sum()
program_day_pct = round((total_completed_days / total_required_days) * 100, 1) if total_required_days > 0 else 0

# --- Theses & Comps ---
theses_total = 45
theses_completed = 4
theses_pct = round((theses_completed / theses_total) * 100, 1)

comps_total = 45
comps_completed = 0
comps_pct = round((comps_completed / comps_total) * 100, 1)

# --- KPI Display (Reorganized Layout) ---
st.markdown("### 📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Program Progress (# of Program Days Completed)", f"{completed_days} / {total_days} days ({program_pct_complete}%)")
    st.metric("Course Progress (# of Course Days Completed)", f"{total_completed_days} / {total_required_days} ({program_day_pct}%)")
    st.metric("Course Completion (# of Courses Completed)", f"{completed_courses} / {total_courses} ({completed_courses_pct}%)")
with col2:
    st.metric("Books Completed", f"{total_books}")
    st.metric("Pages Read", f"{total_pages}")
with col3:
    st.metric("Theses Completed", f"{theses_completed} / {theses_total} ({theses_pct}%)")
    st.metric("Comps Completed", f"{comps_completed} / {comps_total} ({comps_pct}%)")

st.markdown("### 📚 Course Completion Status")
df['Progress %'] = (df['Completed Days'] / df['Required Days']).clip(0, 1)
bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('Course', sort='-y'),
    y=alt.Y('Progress %', scale=alt.Scale(domain=[0, 1])),
    color='Status',
    tooltip=['Course', 'Completed Days', 'Required Days', 'Status']
).properties(width=800, height=400)
st.altair_chart(bar, use_container_width=True)

# --- Unified Progress Bar Display ---
st.markdown("### 📈 Visual Progress Overview")

st.subheader("🗓️ Program Progress")
st.progress(program_pct_complete / 100)
st.caption(f"{completed_days} of {total_days} calendar days completed ({program_pct_complete}%)")

st.subheader("📅 Course Progress")
st.progress(program_day_pct / 100)
st.caption(f"{total_completed_days} of {total_required_days} course days completed ({program_day_pct}%)")

st.subheader("📘 Courses Completed")
st.progress(completed_courses / total_courses)
st.caption(f"{completed_courses} of {total_courses} courses completed ({completed_courses_pct}%)")

st.subheader("🎓 Theses")
st.progress(theses_completed / theses_total)
st.caption(f"{theses_completed} of {theses_total} theses completed ({theses_pct}%)")

st.subheader("🧠 Comps")
st.progress(comps_completed / comps_total)
st.caption(f"{comps_completed} of {comps_total} comps completed ({comps_pct}%)")



st.markdown("### Course Table")
visible_cols = ['Course', 'Course Number', 'Required Days', 'Completed Days', 'Completed Books', 'Book Pages', 'Status']
existing_cols = [col for col in visible_cols if col in df.columns]
if existing_cols:
    st.dataframe(df[existing_cols])
else:
    st.warning("⚠️ None of the expected columns were found in the data.")
