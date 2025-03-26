import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="SAASS Progress", layout="wide")

st.title("?? SAASS Progress Dashboard")
st.markdown("This dashboard updates automatically from a live Google Sheet.")

# Load the Google Sheet data
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUoPJRLuSRN1Y2GOSunfe0YtIECq2AeRzpVRoTVbDWbJ0Zw3J7VPUpKZjSDlKEYIeoELN39pBFUZJB/pub?gid=1897265951&single=true&output=csv"

try:
    df = pd.read_csv(url)
    st.success("? Data loaded successfully!")

    st.write("### Data Preview")
    st.dataframe(df)

    # Try plotting if expected columns are available
    if 'Date' in df.columns and 'Progress' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='Date:T',
            y='Progress:Q',
            tooltip=['Date', 'Progress']
        ).properties(
            title="?? SAASS Progress Over Time",
            width=700,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Chart not generated. Make sure your Google Sheet has 'Date' and 'Progress' columns.")

except Exception as e:
    st.error(f"Failed to load data: {e}")
