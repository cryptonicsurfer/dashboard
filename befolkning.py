import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
from io import BytesIO

# API endpoint
befolkning_URL = "https://nav.utvecklingfalkenberg.se/items/befolkning?limit=-1"

# Så här kan man kommentera
@st.cache_data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

@st.cache_data
def compute_age_group_data(df):
    age_group_size = 10
    bins = list(range(0, 101, age_group_size))
    labels = [f"{i}-{i + age_group_size - 1}" for i in bins[:-1]]

    df['age_group_10yr'] = pd.cut(df['alder'], bins=bins, labels=labels, right=False, include_lowest=True)
    return df.groupby(['datum', 'age_group_10yr'])['befolkningsmangd'].sum().unstack()

@st.cache_data
def compute_avg_age(df):
    df['weighted_age'] = df['alder'] * df['befolkningsmangd']
    return df.groupby('datum').apply(lambda x: x['weighted_age'].sum() / x['befolkningsmangd'].sum()).reset_index(name="avg_age")

def show():
    data = fetch_data(befolkning_URL)

    if data:
        df = pd.DataFrame(data)
        col1, col2, = st.columns(2)

        with col1:
            grouped_10yr = compute_age_group_data(df)
            fig_age_group_10yr = px.bar(grouped_10yr, barmode='stack', title="Befolkning per åldersgrupp över tid")
            st.plotly_chart(fig_age_group_10yr)

            # Download data for Age Group
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                grouped_10yr.to_excel(writer, sheet_name="Age_Group_Data")
            excel_data = output.getvalue()
            st.download_button(
                label="Ladda ner som Excel",
                data=excel_data,
                file_name='age_group_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        with col2: 
            grouped_avg_age = compute_avg_age(df)
            fig_avg_age = px.line(grouped_avg_age, x="datum", y="avg_age", title="Medelålder över tid")
            st.plotly_chart(fig_avg_age)

            # Download data for Average Age
            output_avg = BytesIO()
            with pd.ExcelWriter(output_avg, engine='xlsxwriter') as writer:
                grouped_avg_age.to_excel(writer, sheet_name="Average_Age_Data")
            excel_data_avg = output_avg.getvalue()
            st.download_button(
                label="Ladda ner som Excel",
                data=excel_data_avg,
                file_name='average_age_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    else:
        st.write(f"Failed to fetch data from API. Status code: {response.status_code}") 
