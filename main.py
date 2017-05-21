import requests, json, sqlite3
from pprint import pprint


class Playlist:
    def __init__(self, name: str, id: str, owner: str):
        self.name = name
        self.id = id
        self.owner = owner
    def __str__(self):
        return self.id + " - " + self.owner + " - " + self.name

class User:
    def __init__(self, display_name: str, id: str):
        self.display_name = display_name
        self.id = id
    def __str__(self):
        return self.id + " - " + self.display_name

class Fetcher:
    def __init__(self):
        self.pages = {
            'get_user_playlists': "https://api.spotify.com/v1/users/%s/playlists",
            'get_current_user': "https://api.spotify.com/v1/me",
            'get_playlist_tracks': "https://api.spotify.com/v1/users/%s/playlists/%s/tracks",
            'get_tracks_features': "https://api.spotify.com/v1/audio-features"
        }
        self.oauth_token = self.get_oauth()
        self.headers = {'Authorization': 'Bearer '+self.oauth_token}

    def get_oauth(self) -> str:
        with open('oauth.txt', 'r') as f:
            return f.read()

    def fetch_page(self, url: str) -> str:
        with requests.Session() as session:
            response = session.get(url, headers=self.headers)
        return str(response.text)

    def fetch_json(self, url: str) -> dict:
        return json.loads(self.fetch_page(url))

    def fetch_api(self, api_call: str, params: list=[], optionals: dict={}) -> dict:
        url = self.pages[api_call] % tuple(params)
        if optionals:
            url += "?"
            for key, value in optionals.items():
                url += key+"="+str(value)+"&"
        return self.fetch_json(url)

class SqliteExport:
    def __init__(self, fname: str):
        self.con = sqlite3.connect(fname)
        self.cur = self.con.cursor()

    def delete(self):
        self.con.execute('DELETE FROM piosenki;')
        self.con.commit()

    def close(self):
        self.con.commit()
        self.con.close()

    def export(self, d: list):
        dict_model = [
            'id', 'title', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
            'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms'
        ]

        #self.cur.execute(  # uncomment on first launch
        #    "CREATE TABLE piosenki ("+', '.join(dict_model)+");")
        query = "INSERT INTO piosenki ("+', '.join(dict_model)+") VALUES ("+', '.join(['?']*len(dict_model))+");"
        self.cur.executemany(query, d)

class Parser:
    def p_playlists(self, json_dict: dict) -> list:
        playlists = []
        for p in json_dict['items']:
            playlists.append(Playlist(p['name'], p['id'], p['owner']['id']))
        return playlists
    def p_user(self, json_dict: dict) -> object:
        return User(json_dict['display_name'], json_dict['id'])
    def ids_from_playlist(self, json_dict: dict) -> dict:
        ids = {}
        for song in json_dict['items']:
            ids[song['track']['id']] = song['track']['album']['artists'][0]['name']+" - "+song['track']['name']
        return ids

prsr = Parser()
ftch = Fetcher()


"""
0nctmSV1j6bc6CJBpOCEVz - 1191584733 - Dopracowane perełki
7sP34VAMpoB9IDY6Hw1C4J - 1191584733 - Imprezowe
6P7FpSCVS0788uHO2QaasY - 1191584733 - Dobra muzyka - po prostu.
3NvqgfDX4gnjo8MHUwKuSP - 1191584733 - Rock, ew. metal
5hU005cVJ6YxukoH0aWCyK - 1191584733 - Polskie, głównie pop
0ASbkhRRPIcEMc6eMFoyQT - 1191584733 - House/trance/itp
4jxLNcEcXo3pAyGzMxQYV8 - 1191584733 - Rap
"""
user_id = prsr.p_user(ftch.fetch_api('get_current_user')).id
plays = prsr.p_playlists(ftch.fetch_api('get_user_playlists', [user_id]))
for p in plays:
    print(p)
ids_list_one = prsr.ids_from_playlist(
    ftch.fetch_api('get_playlist_tracks',
                   [user_id, '4jxLNcEcXo3pAyGzMxQYV8'],
                   {'offset': 0}))
ids_list_two = prsr.ids_from_playlist(
    ftch.fetch_api('get_playlist_tracks',
                   [user_id, '4jxLNcEcXo3pAyGzMxQYV8'],
                   {'offset': 100}))

ids_list = {**ids_list_one, **ids_list_two}
cool_ids = ','.join(list(ids_list.keys())[:100])
cool_ids2 = ','.join(list(ids_list.keys())[100:-1])
csv_list = [[
    'id', 'title', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms'
]]
for x in (cool_ids, cool_ids2):
    xD = ftch.fetch_api('get_tracks_features', optionals={'ids':x})
    for i in xD['audio_features']:
        csv_list.append([
            i['id'], ids_list[i['id']], i['danceability'], i['energy'], i['key'], i['loudness'], i['mode'],
            i['speechiness'], i['acousticness'], i['instrumentalness'], i['liveness'], i['valence'],
            i['tempo'], i['duration_ms']
        ])

sq = SqliteExport('piosenki.db')
sq.delete()
sq.export(csv_list[1:])
sq.close()
print(csv_list)
