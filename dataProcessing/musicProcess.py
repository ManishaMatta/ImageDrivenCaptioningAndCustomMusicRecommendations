import os
import requests
import json
import subprocess
import pandas as pd
from builtins import *
from datetime import datetime
from IPython.display import IFrame
from bs4 import BeautifulSoup
from unidecode import unidecode
# import textProcess


# https://nitratine.net/blog/post/finding-emotion-in-music-with-python/
# https://towardsdatascience.com/predicting-my-mood-using-my-spotify-data-2e898add122a


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
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
        return pd.DataFrame(rows)

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
        invalid_url = []  # delete this
        for url in urls:
            lyrics = []
            new_url = MusicModule.is_valid_link(url)
            response = requests.get(new_url)
            if response.status_code == 200:
                content = BeautifulSoup(response.text, 'html.parser')
                for val in content.find_all("span", class_="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw"):
                    lyrics.append(val.text)
                track_lyrics[url] = '\n'.join(lyrics)

            else:
                print("Invalid url", url)
                track_lyrics[url] = url

        return track_lyrics

    @staticmethod
    def join_lyrics_songs():
        # print("************************* ", MusicModule.ACCESS_TOKEN, " *************************")
        spotify_df = MusicModule.spotify()
        print(spotify_df.head(10))
        # track_lyrics = MusicModule.lyrics(spotify_df)
        # track_lyrics.keys()
        # for url in list(track_lyrics.keys())[:10]:
        #     print(textProcess.sentiment(track_lyrics[url]))


MusicModule.join_lyrics_songs()


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
