# Reddit Comment Downloader
Client for downloading comments from Reddit's API. It caches the Reddit API's JSON responses locally for efficiency.

## Instructions
Run `python download_commments.py`. The output will be in `dist/`. The Reddit API responses are cached in `cache/`.

# Setup

## Python and Dependencies

Install the version of Python in `.python-version`.

Run `pip install -r requirements.txt` to install dependencies.

## Reddit Setup
You need to create your own app on Reddit before using this. Go here to do that: https://www.reddit.com/prefs/apps

## Developer Setup

### Secrets
Create a `.env` file at the root of this repo. It should have this format:

```
CLIENT_ID=your_app_client_id
CLIENT_SECRET=your_app_secret
USERNAME=your_reddit_username
PASSWORD=your_reddit_password
```

The `CLIENT_ID` is the alphanumeric string under your app in Reddit. The secret is available when you first create the app, and when you go to edit it.

# Appendix

Useful doc on auth for scripts: https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example

## Example Reddit Oauth - raw

```
curl -X POST -d 'grant_type=password&username=USERNAME&password=PASSWORD' --user 'CLIENT_ID' https://www.reddit.com/api/v1/access_token
```

That yields something like
```
{"access_token": "221585764340-5sjEGRZJReAxwR6Ai2ZiWE6mR1-jdQ", "token_type": "bearer", "expires_in": 86400, "scope": "*"}
```

Use that token as the bearer one in subsequent calls to the oauth.reddit.com domain:

```
curl -H "Authorization: bearer 221585764340-5sjEGRZJReAxwR6Ai2ZiWE6mR1-jdQ" -A "CUSTOM_CLIENT_NAME" https://oauth.reddit.com/api/v1/me
```

`CUSTOM_CLIENT_NAME` needs to be something that is fairly unique. Something like 'My Custom Client 1.0' will be OK.

## Get top 20 posts
Doesn't even need auth when used with the www.reddit.com domain:

```
curl -X GET -L https://www.reddit.com/r/worldnews/top/.json?count=20
```

## Get comments for a post

```
curl -H "Authorization: bearer OAUTH_TOKEN" -A "CUSTOM_CLIENT_NAME" -X GET -L https://oauth.reddit.com/r/worldnews/comments/12agp1u
```

Docs: https://www.reddit.com/dev/api#GET_comments_{article}


