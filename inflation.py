import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

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
    col1, col2 = st.columns(2)
    data = fetch_data(inflation_URL)

    if data:
        df = pd.DataFrame(data)
        df['datum'] = pd.to_datetime(df['datum'])
        
        # Get the most recent year from the dataframe
        current_year = df['datum'].dt.year.max()
        last_year = current_year - 1

        # Get year range
        min_year = df['ar'].min()
        max_year = df['ar'].max()
        start_year, end_year = st.slider('Select a range of years', int(min_year), int(max_year), (int(max_year)-6, int(max_year)))

        filtered_df = df[(df['ar'].astype(int) >= start_year) & (df['ar'].astype(int) <= end_year)]

        #remove duplicates if any (using years and datum)
        filtered_df = filtered_df.drop_duplicates(subset=['datum', 'ar'])


        # Pivot the dataframe to have years as columns, months as index, and inflation as values
        pivot_df = filtered_df.pivot(index='datum', columns='ar', values='inflation')
        
        # Create a line chart for the selected range
        fig_range = px.line(pivot_df, x=pivot_df.index.month_name(), y=pivot_df.columns, title="Inflation Rate for Selected Range")
        with col1:
            st.plotly_chart(fig_range)
            # Download data for Inflation
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pivot_df.to_excel(writer, sheet_name="Inflationsdata")
            excel_data = output.getvalue()
            st.download_button(
                label="Ladda ner som Excel",
                data=excel_data,
                file_name='inflation_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        # Create a line chart for the filtered time series
        fig_all = px.line(filtered_df, x='datum', y='inflation', title="Inflation Rate for Selected Years")
        with col2: 
            st.plotly_chart(fig_all)
            # Download data for Inflation
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, sheet_name="Inflationsdata_historik")
            excel_data = output.getvalue()
            st.download_button(
                label="Ladda ner som Excel",
                data=excel_data,
                file_name='inflation_data_line.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
       
    else:
        st.write(f"Failed to fetch data from API.")
