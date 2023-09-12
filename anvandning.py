import streamlit as st

def show():
    st.write("hello")
    video_file = open('myvideo.mp4', 'rb')  # 'myvideo.mp4' is correctly passed as a string here
    video_bytes = video_file.read()

    st.video(video_bytes)


    #displaying a local video file

# video_file = open('FILENAME', 'rb') #enter the filename with filepath

# video_bytes = video_file.read() #reading the file

# st.video(video_bytes) #displaying the video

