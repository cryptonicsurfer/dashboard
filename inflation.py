import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# Move API endpoint out of the function to avoid duplication
inflation_URL = "https://nav.utvecklingfalkenberg.se/items/inflation?limit=-1"

@st.cache_data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

def show():
    # Implement the button to clear cache

    
    data = fetch_data(inflation_URL)

    if data:
        df = pd.DataFrame(data)
        df['datum'] = pd.to_datetime(df['datum'])
        
        # Get year range
        min_year = df['ar'].min()
        max_year = df['ar'].max()
        start_year, end_year = st.slider('Select a range of years', int(min_year), int(max_year), (int(max_year)-6, int(max_year)))

        filtered_df = df[(df['ar'].astype(int) >= start_year) & (df['ar'].astype(int) <= end_year)]

        # Pivot the dataframe to have years as columns, months as index, and inflation as values
        pivot_df = filtered_df.pivot(index='datum', columns='ar', values='inflation')
        
        # Create a line chart
        fig = px.line(pivot_df, x=pivot_df.index.month_name(), y=pivot_df.columns, title="Inflation Rate Over Time")

        st.plotly_chart(fig)

    else:
        st.write(f"Failed to fetch data from API.")
