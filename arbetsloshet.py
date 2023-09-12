# arbetsloshet.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

def fetch_data():
    url = "https://nav.utvecklingfalkenberg.se/items/arbetsloshet?limit=-1"
    response = requests.get(url)
    return response.json()['data']

def create_line_chart1(data):
    fig = px.line(data, x='datum', y='arbetsloshet', title='Arbetslöshet över perioden, %', markers=True)
    st.plotly_chart(fig)


def create_line_chart2(data):
    fig2 = px.scatter(data, x='datum', y='arbetsloshet', title='Arbetslöshet över perioden, %',
                     color='arbetsloshet', color_continuous_scale=["teal", "red"])

    # Remove the color axis to the right
    fig2.layout.coloraxis.showscale = False
    st.plotly_chart(fig2)

def create_heatmap(data):
    data = pd.DataFrame(data)
    data['year'] = data['datum'].apply(lambda x: x.split('-')[0])
    data['month'] = data['datum'].apply(lambda x: x.split('-')[1])
    heatmap_data = data.pivot(index='year', columns='month', values='arbetsloshet')
    fig = px.imshow(heatmap_data, title='Månads "heatmap" av arbetslöshet per år', labels=dict(x="Month", y="Year", color="Rate"), color_continuous_scale="Viridis")
    st.plotly_chart(fig)

def show():
    st.title("Arbetslöshet i Falkenberg sedan 2020")
       
    data = fetch_data()

    col1, col2 = st.columns(2)

    with col1:
        # Line chart visualization
        create_line_chart1(data)
        create_line_chart2(data)

    with col2:
        # Heatmap visualization
        create_heatmap(data)
