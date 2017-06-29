import os
import json
import datetime

import jwt

import requests

from flask import Flask, request

from werkzeug.contrib.fixers import ProxyFix

app = Flask('astrochangebot')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Nothing to see here"


def get_jwt():
    """
    Prepares the JSON Web Token (JWT) based on the private key.
    """

    now = datetime.datetime.now()
    expiration_time = now + datetime.timedelta(minutes=9)
    payload = {
        # Issued at time
        'iat': int(now.timestamp()),
        # JWT expiration time (10 minute maximum)
        'exp': int(expiration_time.timestamp()),
        # Integration's GitHub identifier
        'iss': app.integration_id
    }

    return jwt.encode(payload, app.private_key.encode('ascii'), algorithm='RS256')


def request_access_token(installation):

    print(get_jwt())

    headers = {}
    # note, won't work if netrc file is present
    headers['Authorization'] = 'Bearer {0}'.format(get_jwt().decode('ascii'))
    headers['Accept'] = 'application/vnd.github.machine-man-preview+json'

    url = 'https://api.github.com/installations/{0}/access_tokens'.format(installation)

    req = requests.post(url, headers=headers)

    resp = req.json()

    return resp['token']


@app.route("/hook", methods=['POST'])
def hook():

    if request.headers['X-GitHub-Event'] != 'pull_request':
        return "Not a pull_request event"

    data = json.loads(request.data)

    token = request_access_token(data['installation'])

    headers = {}
    headers['Authorization'] = 'token {0}'.format(token)
    headers['Accept'] = 'application/vnd.github.machine-man-preview+json'

    url_review = data['review_comments_url'].replace('comments', 'reviews')

    data = {}
    data['commit_id'] = data['head']['sha']
    data['body'] = 'yay'
    data['event'] = 'APPROVE'

    requests.post(url_review, json=data, headers=headers)

    url_status = data['statuses_url']

    data = {}
    data['state'] = 'error'
    data['description'] = 'see latest review by astrochangebot'
    data['context'] = 'astrochangebot'

    requests.post(url_status, json=data, headers=headers)

    changes_url = data['contents_url'].replace('{+path}', 'CHANGES.rst')

    data = {}
    data['ref'] = data['head']['ref']

    requests.get(changes_url, json=data)
    j = resp.json()

    print(base64.b64decode(j['content']))


    return str(request.data)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
