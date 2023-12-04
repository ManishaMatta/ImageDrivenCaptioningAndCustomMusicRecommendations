# streamlit run /Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/dataProcessing/mainApp.py
# python -m streamlit run your_script.py
# streamlit run https://raw.githubusercontent.com/streamlit/demo-uber-nyc-pickups/master/streamlit_app.py

import os
import streamlit as st
import tempfile
import numpy as np

st.title('Image Driven Captioning And Custom Music Recommendations')

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    image_uploaded = st.image(uploaded_file)

    st.write("********************************************************")
    label = ['caption1', 'caption3', 'caption3']
    caption = st.radio(
        'The captions generated for the image are',
        key="visibility",
        options=label,)
    hashtag = st.multiselect(
    'Hashtags',
    ['Green', 'Yellow', 'Red', 'Blue'])

    st.write("********************************************************")
    from musicProcess import music_recommendation
    caption_text1 = "Men garden green blue a women hand"
    caption_text2 = "Two young guys with shaggy hair look at their hands while hanging out in the yard ."
    caption_dict = music_recommendation(caption_text1+caption_text2)
    col1, col2 = st.columns(2)
    caption_radio = col1.radio("**Music Details**",  options=[tn['track_name'] for tn in caption_dict],)
    if caption_radio:
        track_dtls = [tn for tn in caption_dict if tn['track_name'] == caption_radio][0]
        col2.write("**Song Details**")

        col2.write("**Album :** "+track_dtls['album_name'])
        col2.write("**Artist :** "+track_dtls['artist_names'])
        col2.write("**Genres :** " + ('None' if track_dtls['track_genres'].strip() == '' else track_dtls['track_genres']))
        if track_dtls['track_preview_url'] is not np.NAN:
            st.audio(track_dtls['track_preview_url'], format='audio/mp3', start_time=0)
        else:
            st.markdown(f"[{track_dtls['track_link_spotify']}]({track_dtls['track_link_spotify']})")

        st.write("********************************************************")
        st.markdown("""<style>.big-font {font-size:20px !important;}</style>""", unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">Caption: {caption}</p>'
                    f'<p class="big-font">HashTags: {", ".join(["#"+i for i in hashtag])}</p>'
                    f'<p class="big-font">SongDetails: {caption_radio}</p>', unsafe_allow_html=True)
        st.write("********************************************************")
