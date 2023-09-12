import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
from io import BytesIO

flyttnetto_URL = "https://nav.utvecklingfalkenberg.se/items/flyttnetto?limit=-1"

@st.cache_data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

def save_to_excel(data, sheet_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name=sheet_name)
    return output.getvalue()

def show():
    data = fetch_data(flyttnetto_URL)

    if not data:
        st.write(f"Failed to fetch data from API.")
        return

    df = pd.DataFrame(data)
    df['datum'] = pd.to_datetime(df['datum'])
    df['year'] = df['datum'].dt.year

    grouped_net_migration = df.groupby('datum')['flyttnetto'].sum().reset_index()
    fig_net_migration = px.bar(grouped_net_migration, x="datum", y="flyttnetto", title="Flyttnetto per år")

    age_group_size_10yr = 10
    bins_10yr = list(range(0, 101, age_group_size_10yr))
    labels_10yr = [f"{i}-{i + age_group_size_10yr - 1}" for i in bins_10yr[:-1]]
    df['age_group_10yr'] = pd.cut(df['alder'], bins=bins_10yr, labels=labels_10yr, right=False)
    grouped_10yr = df.groupby(['datum', 'age_group_10yr'])['flyttnetto'].sum().unstack()

    yearly_cumulative = df.groupby(['year', 'age_group_10yr'])['flyttnetto'].sum().groupby(level=1).cumsum().unstack()
    fig_relative_barmode = go.Figure(data=[go.Bar(x=yearly_cumulative.index, y=yearly_cumulative[age_group], name=age_group) for age_group in yearly_cumulative.columns])
    fig_relative_barmode.update_layout(barmode='relative', title_text="Ackumulerad inflyttning över tid per åldersgrupp (Relative Barmode)")

    total_yearly_cumulative = df.groupby('year')['flyttnetto'].sum().cumsum()
    fig_total_yearly = px.line(total_yearly_cumulative, title="Total Ackumulerad inflyttning över tid")

    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_net_migration)
        st.download_button(
            label="Ladda ner som Excel",
            data=save_to_excel(grouped_net_migration, "Net_Migration_Data"),
            file_name='net_migration_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        

        st.write("---")

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)

        st.plotly_chart(fig_relative_barmode)
        st.download_button(
            label="Ladda ner som Excel (Relative Barmode Data)",
            data=save_to_excel(yearly_cumulative, "Yearly_Cumulative_Data"),
            file_name='yearly_cumulative_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    with col2:
        st.plotly_chart(fig_total_yearly)
        st.download_button(
            label="Ladda ner som Excel",
            data=save_to_excel(total_yearly_cumulative, "Total_Yearly_Cumulative"),
            file_name='total_yearly_cumulative.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        st.write("---")

        min_year = df['datum'].dt.year.min()
        max_year = df['datum'].dt.year.max()
        start_year, end_year = st.slider('Select a range of years', min_year, max_year, (max_year-10, max_year))
        filtered_df = df[(df['datum'].dt.year >= start_year) & (df['datum'].dt.year <= end_year)]
        filtered_df_grouped = filtered_df.groupby(['datum', 'age_group_10yr'])['flyttnetto'].sum().groupby(level=1).cumsum().reset_index()
        fig_cumsum = px.line(filtered_df_grouped, x="datum", y="flyttnetto", color="age_group_10yr", title="Ackumulerat flyttnetto över tid på åldersgruppsnivå")
        
        st.plotly_chart(fig_cumsum)
        st.download_button(
            label="Ladda ner som Excel",
            data=save_to_excel(filtered_df_grouped, "filtered_df_grouped"),
            file_name='filtered_df_grouped.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

