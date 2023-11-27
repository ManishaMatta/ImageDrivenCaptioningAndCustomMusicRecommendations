import csv
import os
import re
from pathlib import Path

import numpy as np
import requests
import json
import subprocess
import pandas as pd
import time
from builtins import *
from datetime import datetime
from IPython.display import IFrame
from bs4 import BeautifulSoup
from unidecode import unidecode
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS
import gensim
from gensim.utils import simple_preprocess
import gensim.corpora as corpora
from pprint import pprint
from datetime import datetime
# import textProcess
#import spotify
from nltk.corpus import stopwords
nltk.download('stopwords')



import warnings
warnings.filterwarnings("ignore")

# https://nitratine.net/blog/post/finding-emotion-in-music-with-python/
# https://towardsdatascience.com/predicting-my-mood-using-my-spotify-data-2e898add122a


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
class MusicModule:
    ACCESS_TOKEN = ''
    TOKEN_TIME = ''
    LYRICS_TOPICS = ''
    id2word=''

    @staticmethod
    def generate_bearer_token():
        URL = "https://accounts.spotify.com/api/token"
        HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}
        PARAMS = {"grant_type": "client_credentials",
                  "client_id": "9d7429fddef847139c8ae837b6bcdd92",
                  "client_secret": "75bef32687344efa8a6f2a7e2b4ce132"
                  }
        MusicModule.TOKEN_TIME = datetime.now().strftime("%Y%m%d%H%M%S")
        response = requests.post(URL, headers=HEADER, data=PARAMS)
        if response.status_code == 200:
            print("Request was successful")
            MusicModule.ACCESS_TOKEN = response.json().get('access_token')
        else:
            print("Request failed with status code:", response.status_code)

    @staticmethod
    def validate_access_token():
        if (MusicModule.ACCESS_TOKEN == '' or (
                datetime.now().strftime("%Y%m%d%H%M%S") - MusicModule.TOKEN_TIME) >= 3600):
            return False
        else:
            return True

    @staticmethod
    def spotify_trendy_track(url):
        time.sleep(30)
        command = f"curl --request GET --url '{url}' --header 'Authorization: Bearer {MusicModule.ACCESS_TOKEN}'"
        result = subprocess.check_output(command, shell=True, text=True)
        return result

    @staticmethod
    def is_valid_link(url, retry_url=1):
        try:
            response = requests.head(url)
            if response.status_code < 400:
                return url
            else:
                if retry_url == 1:
                    link_nval = url.lower().split('-sped-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 2)
                    else:
                        return MusicModule.is_valid_link(url, 2)
                elif retry_url == 2:
                    link_nval = url.lower().split('-from-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 3)
                    else:
                        return MusicModule.is_valid_link(url, 3)
                elif retry_url == 3:
                    link_nval = url.lower().split('-with-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 4)
                    else:
                        return MusicModule.is_valid_link(url, 4)
                elif retry_url == 4:
                    link_nval = url.lower().split('-w-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 5)
                    else:
                        return MusicModule.is_valid_link(url, 5)
                elif retry_url == 5:
                    link_nval = url.lower().split('-single-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 6)
                    else:
                        return MusicModule.is_valid_link(url, 6)
                elif retry_url == 6:
                    link_nval = url.lower().split('-club-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 7)
                    else:
                        return MusicModule.is_valid_link(url, 7)
                elif retry_url == 7:
                    link_nval = url.lower().split('-2011-')
                    if len(link_nval) > 1:
                        new_url = link_nval[0] + '-lyrics'
                        return MusicModule.is_valid_link(new_url, 8)
                    else:
                        return MusicModule.is_valid_link(url, 8)
                elif retry_url == 8:
                    if url.find('&') != -1:
                        new_url = url.lower().replace('&', 'and')
                        return MusicModule.is_valid_link(new_url, 9)
                    else:
                        return MusicModule.is_valid_link(url, 9)
                else:
                    return url

        except requests.exceptions.RequestException:
            print("exception", retry_url)
            return url

    @staticmethod
    def lyric_url(lyric_url):
        if lyric_url == '':
            print("*****")
        else:
            pass

        if type(lyric_url) is str:
            return unidecode(((lyric_url.split('(')[0] + lyric_url.split(')')[1] if (
                    len(lyric_url.split(')')) > 1 and len(lyric_url.split(')')[1]) > 0) else lyric_url.replace('(',
                                                                                                               '').replace(
                ')', ''))).split('[')[0].split("feat.")[0].strip().replace(",", "-and-").replace("/", "").replace(".",
                                                                                                                  "").replace(
                "\'", "").replace(" ", "-").replace("’", "").replace("--", "-").replace('--', '-').replace('?',
                                                                                                           '').replace(
                '!', ''))
        else:
            return unidecode(
                "-".join("-and-".join(lyric_url).strip().split()).replace(".", "").replace(",", "").replace('\'',
                                                                                                            '').replace(
                    '--', '-').replace('?', '').replace('!', ''))

    @staticmethod
    def spotify_features(row_dict, track_id):
        url = "https://api.spotify.com/v1/audio-features?ids="+track_id
        data = json.loads(MusicModule.spotify_trendy_track(url))
        try:
            row_dict['track_danceability'] = data['audio_features'][0]['danceability']
            row_dict['track_energy'] = data['audio_features'][0]['energy']
            row_dict['track_loudness'] = data['audio_features'][0]['loudness']
            row_dict['track_speechiness'] = data['audio_features'][0]['speechiness']
            row_dict['track_acousticness'] = data['audio_features'][0]['acousticness']
            row_dict['track_instrumentalness'] = data['audio_features'][0]['instrumentalness']
            row_dict['track_liveness'] = data['audio_features'][0]['liveness']
            row_dict['track_tempo'] = data['audio_features'][0]['tempo']
            row_dict['track_track_href'] = data['audio_features'][0]['track_href']
        except Exception as e:
            print(e)

# curl --request GET --url 'https://api.spotify.com/v1/audio-features?ids=1Qrg8KqiBpW07V7PNxwwwL' --header 'Authorization: Bearer BQDhPoOy_kNebEVHtrjY2APhkPDCHgCI7oExIpznJDNvTN0ZHJpNXEVg1OZAyxZ6yVeX3prM_C82M6AT56xn9ROdwUL8XWN6aCNBNTEiELjmD19hB_Y'
# curl --request GET --url https://api.spotify.com/v1/artists/7tYKF4w9nC0nq9CsPZTHyP --header 'Authorization: Bearer BQDqs7dUPGuRGzrpqVCUpBcSW6UmRVpYXvmSz-yX6RpmPl3F4OKuJyNQA2-dHdlmoowiHaySKJsQMKAqgsdR-3Q259te6S7lkIui5H9W9u3f9b0LSns'

    @staticmethod
    def spotify_artist_genres(row_dict, artist_id):
        genre_list = []
        for a_id in artist_id:
            url = "https://api.spotify.com/v1/artists/"+a_id
            data = json.loads(MusicModule.spotify_trendy_track(url))
            genre_list += data['genres']
        row_dict['track_genres'] = genre_list

    @staticmethod
    def spotify():
        url = "https://api.spotify.com/v1/playlists/6QGk7b8naF3ZPljgPtWMAD"
        MusicModule.generate_bearer_token()
        if not MusicModule.validate_access_token:
            MusicModule.generate_bearer_token()

        data = json.loads(MusicModule.spotify_trendy_track(url))
        base_row_dict = {}
        data_list = [data]
        base_row_dict['playlist_name'] = data['name']
        base_row_dict['playlist_followers'] = data['followers']['total']
        base_row_dict['playlist_uri'] = data['uri']
        base_row_dict['playlist_id'] = data['id']
        base_row_dict['total_tracks'] = data['tracks']['total']
        page = data['tracks']['next']
        while str(page) != 'None':
            data = json.loads(MusicModule.spotify_trendy_track(page))
            data_list.append(data)
            page = data['next']

        rows = []
        for i in data_list:
            if ('tracks' in i.keys()) and ('items' not in i.keys()):
                for j in i['tracks']['items']:
                    row_dict = base_row_dict.copy()
                    row_dict['track_added_time'] = j['added_at']
                    row_dict['track_id'] = j['track']['id']
                    row_dict['artist_names'] = [nm['name'] for nm in j['track']['album']['artists']]
                    row_dict['artist_id'] = [nm['id'] for nm in j['track']['album']['artists']]
                    row_dict['album_available_market'] = j['track']['album']['available_markets']
                    row_dict['album_name'] = j['track']['album']['name']
                    row_dict['album_type'] = j['track']['album']['type']
                    row_dict['album_release_date'] = j['track']['album']['release_date']
                    row_dict['album_date_precision'] = j['track']['album']['release_date_precision']
                    row_dict['album_tracks'] = j['track']['album']['total_tracks']
                    row_dict['track_available_market'] = j['track']['available_markets']
                    row_dict['track_duration_ms'] = j['track']['duration_ms']
                    row_dict['track_link_spotify'] = j['track']['external_urls']['spotify']  # IMP: link of the song
                    row_dict['track_name'] = j['track']['name']
                    row_dict['track_popularity'] = j['track']['popularity']
                    row_dict['track_preview_url'] = j['track']['preview_url']  # IMP : play song directly
                    MusicModule.spotify_features(row_dict, j['track']['id'])
                    MusicModule.spotify_artist_genres(row_dict, row_dict['artist_id'])
                    MusicModule.sentiment_lyrics(row_dict)
                    rows.append(row_dict)
            else:
                for j in i['items']:
                    row_dict = base_row_dict.copy()
                    row_dict['track_added_time'] = j['added_at']
                    row_dict['track_id'] = j['track']['id']
                    row_dict['artist_names'] = [nm['name'] for nm in j['track']['album']['artists']]
                    row_dict['artist_id'] = [nm['id'] for nm in j['track']['album']['artists']]
                    row_dict['album_available_market'] = j['track']['album']['available_markets']
                    row_dict['album_name'] = j['track']['album']['name']
                    row_dict['album_type'] = j['track']['album']['type']
                    row_dict['album_release_date'] = j['track']['album']['release_date']
                    row_dict['album_date_precision'] = j['track']['album']['release_date_precision']
                    row_dict['album_tracks'] = j['track']['album']['total_tracks']
                    row_dict['track_available_market'] = j['track']['available_markets']
                    row_dict['track_duration_ms'] = j['track']['duration_ms']
                    row_dict['track_link_spotify'] = j['track']['external_urls']['spotify']  # IMP: link of the song
                    row_dict['track_name'] = j['track']['name']
                    row_dict['track_popularity'] = j['track']['popularity']
                    row_dict['track_preview_url'] = j['track']['preview_url']  # IMP : play song directly
                    MusicModule.spotify_features(row_dict, j['track']['id'])
                    MusicModule.spotify_artist_genres(row_dict, row_dict['artist_id'])
                    MusicModule.sentiment_lyrics(row_dict)
                    rows.append(row_dict)
        return pd.DataFrame(rows)

    @staticmethod
    def lda_lyrics(spotify_df):
        def sent_to_words(sentences):
            for sentence in sentences:
                yield gensim.utils.simple_preprocess(str(sentence), deacc=True)

        def remove_stopwords(texts):
            return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

        def pre_process(lyrics):
            if isinstance(lyrics, str):
                cleaned_lyrics = lyrics.strip().replace('\d+', '')
                cleaned_lyrics = re.sub('[,\.!?]', '', cleaned_lyrics.lower())
                return cleaned_lyrics
            else:
                print(lyrics)

        spotify_df.dropna(subset=['track_lyrics'])
        spotify_df['track_lyrics_processed'] = spotify_df['track_lyrics'].apply(pre_process)
        stop_words = stopwords.words('english')
        stop_words.extend(['i','i\'m','hii','hi','might','even','got','ooh','oh','wanna','na','yeah','would','from', 'to', 'do', 'be', 'in', 'for', 'my', 'how', 'of', 'get', 'know', 'uh', 'ya', 'like', 'iz' ])

        data = spotify_df['track_lyrics_processed'].values.tolist()
        data_words = list(sent_to_words(data))
        data_words = remove_stopwords(data_words)
        MusicModule.id2word = corpora.Dictionary(data_words)
        texts = data_words
        corpus = [MusicModule.id2word.doc2bow(text) for text in texts]
        lda_model = gensim.models.LdaModel(corpus=corpus, id2word=MusicModule.id2word, num_topics=10)
        pprint(lda_model.print_topics())
        MusicModule.LYRICS_TOPICS = lda_model.print_topics()

        # @TODO identify/correlate qoutes received with the lyrics[LDA] and filter the needed group lyrics

        spotify_df['track_lyrics_processed_list'] = spotify_df['track_lyrics_processed'].apply(lambda x:remove_stopwords(list(sent_to_words([x]))))
        spotify_df['Bow_Vector'] = spotify_df['track_lyrics_processed_list'].apply(lambda x: [MusicModule.id2word.doc2bow(j) for j in x])
        spotify_df['lyrics_topic_distribution'] = spotify_df['Bow_Vector'].apply(lambda x: lda_model[x])

        # @TODO Wordcloud: display for report and store it in first run
        # spotify_df['track_lyrics_processed'] = spotify_df['track_lyrics'].str.strip().str.replace('\d+', '').map(lambda x: re.sub('[,\.!?]', '', x)).map(lambda x: x.lower())
        # stop_words = stopwords.words('english')
        # stopwords_wc = set(STOPWORDS)
        # stopwords_wc.update(["and", "uh", "hi", "new", "next"])
        # stop_words.extend(stopwords_wc)
        long_string = ','.join(list(spotify_df['track_lyrics_processed'].explode()))
        # ','.join(list(spotify_df['track_genres'].explode().unique()))
        wordcloud = WordCloud(stopwords=stop_words, background_color="white", max_words=500, contour_width=3, contour_color='steelblue').generate(long_string)
        # print(list(wordcloud.words_.items())[:10])
        wordcloud.to_file("resources/pictures/lyrics_word_cloud.png")
        # @TODO Store once and comment this section
        spotify_df.drop('track_lyrics_processed_list', axis=1)
        spotify_df.drop('Bow_Vector', axis=1)

        spotify_df['track_lyrics']=spotify_df['track_lyrics'].str.replace('\n', ' ').str.replace('\s+', ' ', regex=True)
        spotify_df['track_lyrics_processed']=spotify_df['track_lyrics_processed'].str.replace('\n', ' ').str.replace('\s+', ' ', regex=True)
        # spotify_df['track_lyrics']=spotify_df['track_lyrics'].str.replace('\n', ' ').str.replace('\s+', ' ', regex=True)
    #     track_lyrics|track_lyrics_sentiment|track_lyrics_processed|track_lyrics_processed_list|Bow_Vector|lyrics_topic_distribution

    @staticmethod
    def sentiment(line):
        return SentimentIntensityAnalyzer().polarity_scores(line)
    @staticmethod
    def sentiment_lyrics(row_dict):
        row_dict['artists'] = MusicModule.lyric_url(row_dict['artist_names'])  # .apply(MusicModule.lyric_url)
        row_dict['track_names'] = MusicModule.lyric_url(row_dict['track_name'])  # .apply(MusicModule.lyric_url)
        base_url = 'https://genius.com/'
        end_url = 'lyrics'
        row_dict['artists_track'] = base_url+row_dict['artists']+'-'+row_dict['track_names']+'-'+end_url
        lyrics = []
        new_url = MusicModule.is_valid_link(row_dict['artists_track'])
        time.sleep(30)
        response = requests.get(new_url)
        if response.status_code == 200:
            content = BeautifulSoup(response.text, 'html.parser')
            for val in content.find_all("span", class_="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw"):
                lyrics.append(val.text)
            track_lyrics = '\n'.join(lyrics)
            row_dict['track_lyrics'] = track_lyrics
            row_dict['track_lyrics_sentiment'] = MusicModule.sentiment(track_lyrics)
        else:
            print("Invalid url", new_url)
            row_dict['track_lyrics'] = np.NAN
            row_dict['track_lyrics_sentiment'] = np.NAN


    @staticmethod
    def lyrics(input_df):
        # input_df = pd.read_orc('/Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/code/output/spotify.orc')
        # print(input_df[['artist_names','track_name']].head(20))
        input_df['artists'] = input_df['artist_names'].apply(MusicModule.lyric_url)
        input_df['track_names'] = input_df['track_name'].apply(MusicModule.lyric_url)
        input_df['base_url'] = 'https://genius.com/'
        input_df['end_url'] = 'lyrics'
        input_df['artists_track'] = input_df['base_url'].str.cat(
            input_df['artists'].str.cat(input_df['track_names'], sep='-')).str.cat(input_df['end_url'], sep='-')

        pd.options.display.max_colwidth = 100
        pd.options.display.max_rows = 999
        # for i in [input_df[['artist_names','artists','track_names','track_name','artists_track']]]:
        #     print(i)

        # print(input_df[['track_names','track_name']].head(20))
        # print(input_df[['artist_names', 'artists', 'track_names', 'track_name', 'artists_track']].head(3))

        urls = input_df['artists_track']
        track_lyrics = {}
        for url in urls:
            lyrics = []
            new_url = MusicModule.is_valid_link(url)
            response = requests.get(new_url)
            if response.status_code == 200:
                content = BeautifulSoup(response.text, 'html.parser')
                for val in content.find_all("span", class_="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw"):
                    lyrics.append(val.text)
                track_lyrics[url] = ' '.join(lyrics)

            else:
                print("Invalid url", url)
                track_lyrics[url] = url

        return track_lyrics

    @staticmethod
    def join_lyrics_songs():
        # print("************************* ", MusicModule.ACCESS_TOKEN, " *************************")
        current_date = datetime.now().strftime("%Y%m%d")
        file_path = Path(f"resources/datasets/music_{current_date}.csv")

        if not file_path.is_file():
            spotify_df = MusicModule.spotify()
            MusicModule.lda_lyrics(spotify_df)
            spotify_df.to_csv(file_path, sep='|', header='true', index=False)
            # spotify_df.write.option("sep", "|").option("header","true").csv(file_path)
            return spotify_df
        else:
            return pd.read_csv(file_path, sep='|', header='infer', skipinitialspace=True)

        # print(spotify_df[['track_id', 'track_danceability', 'track_genres', 'track_lyrics_sentiment', 'lyrics_topic_distribution']].head(10))
        # print(spotify_df.columns)

    @staticmethod
    def music_recommendation(qoute):
        spotify_df = MusicModule.join_lyrics_songs()
        # print(spotify_df.head(2))
        # print(qoute)



MusicModule.music_recommendation("Two young guys with shaggy hair look at their hands while hanging out in the yard .")
# @todo similarity test, LDA,,sentiment, features, popularity

# Pygame package -> for music recommendation

# curl --request GET --url 'https://api.spotify.com/v1/audio-features?ids=5Z2MiIZ5I3jJvvmeWMLbOQ' --header 'Authorization: Bearer BQBU2XLhIXmzR_Yb7RvDwbHdKHLonU-yngPXKSPRJk4UG5I5rfyQ5Geh3TDsVLNYKWOWikDZoYbfq-pVKFVJpeTTwnUadjy9AhApvJsZ4Eg6RIJO7Ys'
# curl --request GET --url https://api.spotify.com/v1/artists/7tYKF4w9nC0nq9CsPZTHyP --header 'Authorization: Bearer BQDqs7dUPGuRGzrpqVCUpBcSW6UmRVpYXvmSz-yX6RpmPl3F4OKuJyNQA2-dHdlmoowiHaySKJsQMKAqgsdR-3Q259te6S7lkIui5H9W9u3f9b0LSns'
# curl --request GET --url https://api.spotify.com/v1/artists/0TnOYISbd1XYRBk9myaseg --header 'Authorization: Bearer BQDqs7dUPGuRGzrpqVCUpBcSW6UmRVpYXvmSz-yX6RpmPl3F4OKuJyNQA2-dHdlmoowiHaySKJsQMKAqgsdR-3Q259te6S7lkIui5H9W9u3f9b0LSns'


# @TODO
# DONE > include features and genres into spotify data
# > join lyrics to spotify data + sentiment on lyrics + popularity + features [sentiment]
# > artist genre -> pull song genra
# > classify songs and rank
# > recommend song

# print(','.join(list(spotify_df['track_genres'].explode().unique())))
# print(lyrics_topic)

# Music Recommendation
# This section aims to provide personalized song recommendations to users through a multi-step process. The key steps include extracting songs, scraping lyrics, analyzing lyrics sentiment, generating captions, detecting genres, comparing songs, and ultimately recommending songs tailored to the user's preferences.
# Song Extraction: We employ HTTP API requests to gather details about trendy songs, such as playlist URL, popularity, and artist information from Spotify. This playlist contains songs from different genres currently trending among listeners.
# Lyrics Scraping: We employ web scraping techniques to retrieve lyrics for all the songs from the genius.com webpage. Reformatting the metadata collected from the playlist, we pass it as a URL query to collect lyrics for all songs gathered from Spotify.
# Lyrics Sentiment Analysis: We are conducting sentiment analysis using natural language processing techniques on all songs to understand whether the lyrics are positive, negative, or neutral. Additionally, we use the Spotify API to obtain song features like loudness, acoustics, danceability, liveliness, and energy. Combining these features helps us understand the actual sentiment and popularity of each song.
# Genre Detection: Utilizing natural language processing, specifically LDA, we identify keywords from the songs. Additionally, we take into account the features associated with the tracks and the artists' specialized genres. Rule-based methods are then applied to imply the song genre.
# Song Comparison: We are implementing an algorithm, to compare all songs based on computed features, classify, and rank them into multiple categories for a better recommendation model.
# Song Recommendations: Based on the classified song groups and analysis of the generated captions, this recommendation model would return the most relevant songs for the incoming image.
#
# This block under the music recommendation module is executed post the captions generation. We are considering the captions as the primary input component for our model to analyze song lyrics and genre and recommend a song track suitable for the caption.
# Sentiment Analysis: We are capturing the sentiment of the caption and the sentiment of all song lyrics using the SentimentIntensityAnalyzer, this returns if the parameter passed through the analyser is positive, negative or neutral. With this information we can understand the tone and classify them accordingly.
# Song Classifier: Based on the tone from sentiment analysis of the tracks, its artist genres and features collected from Spotify API. We classify the songs into different genres on a rule-based method. This classification would only depict major categories which we can use for selecting tracks. With this approach we are reorganizing the existing genres based on these different features and consolidate them into specific groups which can be deduced easily from the caption.
# Analyzing Lyrics: We use the Latent Dirichlet Allocation model to gather the topic and relevant keyword in our song lyrics. The main goal of this is to identify the essence of the song from words.
# Ranking tracks: In addition to classifying songs into separate groups we are also ranking them, so we can display only the most relevant track for a caption. We are implementing this by reviewing the caption tokens and their synonyms, comparing them with the lyric keywords. By analyzing and comparing the keywords, we can reorder the tracks inside the group based on its popularity.
# Recommendation Model: From the above analysis we can correlate the captions with the classified track group, and prioritize them based on the feature relevance. Thus returning songs which are suitable for the caption.
#
# Sentiment Analysis using SentimentIntensityAnalyzer, Natural Language Toolkit (nltk) library in Python : It is the process of determining the sentiment or emotional tone expressed in a piece of text.
    # Intensity Scores: The SentimentIntensityAnalyzer assigns intensity scores to the text based on the presence of positive, negative, and neutral words, as well as the overall polarity of the text.
    # Polarity Score: The tool calculates a polarity score for the given text, which indicates the overall sentiment as positive, negative, or neutral. The polarity score is a continuous value between -1 (most negative) and 1 (most positive).
    # Compound Score: The compound score is a single metric that represents the overall sentiment of the text. It is a combination of the positive, negative, and neutral scores, normalized to a range between -1 and 1. A positive compound score suggests a positive sentiment, while a negative score suggests a negative sentiment.
    # Use of Lexicons: The SentimentIntensityAnalyzer relies on pre-built lexicons or dictionaries that contain lists of words associated with different sentiments. These lexicons are used to match words in the input text and assign sentiment scores.
# Topic Modeling using Latent Dirichlet Allocation (LDA), gensim library in python: LDA assumes that documents are mixtures of topics and that each word in a document is attributable to one of the document's topics.
    # Initialization: LDA starts by assuming a fixed number of topics for the entire corpus and a distribution of topics for each document. The number of topics is a hyperparameter that needs to be set prior to training.
    # Assigning Topics: For each document in the corpus, LDA assigns a distribution of topics based on the words in the document. Each word in the document is then assigned a specific topic based on a probability distribution.
    # Generative Process: LDA assumes a generative process for creating documents, For each document, choose a distribution of topics. For each word in the document, Choose a topic from the distribution of topics or Choose a word from the topic's distribution of words.
    # Parameter Estimation: The goal of training an LDA model is to estimate the parameters (topic distributions for documents, word distributions for topics) that best explain the observed documents.
    # Dirichlet Priors: LDA uses Dirichlet priors to model the distribution of topics and words. The Dirichlet distribution is a family of continuous multivariate probability distributions.
    # Inference: Inference in LDA involves estimating the posterior distribution of topics for each document and the distribution of words for each topic. This is typically done using techniques like variational inference or Gibbs sampling.
    # The output of LDA includes the identified topics and the words associated with each topic. Each document is represented as a mixture of topics, and each topic is represented as a distribution of words.
# Similarity Scoring Model using TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer and cosine similarity, sklearn library in python: To find similar documents based on textual content
    # TF-IDF Vectorization: The TfidfVectorizer from scikit-learn is used to convert the preprocessed text data into numerical vectors using the TF-IDF representation. TF-IDF reflects the importance of a word in a document relative to its importance in the entire dataset.
    # Cosine Similarity Calculation: The cosine_similarity function from scikit-learn computes the cosine similarity between documents based on their TF-IDF vectors. Cosine similarity measures the cosine of the angle between two non-zero vectors, providing a similarity score between 0 and 1.
    # Similarity Scoring Function: The get_similarity_scores function takes a query text and calculates the cosine similarity scores between the query and all documents in the dataset. It returns a dictionary where the keys are document texts, and the values are their similarity scores with the query.



# --------------#--------------#--------------#--------------#--------------
# playlist_name  playlist_followers \ playlist_uri             playlist_id \ total_tracks      track_added_time                artist_names \ artist_id \ album_available_market \ album_name album_type album_release_date \ album_date_precision  album_tracks \ track_available_market \ track_duration_ms                                     track_link_spotify \ track_name  track_popularity \ track_preview_url
# 0  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:20:35Z                       [SZA] 0                          [7tYKF4w9nC0nq9CsPZTHyP] 0  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 0                                      SOS      album         2022-12-08 0                  day            23 0  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 0             153946  https://open.spotify.com/track/1Qrg8KqiBpW07V7PNxwwwL 0          Kill Bill                92 0  https://p.scdn.co/mp3-preview/4bd2dc84016f3743add7eea8b988407b1b900672?cid=9d7429fddef847139c8ae837b6bcdd92
# 1  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:20:45Z                      [RAYE] 1                          [5KKpBU5eC2tJDzf0wmlRp2] 1                                                                                                                                                                                                                                                                                                                                                                                                                     [] 1          Escapism. / The Thrill Is Gone.      album         2022-10-12 1                  day             4 1                                                                                                                                                                                                                                                                                                                                                                                                                     [] 1             272373  https://open.spotify.com/track/5Z2MiIZ5I3jJvvmeWMLbOQ 1          Escapism.                24 1                                                                                                         None
# 2  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:21:16Z              [Taylor Swift] 2                          [06HL4z0CvFAxyc27GXpf02] 2  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 2                                Midnights      album         2022-10-21 2                  day            13 2  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 2             200690  https://open.spotify.com/track/0V3wPSX9ygBnCm8psDIegu 2          Anti-Hero                93 2                                                                                                         None
# 3  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:21:29Z                      [d4vd] 3                          [5y8tKLUfMvliMe8IKamR32] 3                                                                                                                                                                                                                                                                                                                                                                                                                     [] 3                             Here With Me      album         2022-09-22 3                  day             1 3                                                                                                                                                                                                                                                                                                                                                                                                                     [] 3             242484  https://open.spotify.com/track/78Sw5GDo6AlGwTwanjXbGh 3       Here With Me                39 3                                                                                                         None
# 4  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:21:35Z                      [JVKE] 4                          [164Uj4eKjl6zTBKfJLFKKK] 4  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, BS, ...] 4  this is what ____ feels like (Vol. 1-4)      album         2022-09-23 4                  day            12 4  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, BS, ...] 4             209259  https://open.spotify.com/track/5odlY52u43F5BjByhxg7wg 4        golden hour                86 4  https://p.scdn.co/mp3-preview/bcc17f30841d6fbf3cd7954c3e3cf669f11b6a21?cid=9d7429fddef847139c8ae837b6bcdd92
# 5  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:21:43Z  [David Guetta, Bebe Rexha] 5  [1Cs0zKBU1kc0i8ypK3B9ai, 64M6ah0SkkRsnPGtGiRAbb] 5  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 5                          I'm Good (Blue)      album         2022-08-26 5                  day             2 5  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 5             175238  https://open.spotify.com/track/4uUG5RXrOk84mYEfFvj3cK 5    I'm Good (Blue)                92 5  https://p.scdn.co/mp3-preview/c1de960c1a98f7ab652331e5223c50baba75c460?cid=9d7429fddef847139c8ae837b6bcdd92
# 6  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:22:17Z                       [SZA] 6                          [7tYKF4w9nC0nq9CsPZTHyP] 6  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, ...] 6                                      SOS      album         2022-12-09 6                  day            23 6  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, BY, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, ...] 6             180853  https://open.spotify.com/track/5Y35SjAfXjjG0sFQ3KOxmm 6     Nobody Gets Me                84 6  https://p.scdn.co/mp3-preview/36cfe8fbfb78aa38ca3b222c4b9fc88cda992841?cid=9d7429fddef847139c8ae837b6bcdd92
# 7  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:22:24Z            [PinkPantheress] 7                          [78rUTD7y6Cy67W1RVzYs7t] 7  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 7                             Boy's a liar      album         2022-11-30 7                  day             2 7  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 7             131253  https://open.spotify.com/track/3NanY0K4okhIQzL33U5Ad8 7       Boy's a Liar                75 7  https://p.scdn.co/mp3-preview/221777a319603445900b65db0ceaccb2624b0df3?cid=9d7429fddef847139c8ae837b6bcdd92
# 8  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:23:17Z          [Drake, 21 Savage] 8  [3TVXtAsR1Inumwj472S9r4, 1URnnhqYAYcrqrcwql10ft] 8  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 8                                 Her Loss      album         2022-11-04 8                  day            16 8  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, SE, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, ...] 8             239359  https://open.spotify.com/track/1bDbXMyjaUIooNwFE9wn0N 8          Rich Flex                87 8                                                                                                         None
# 9  Trendy songs 2023                9190   spotify:playlist:6QGk7b8naF3ZPljgPtWMAD  6QGk7b8naF3ZPljgPtWMAD            248  2023-01-01T13:23:26Z                      [d4vd] 9                          [5y8tKLUfMvliMe8IKamR32] 9  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, BS, ...] 9                        Romantic Homicide      album         2022-07-20 9                  day             1 9  [AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, CY, CZ, DK, DO, DE, EC, EE, SV, FI, FR, GR, GT, HN, HK, HU, IS, IE, IT, LV, LT, LU, MY, MT, MX, NL, NZ, NI, NO, PA, PY, PE, PH, PL, PT, SG, SK, ES, CH, TW, TR, UY, US, GB, AD, LI, MC, ID, JP, TH, VN, RO, IL, ZA, SA, AE, BH, QA, OM, KW, EG, MA, DZ, TN, LB, JO, PS, IN, KZ, MD, UA, AL, BA, HR, ME, MK, RS, SI, KR, BD, PK, LK, GH, KE, NG, TZ, UG, AG, AM, BS, ...] 9             132630  https://open.spotify.com/track/1xK59OXxi2TAAAbmZK0kBL 9  Romantic Homicide                91 9                                                                                                         None

# Bearer key : BQBOTNBR2zgPfb5e2C7e-p5yGqNuitsaHX5MfEiz9jP9ZF6bG7jzGDi7dzFkFPx8K66J3FGN_Be4NLSkxnREQHl4J9SxfTx8f_cjfDTZ_99QtRI_Sn8
# get audio features
#curl --request GET --url https://api.spotify.com/v1/audio-features/11dFghVXANMlKmJXsNCbNl --header 'Authorization: Bearer BQBOTNBR2zgPfb5e2C7e-p5yGqNuitsaHX5MfEiz9jP9ZF6bG7jzGDi7dzFkFPx8K66J3FGN_Be4NLSkxnREQHl4J9SxfTx8f_cjfDTZ_99QtRI_Sn8'

# Get Available Genre Seeds
# curl --request GET --url https://api.spotify.com/v1/recommendations/available-genre-seeds --header 'Authorization: Bearer BQBOTNBR2zgPfb5e2C7e-p5yGqNuitsaHX5MfEiz9jP9ZF6bG7jzGDi7dzFkFPx8K66J3FGN_Be4NLSkxnREQHl4J9SxfTx8f_cjfDTZ_99QtRI_Sn8'
# "genres" : \
#     [ "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal", "bluegrass",
#       "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop", "chicago-house", "children",
#       "chill", "classical", "club", "comedy", "country", "dance", "dancehall", "death-metal",
#       "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep",
#       "edm", "electro", "electronic", "emo", "folk", "forro", "french", "funk", "garage",
#       "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar", "happy",
#       "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk", "house",
#       "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock",
#       "jazz", "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore",
#       "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode", "party", "philippines-opm",
#       "piano", "pop", "pop-film", "post-dubstep", "power-pop", "progressive-house", "psych-rock", "punk",
#       "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", "road-trip", "rock", "rock-n-roll",
#       "rockabilly", "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter",
#       "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish",
#       "synth-pop", "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music" ]

# recommendations
# https://developer.spotify.com/documentation/web-api/reference/get-recommendations
# curl --request GET --url 'https://api.spotify.com/v1/recommendations?limit=2&seed_genres=classical%2Ccountry' --header 'Authorization: Bearer BQBOTNBR2zgPfb5e2C7e-p5yGqNuitsaHX5MfEiz9jP9ZF6bG7jzGDi7dzFkFPx8K66J3FGN_Be4NLSkxnREQHl4J9SxfTx8f_cjfDTZ_99QtRI_Sn8'
# curl --request GET --url 'https://api.spotify.com/v1/recommendations?limit=1&seed_genres=children&max_popularity=100' --header 'Authorization: Bearer BQBOTNBR2zgPfb5e2C7e-p5yGqNuitsaHX5MfEiz9jP9ZF6bG7jzGDi7dzFkFPx8K66J3FGN_Be4NLSkxnREQHl4J9SxfTx8f_cjfDTZ_99QtRI_Sn8'

# def intra_qoutes(link):
#
#
#     return []
#
# x={
#     "intra_qoutes": link,
#     "writer_qoutes": link
#
# }
# for i in x.keys():
#     [q1,q2,q3]=find(function(i)) [link]


