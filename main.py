import streamlit as st
from befolkning import show as show_befolkning
from anvandning import show as show_anvandning
from flyttnetto import show as show_flyttnetto
from inflation import show as show_inflation
from konkurser import show as show_konkurser

# Import other pages similarly

st.set_page_config(layout="wide")
st.header('Falkenberg Dashboard :chart:')

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Användning", "Befolkning", "Flyttnetto", "Inflation", "Konkurser"])  # Add other pages as needed

    if selection == "Befolkning":
        show_befolkning()
    elif selection == "Användning":
        show_anvandning()
    elif selection == "Flyttnetto":
        show_flyttnetto()
    elif selection == "Inflation":
        show_inflation()
    elif selection == "Konkurser":
        show_konkurser()
    # Add more elif conditions for other pages

if __name__ == "__main__":
    main()
