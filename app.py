import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="SAASS Progress Dashboard", layout="wide")
st.title("📘 SAASS Progress Dashboard")
st.markdown("Auto-updating dashboard from Google Sheets — tracking books, courses, and program milestones.")

# --- Load Google Sheet Data ---
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUoPJRLuSRN1Y2GOSunfe0YtIECq2AeRzpVRoTVbDWbJ0Zw3J7VPUpKZjSDlKEYIeoELN39pBFUZJB/pub?gid=1897265951&single=true&output=csv"
df = pd.read_csv(url)

# --- Clean Data ---
df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)
df = df.rename(columns={' Book Pages': 'Book Pages'})
for col in ['Required Days', 'Completed Days', '% Complete', 'Completed Books', 'Book Pages']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- KPIs ---
total_courses = df['Course'].nunique()
completed_courses = df[df['% Complete'] == 1].shape[0]
completed_courses_pct = round((completed_courses / total_courses) * 100, 1)

total_books = int(df['Completed Books'].sum())
total_pages = int(df['Book Pages'].sum())

total_required_days = df['Required Days'].sum()
total_completed_days = df['Completed Days'].sum()
program_day_pct = round((total_completed_days / total_required_days) * 100, 1)

# Hard-coded for now; could automate from sheet later
theses_total = 45
theses_completed = 4
theses_pct = round((theses_completed / theses_total) * 100, 1)

comps_total = 45
comps_completed = 0
comps_pct = 0.0

# --- KPI Display ---
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

# --- Bar Chart of Course Progress ---
st.markdown("### 📚 Course Completion Status")
bar = alt.Chart(df).mark_bar().encode(
    x=alt.X('Course', sort='-y'),
    y=alt.Y('% Complete', scale=alt.Scale(domain=[0, 1])),
    tooltip=['Course', '% Complete']
).properties(width=800, height=400)
st.altair_chart(bar, use_container_width=True)

# --- Pie Chart ---
completed = completed_courses
incomplete = total_courses - completed_courses
pie_data = pd.DataFrame({
    'Status': ['Completed', 'Incomplete'],
    'Count': [completed, incomplete]
})
pie = alt.Chart(pie_data).mark_arc().encode(
    theta='Count',
    color='Status',
    tooltip=['Status', 'Count']
).properties(title="Course Completion Breakdown")
st.altair_chart(pie, use_container_width=True)

# --- Raw Data Table ---
st.markdown("### 🧾 Raw Course Table")
st.dataframe(df[['Course', 'Course Number', 'Required Days', 'Completed Days', 'Completed Books', 'Book Pages', '% Complete']])
