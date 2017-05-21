import requests, json
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
            'get_current_user': "https://api.spotify.com/v1/me"
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

class Parser:
    def p_playlists(self, json_dict: dict) -> list:
        playlists = []
        for p in json_dict['items']:
            playlists.append(Playlist(p['name'], p['id'], p['owner']['id']))
        return playlists
    def p_user(self, json_dict: dict) -> object:
        return User(json_dict['display_name'], json_dict['id'])

prsr = Parser()
ftch = Fetcher()

user_id = prsr.p_user(ftch.fetch_api('get_current_user')).id
plays = prsr.p_playlists(ftch.fetch_api('get_user_playlists', [user_id]))
for p in plays:
    print(p)