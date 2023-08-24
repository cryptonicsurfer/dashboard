import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
from io import BytesIO

# Move API endpoint out of the function to avoid duplication
flyttnetto_URL = "https://nav.utvecklingfalkenberg.se/items/flyttnetto?limit=-1"

@st.cache_data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

def show():
    
    
    data = fetch_data(flyttnetto_URL)

    if data:
        df = pd.DataFrame(data)
        df['datum'] = pd.to_datetime(df['datum'])

        col1, col2 = st.columns(2)

        # Creating age group buckets
        age_group_size_10yr = 10
        bins_10yr = list(range(0, 101, age_group_size_10yr))
        labels_10yr = [f"{i}-{i + age_group_size_10yr - 1}" for i in bins_10yr[:-1]]
        df['age_group_10yr'] = pd.cut(df['alder'], bins=bins_10yr, labels=labels_10yr, right=False)

        grouped_10yr = df.groupby(['datum', 'age_group_10yr'])['flyttnetto'].sum().unstack()
        fig_age_group_10yr = px.bar(grouped_10yr, barmode='stack', title="Flyttnetto per åldersgrupp över tid")

        with col1:
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

        # Line chart of net migration
        grouped_net_migration = df.groupby('datum')['flyttnetto'].sum().reset_index()
        fig_net_migration = px.line(grouped_net_migration, x="datum", y="flyttnetto", title="Net Migration Over Time")

        with col2:
            st.plotly_chart(fig_net_migration)
            # Download data for Net Migration
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                grouped_net_migration.to_excel(writer, sheet_name="Net_Migration_Data")
            excel_data = output.getvalue()
            st.download_button(
                label="Ladda ner som Excel",
                data=excel_data,
                file_name='net_migration_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        # Cumulative sum for flyttnetto
        df_grouped = df.groupby(['datum', 'age_group_10yr'])['flyttnetto'].sum().groupby(level=1).cumsum().reset_index()
        
       # Filter based on slider
        min_year = df['datum'].dt.year.min()
        max_year = df['datum'].dt.year.max()
        start_year, end_year = st.slider('Select a range of years', min_year, max_year, (max_year-10, max_year))

        filtered_df = df[(df['datum'].dt.year >= start_year) & (df['datum'].dt.year <= end_year)]

        # Compute the cumulative sum on the filtered dataframe
        filtered_df_grouped = filtered_df.groupby(['datum', 'age_group_10yr'])['flyttnetto'].sum().groupby(level=1).cumsum().reset_index()

        fig_cumsum = px.line(filtered_df_grouped, x="datum", y="flyttnetto", color="age_group_10yr", title="Accumulated Flyttnetto Over Time")

        st.plotly_chart(fig_cumsum)
        # Download data for Net Migration
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df_grouped.to_excel(writer, sheet_name="filtered_df_grouped")
        excel_data = output.getvalue()
        st.download_button(
            label="Ladda ner som Excel",
            data=excel_data,
            file_name='filtered_df_grouped.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    else:
        st.write(f"Failed to fetch data from API. Status code: {response.status_code}")
