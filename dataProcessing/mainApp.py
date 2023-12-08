# streamlit run /Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/dataProcessing/mainApp.py
# python -m streamlit run your_script.py
# streamlit run /Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/dataProcessing/mainApp.py

import os
import streamlit as st
import tempfile
import numpy as np
from musicProcess import music_recommendation

st.title('Image Driven Captioning And Custom Music Recommendations')

uploaded_file = st.file_uploader("Choose a file")

# @st.cache(suppress_st_warning=True)
@st.cache_data(experimental_allow_widgets=True)
def music_app(caption):
    caption_dict = music_recommendation("caption")
    print(caption_dict)
    col1, col2 = st.columns(2)
    song_radio = col1.radio("**Music Details**",  options=[tn['track_name'] for tn in caption_dict],)
    if song_radio:
        track_dtls = [tn for tn in caption_dict if tn['track_name'] == song_radio][0]
        col2.write("**Song Details**")
        col2.write("**Album :** "+track_dtls['album_name'])
        col2.write("**Artist :** "+track_dtls['artist_names'])
        col2.write("**Genres :** " + ('None' if track_dtls['track_genres'].strip() == '' else track_dtls['track_genres']))
        if track_dtls['track_preview_url'] is not np.NAN:
            st.audio(track_dtls['track_preview_url'], format='audio/mp3', start_time=0)
        else:
            st.markdown(f"[{track_dtls['track_link_spotify']}]({track_dtls['track_link_spotify']})")

print(st.session_state)

if uploaded_file is not None:
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    image_uploaded = st.image(uploaded_file)
    caption_text1 = "A little girl climbing the stairs to her playhouse"
    # caption_button = st.button("Generate Captions", type="primary")
    # button_state1
    st.write("********************************************************")
    # if caption_button:
        # st.session_state.caption_button = True
    label = ['caption1', 'caption3', 'caption3']
    caption_radio_val = st.radio(
        'The captions generated for the image are',
        key="caption_radio",
        options=label)
    hash_multiselect = st.multiselect(
        'Hashtags',
        ['Green', 'Yellow', 'Red', 'Blue'], key='hashtag_multisel')
    caption_text2 = "Four men on top of a tall structure"
    caption_dict = music_recommendation("caption")
    print(caption_dict)
    col1, col2 = st.columns(2)
    song_radio = col1.radio("**Music Details**",  options=[tn['track_name'] for tn in caption_dict],)
    if song_radio:
        track_dtls = [tn for tn in caption_dict if tn['track_name'] == song_radio][0]
        col2.write("**Song Details**")
        col2.write("**Album :** "+track_dtls['album_name'])
        col2.write("**Artist :** "+track_dtls['artist_names'])
        col2.write("**Genres :** " + ('None' if track_dtls['track_genres'].strip() == '' else track_dtls['track_genres']))
        if track_dtls['track_preview_url'] is not np.NAN:
            st.audio(track_dtls['track_preview_url'], format='audio/mp3', start_time=0)
        else:
            st.markdown(f"[{track_dtls['track_link_spotify']}]({track_dtls['track_link_spotify']})")
    if st.button("Generate Songs", type="primary", key='song_button') and caption_radio_val is not None:
        st.write("********************************************************")
        st.markdown("""<style>.big-font {font-size:20px !important;}</style>""", unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">Caption: {caption}</p>'
                f'<p class="big-font">HashTags: {", ".join(["#"+i for i in hashtag])}</p>'
                f'<p class="big-font">SongDetails: {caption_radio}</p>', unsafe_allow_html=True)
        st.write("********************************************************")
        # s=st.State()
        # state = st.session_state

        # print(s)
        # print(st.session_state.keys)
        # st.session_state.caption_radio = caption_radio_val
        # music_app(caption_text1+caption_text2)
        # st.session_state.song_button = True
    st.write("********************************************************")
    print("*&*&*&*&*&*&*&*&*&*&")




#st.experimental_rerun()

