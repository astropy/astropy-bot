import os
import json

from flask import Flask, redirect, url_for, request

from github import Github
from github.GithubException import GithubException

from werkzeug.contrib.fixers import ProxyFix

app = Flask('astrochangebot')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Nothing to see here"


@app.route("/hook", methods=['POST'])
def hook():

    if request.headers['X-GitHub-Event'] != 'pull_request':
        return "Not a pull_request event"

    gh = Github(client_id=app.config["GITHUB_OAUTH_CLIENT_ID"],
                client_secret=app.config["GITHUB_OAUTH_CLIENT_SECRET"])

    data = json.loads(request.data)

    repo = gh.get_repo(data['repository']['full_name'])

    pr = repo.get_pull(int(data['number']))

    commit = repo.get_commit(pr.head.sha)

    # can also set target_url
    commit.create_status('error',
                         description='Your changelog sucks',
                         context='astrochangebot')

    return str(request.data)



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
