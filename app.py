import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="SAASS Progress Dashboard", layout="wide")
st.title("📘 SAASS Progress Dashboard")
st.markdown("Auto-updating dashboard from Google Sheets — tracking books, courses, and program milestones.")

# --- Load Google Sheet Data ---
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUoPJRLuSRN1Y2GOSunfe0YtIECq2AeRzpVRoTVbDWbJ0Zw3J7VPUpKZjSDlKEYIeoELN39pBFUZJB/pub?gid=1897265951&single=true&output=csv"
df = pd.read_csv(url)

# --- Clean Columns and Header Row ---
df = df.dropna(how="all", axis=1)
df.columns = df.iloc[1].fillna("").str.strip()
df = df[2:].reset_index(drop=True)
df = df.rename(columns=lambda x: x.strip())

# Rename 'Course Title' to 'Course'
if 'Course Title' in df.columns:
    df = df.rename(columns={'Course Title': 'Course'})

# Drop rows with missing Course
df = df[df['Course'].notnull() & (df['Course'] != "")]

# --- Keep only the 10 known curriculum courses ---
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
df = df[df['Course'].isin(curriculum_courses)]

# --- Convert relevant columns ---
numeric_cols = ['Required Days', 'Completed Days', 'Completed Books', 'Book Pages']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- Add Status Logic ---
def determine_status(row):
    if row['Completed Days'] >= row['Required Days'] and row['Required Days'] > 0:
        return '✅ Completed'
    elif row['Completed Days'] == 0:
        return '🔴 Not Started'
    else:
        return '⏳ In Progress'

df['Status'] = df.apply(determine_status, axis=1)

# --- KPIs ---
total_courses = len(df)
completed_courses = (df['Status'] == '✅ Completed').sum()
not_started_courses = (df['Status'] == '🔴 Not Started').sum()
completed_courses_pct = round((completed_courses / total_courses) * 100, 1)

total_books = int(df['Completed Books'].sum())
total_pages = int(df['Book Pages'].sum())
total_required_days = df['Required Days'].sum()
total_completed_days = df['Completed Days'].sum()
program_day_pct = round((total_completed_days / total_required_days) * 100, 1) if total_required_days > 0 else 0

# Hardcoded extras
theses_total = 45
theses_completed = 4
theses_pct = round((theses_completed / theses_total) * 100, 1)
comps_total = 45
comps_completed = 0
comps_pct = 0.0

# --- Display KPIs ---
st.markdown("### 📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Overall Program Progress", f"{program_day_pct}%")
    st.metric("Course Completion", f"{completed_courses} / {total_courses} ({completed_courses_pct}%)")
with col2:
    st.metric("Books Completed", f"{total_books}")
    st.metric("Pages Read", f"{total_pages}")
with col3:
    st.metric("Theses Completed", f"{theses_completed} / {theses_total} ({theses_pct}%)")
    st.metric("Comps Completed", f"{comps_completed} / {comps_total} ({comps_pct}%)")

# --- Bar Chart of Progress ---
st.markdown("### 📚 Course Completion Status")
df['Progress %'] = (df['Completed Days'] / df['Required Days']).clip(0, 1)
bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('Course', sort='-y'),
    y=alt.Y('Progress %', scale=alt.Scale(domain=[0, 1])),
    color='Status',
    tooltip=['Course', 'Completed Days', 'Required Days', 'Status']
).properties(width=800, height=400)
st.altair_chart(bar, use_container_width=True)

# --- Pie Chart: Status Breakdown ---
status_counts = df['Status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']
pie = alt.Chart(status_counts).mark_arc().encode(
    theta='Count',
    color='Status',
    tooltip=['Status', 'Count']
).properties(title="Course Status Breakdown")
st.altair_chart(pie, use_container_width=True)

# --- Raw Table ---
st.markdown("### 🧾 Raw Course Table")
visible_cols = ['Course', 'Course Number', 'Required Days', 'Completed Days', 'Completed Books', 'Book Pages', 'Status']
st.dataframe(df[visible_cols])
