from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from pathlib import Path
import json
import time
import string
import re
import time
import csv
from dotenv import load_dotenv
import os

# Get secrets from .env file
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

token_cache_path = './dist/token.json'

access_token_url = 'https://www.reddit.com/api/v1/access_token'


def cache_token(token, token_cache_path):
    Path('./dist').mkdir(parents=True, exist_ok=True)
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

oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
token = {}
comment_table = []
cached_token = read_token(token_cache_path)
epoch_time = int(time.time())

print(epoch_time, cached_token['expires_at'])

if (epoch_time >= cached_token['expires_at']):
    print('old token')
    token = oauth.fetch_token(token_url=access_token_url,
            username=username, password=password, client_id=client_id,
            client_secret=client_secret,
            header={'User-agent': 'my-app 0.1'})
    # Looks like:
    # {'access_token': '221585764340-xvPGJ2uoytwpps1btV04z92FriYtkA',
    # 'token_type': 'bearer', 'expires_in': 86400, 'scope': ['*'],
    # 'expires_at': 1680732511.693944}
    cache_token(token, token_cache_path)
else:
    print('good token')
    token = cached_token
    
def strip_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def remove_escaped_quotes(s):
    return re.sub(r'\\\".*?\\\"', '', s)

def remove_escaped_newlines(s):
    return s.replace('\n', ' ')


def get_comments_for_post(post_id):
    client = OAuth2Session(client_id, token=token)
    time.sleep(1)
    url = f'https://oauth.reddit.com/r/worldnews/comments/{post_id}?threaded=false&sort=top'
    r = client.get(url, headers = {'User-agent': 'my-app 0.1'})
    # print(dir(r))
    # print(r.status_code, r.reason)
    if (r.status_code == 200):
        post_id = r.json()[0]['data']['children'][0]['data']['name']
        comments = r.json()[1]['data']['children']
        all_comments = {}
        for comment in comments:
            if comment['kind'] == 't1':
                raw_body = comment['data']['body']
                body = remove_escaped_quotes(raw_body)
                body = strip_punctuation(body)
                body = remove_escaped_quotes(body)
                body = remove_escaped_newlines(body)
                all_comments[comment['data']['name']] = body
        for comment in comments[:20]:
            if comment['data']['parent_id'] != post_id and comment['kind'] == 't1':
                response = all_comments[comment['data']['name']]
                if (len(response) < 256):
                    original = all_comments[ comment['data']['parent_id'] ]
                    row = [original, response]
                    comment_table.append(row)
                   

def get_top_posts():
    # API Doc: https://www.reddit.com/dev/api/#GET_{sort}
    url = 'https://oauth.reddit.com/r/worldnews/top/.json?count=2'
    client = OAuth2Session(client_id, token=token)
    r = client.get(url, headers = {'User-agent': 'my-app 0.1'})
    if (r.status_code == 200):
        for post in r.json()['data']['children']:
            id = post['data']['id']
            get_comments_for_post(id)
        print(comment_table)
        with open('dist/comments.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Prompt', 'Response'])
            writer.writerows(comment_table)


get_top_posts()


