import string
import re
import csv
import reddit_client_lib
from pathlib import Path

    
def strip_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def remove_escaped_quotes(s):
    return re.sub(r'\\\".*?\\\"', '', s)

def remove_escaped_newlines(s):
    return s.replace('\n', ' ')


def get_top_responses_for_post(post_id, subreddit):
    print(f'Getting comments for {post_id} in {subreddit}')
    url = f'https://oauth.reddit.com/r/{subreddit}/comments/{post_id}?threaded=false&sort=top'

    cache_path = f'r/{subreddit}/comments/{post_id}'
    status_code,data = reddit_client_lib.get_and_cache(url, cache_path)

    if (status_code in [200, 304]):
        post_id = data[0]['data']['children'][0]['data']['name']
        comments = data[1]['data']['children']
        all_comments = {}
        # Need all comments first since we don't now if a top response will be
        # a reply to a top comment
        for comment in comments:
            if comment['kind'] == 't1':
                raw_body = comment['data']['body']
                body = remove_escaped_quotes(raw_body)
                body = strip_punctuation(body)
                body = remove_escaped_quotes(body)
                body = remove_escaped_newlines(body)
                all_comments[comment['data']['name']] = body
        # Just get the top 20
        comment_table = []
        for comment in comments[:20]:
            if comment['data']['parent_id'] != post_id and comment['kind'] == 't1':
                response = all_comments[comment['data']['name']]
                # For now, just deal with short response comments
                if (len(response) < 256):
                    original = all_comments[ comment['data']['parent_id'] ]
                    row = [original, response]
                    comment_table.append(row)
        return comment_table
                   

def get_top_posts_in(subreddits, num_posts):
    for subreddit in subreddits:
        # API Doc: https://www.reddit.com/dev/api/#GET_{sort}
        url = f'https://oauth.reddit.com/r/{subreddit}/top/.json?limit={num_posts}'
        print(f'Loading top posts from {subreddit}');
        cache_path = f'r/{subreddit}/top'
        status_code,data = reddit_client_lib.get_and_cache(url, cache_path)

        if (status_code in [200, 304]):
            for post in data['data']['children']:
                id = post['data']['id']
                comment_table = get_top_responses_for_post(id, subreddit)
            Path('./dist').mkdir(parents=True, exist_ok=True)
            with open('dist/comments.csv', 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Prompt', 'Response'])
                writer.writerows(comment_table)

subreddits = ['worldnews']
get_top_posts_in(subreddits, 3)


