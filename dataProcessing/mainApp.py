# streamlit run /Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/dataProcessing/mainApp.py
# python -m streamlit run your_script.py
# streamlit run https://raw.githubusercontent.com/streamlit/demo-uber-nyc-pickups/master/streamlit_app.py
import os
from io import StringIO
# import IPython
from IPython.display import IFrame
from IPython.display import display
import streamlit as st
# from streamlit.components.v1 import html
# from streamlit.components.v1 import IFrame
import pandas as pd
import tempfile
import numpy as np
import time
import pickle
# from IPython.display import Image
from streamlit_player import st_player

st.title('Image Driven Captioning And Custom Music Recommendations')

uploaded_file = st.file_uploader("Choose a file")
# uploaded_file
if uploaded_file is not None:
    temp_dir=tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    # st.write(path)
    # st.write(uploaded_file.name)
    st.image(uploaded_file)
    l = ['caption1', 'caption3', 'caption3']

    # @todo add button to "RETREIVE"
    caption = st.radio(
        'The captions generated for the image are',
        key="visibility",
        options=l,)
    hashtag = st.multiselect(
        'Sample hashtags',
        ['Green', 'Yellow', 'Red', 'Blue'])

    audio_url="https://p.scdn.co/mp3-preview/4bd2dc84016f3743add7eea8b988407b1b900672?cid=9d7429fddef847139c8ae837b6bcdd92"
    st.audio(audio_url, format='audio/mp3', start_time=0)

st.write("********************************************************")

