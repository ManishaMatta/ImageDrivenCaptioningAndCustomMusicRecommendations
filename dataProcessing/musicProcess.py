import os
import requests
import json
import subprocess
import pandas as pd
from builtins import *
from datetime import datetime
from IPython.display import IFrame
from bs4 import BeautifulSoup


# from unidecode import unidecode

# https://nitratine.net/blog/post/finding-emotion-in-music-with-python/
# https://towardsdatascience.com/predicting-my-mood-using-my-spotify-data-2e898add122a

class MusicModule:
    ACCESS_TOKEN = ''
    TOKEN_TIME = ''

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
        if int(len(lyric_url)) == 0:
            print("*****")
        else:
            pass
        if (type(lyric_url) is str):
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

    # --------------#--------------#--------------#--------------#--------------
    @staticmethod
    def spotify():
        MusicModule.generate_bearer_token()
        if (MusicModule.validate_access_token):
            url = "https://api.spotify.com/v1/playlists/6QGk7b8naF3ZPljgPtWMAD"
        else:
            MusicModule.generate_bearer_token()

        data = json.loads(MusicModule.sportify_trendy_track(url))
        base_row_dict = {}
        data_list = [data]
        base_row_dict['playlist_name'] = data['name']
        base_row_dict['playlist_followers'] = data['followers']['total']
        base_row_dict['playlist_uri'] = data['uri']
        base_row_dict['playlist_id'] = data['id']
        base_row_dict['total_tracks'] = data['tracks']['total']
        page = data['tracks']['next']
        while (str(page) != 'None'):
            data = json.loads(MusicModule.sportify_trendy_track(page))
            data_list.append(data)
            page = data['next']

        rows = []
        for i in data_list:
            if (('tracks' in i.keys()) and ('items' not in i.keys())):
                for j in i['tracks']['items']:
                    row_dict = base_row_dict.copy()
                    row_dict['track_added_time'] = j['added_at']
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
                    rows.append(row_dict)
            else:
                for j in i['items']:
                    row_dict = base_row_dict.copy()
                    row_dict['track_added_time'] = j['added_at']
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
                    rows.append(row_dict)

        pd.set_option('display.max_colwidth', None)
        spotify_df = pd.DataFrame(rows)
        print(spotify_df.head(10))
        return (spotify_df)

    @staticmethod
    def lyrics():
        input_df = pd.read_orc('/Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/code/output/spotify.orc')
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
        print(input_df[['artist_names', 'artists', 'track_names', 'track_name', 'artists_track']].head(3))

        urls = input_df['artists_track']
        track_lyrics = {}
        invalid_url = []  # delete this
        for url in urls:
            lyrics = []
            new_url = MusicModule.is_valid_link(url)
            response = requests.get(new_url)
            if (response.status_code == 200):
                content = BeautifulSoup(response.text, 'html.parser')
                for val in content.find_all("span", class_="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw"):
                    lyrics.append(val.text)
                track_lyrics[url] = '\n'.join(lyrics)

            else:
                print("Invalid url", url)
                track_lyrics[url] = url

        return
