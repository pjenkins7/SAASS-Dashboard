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
df = df.dropna(how="all", axis=1)  # drop empty columns
df.columns = df.iloc[1].fillna("").str.strip()  # row 1 = header
df = df[2:].reset_index(drop=True)

# Rename 'Course Title' to 'Course' for clarity
if 'Course Title' in df.columns:
    df = df.rename(columns={'Course Title': 'Course'})

# Strip all column names to remove hidden spaces
df = df.rename(columns=lambda x: x.strip())

# Ensure numeric columns are parsed correctly
numeric_cols = ['Required Days', 'Completed Days', '% Complete', 'Completed Books', 'Book Pages']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# --- KPIs ---
total_courses = df['Course'].nunique() if 'Course' in df.columns else 0
completed_courses = df[df['% Complete'] >= 0.999].shape[0]
completed_courses_pct = round((completed_courses / total_courses) * 100, 1) if total_courses > 0 else 0

total_books = int(df['Completed Books'].sum()) if 'Completed Books' in df.columns else 0
total_pages = int(df['Book Pages'].sum()) if 'Book Pages' in df.columns else 0

total_required_days = df['Required Days'].sum() if 'Required Days' in df.columns else 0
total_completed_days = df['Completed Days'].sum() if 'Completed Days' in df.columns else 0
program_day_pct = round((total_completed_days / total_required_days) * 100, 1) if total_required_days > 0 else 0

# Hardcoded extras — can be dynamic later
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
if '% Complete' in df.columns and 'Course' in df.columns:
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X('Course', sort='-y'),
        y=alt.Y('% Complete', scale=alt.Scale(domain=[0, 1])),
        tooltip=['Course', '% Complete']
    ).properties(width=800, height=400)
    st.altair_chart(bar, use_container_width=True)

# --- Pie Chart ---
if total_courses > 0:
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

# Define the columns we want to show
expected_cols = ['Course', 'Course Number', 'Required Days', 'Completed Days', 'Completed Books', 'Book Pages', '% Complete']
available_cols = [col for col in expected_cols if col in df.columns]

# Show only available ones (avoids KeyError)
if available_cols:
    st.dataframe(df[available_cols])
else:
    st.warning("⚠️ None of the expected columns were found in the data.")
