import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# Define API endpoints
konkurser_URL = "https://nav.utvecklingfalkenberg.se/items/konkurser?limit=-1"
konkurser_anstallda_URL = "https://nav.utvecklingfalkenberg.se/items/konkurser_anstallda?limit=-1"

@st.cache_data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None
    
def compute_cumulative(df, column_name):
    df['year'] = df['datum'].dt.year
    df['month'] = df['datum'].dt.month
    df_sorted = df.sort_values(by=['year', 'month'])
    df_sorted['cumulative'] = df_sorted.groupby('year')[column_name].cumsum()
    return df_sorted

def save_to_excel(dataframe, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name)
    excel_data = output.getvalue()
    return excel_data

def show():
    # Fetch and process data for konkurser
    konkurser_data = fetch_data(konkurser_URL)
    if konkurser_data:
        konkurser_df = pd.DataFrame(konkurser_data)
        konkurser_df['datum'] = pd.to_datetime(konkurser_df['datum'])
        grouped_konkurser_yearly = konkurser_df.groupby([konkurser_df['datum'].dt.year, 'storleksklass'])['konkurser'].sum().unstack()
        fig_konkurser_yearly = px.bar(grouped_konkurser_yearly, title="Yearly Konkurser per Storleksklass")
        
        konkurser_cumulative = compute_cumulative(konkurser_df, 'konkurser')
        fig_cumulative_konkurser = px.line(konkurser_cumulative, x='month', y='cumulative', color='year', title="Monthly Accumulated Konkurser over Year")
        
        konkurser_excel = save_to_excel(grouped_konkurser_yearly, "Konkurser_Data")
    else:
        fig_konkurser_yearly = px.bar(title="Failed to fetch data for Konkurser")
        fig_cumulative_konkurser = None
        konkurser_excel = None

    # Fetch and process data for konkurser_anstallda
    anstallda_data = fetch_data(konkurser_anstallda_URL)
    if anstallda_data:
        anstallda_df = pd.DataFrame(anstallda_data)
        anstallda_df['datum'] = pd.to_datetime(anstallda_df['datum'])
        grouped_anstallda_yearly = anstallda_df.groupby([anstallda_df['datum'].dt.year, 'foretagsform'])['anstallda'].sum().unstack()
        fig_anstallda_yearly = px.bar(grouped_anstallda_yearly, title="Yearly Anställda per Företagsform")
        
        anstallda_cumulative = compute_cumulative(anstallda_df, 'anstallda')
        fig_cumulative_anstallda = px.line(anstallda_cumulative, x='month', y='cumulative', color='year', title="Monthly Accumulated Anställda over Year")
        
        anstallda_excel = save_to_excel(grouped_anstallda_yearly, "Anstallda_Data")
    else:
        fig_anstallda_yearly = px.bar(title="Failed to fetch data for Anställda")
        fig_cumulative_anstallda = None
        anstallda_excel = None

    # Display the plots and download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_konkurser_yearly)
        st.plotly_chart(fig_cumulative_konkurser)
        if konkurser_excel:
            st.download_button(
                label="Ladda ner Konkurser som Excel",
                data=konkurser_excel,
                file_name='konkurser_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    with col2:
        st.plotly_chart(fig_anstallda_yearly)
        st.plotly_chart(fig_cumulative_anstallda)
        if anstallda_excel:
            st.download_button(
                label="Ladda ner Anställda som Excel",
                data=anstallda_excel,
                file_name='anstallda_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            st.write(konkurser_df)
