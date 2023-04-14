from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from pathlib import Path
from dotenv import load_dotenv
import os
import time
import json

user_agent = 'my-app 0.1'

# Get secrets from .env file
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

token_cache_path = './cache/token.json'

access_token_url = 'https://www.reddit.com/api/v1/access_token'

def cache_token(token, token_cache_path):
    Path('./cache').mkdir(parents=True, exist_ok=True)
    f = open(token_cache_path, 'w')
    f.write(json.dumps(token))
    f.close()

def read_token(token_cache_path):
    try:
        f = open(token_cache_path, 'r')
        data = json.load(f)
        f.close()
        return data
    except:
        return {'expires_at': 0}


def get_token():
    epoch_time = int(time.time())
    cached_token = read_token(token_cache_path)
    if (epoch_time >= cached_token['expires_at']):
        print('Token expired, fetching new OAUTH token')
        oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        token = oauth.fetch_token(token_url=access_token_url,
                username=username, password=password, client_id=client_id,
                client_secret=client_secret,
                headers={'User-agent': 'my-app 0.1'})
        # Looks like:
        # {'access_token': '221585764340-xvPGJ2uoytwpps1btV04z92FriYtkA',
        # 'token_type': 'bearer', 'expires_in': 86400, 'scope': ['*'],
        # 'expires_at': 1680732511.693944}
        cache_token(token, token_cache_path)
    else:
        print('Using cached OAUTH token')
        token = cached_token
    return token

def get_oauth_client():
    token = get_token()
    client = OAuth2Session(client_id, token=token)
    return client

# Load a given Reddit URL from local cache, if present, or request it and cache
# it for future.
def get_and_cache(url, cache_path):
    cache_file = f'cache/{cache_path}.json'
    if os.path.isfile(cache_file):
        print(f'Found cached file {cache_file}')
        f = open(cache_file)
        data = json.load(f)
        response_code = 304
        return response_code,data
    else:
        print(f'Requesting URL {url}')
        client = get_oauth_client()
        # Delay needed to stay within Reddit's API limiting
        time.sleep(1)
        resp = client.get(url, headers = {'User-agent': user_agent})
        data = None
        if resp.status_code == 200:
            data = resp.json()
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write(json.dumps(resp.json(), indent=2))
                f.close()
        return resp.status_code, data






