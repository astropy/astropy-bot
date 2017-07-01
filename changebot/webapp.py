import os
import json

from flask import Flask, request

from werkzeug.contrib.fixers import ProxyFix

from changebot.changelog import check_changelog_consistency
from changebot.github_api import RepoHandler, PullRequestHandler


app = Flask('astrochangebot')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Installation authorized"


@app.route("/hook", methods=['POST'])
def hook():

    event = request.headers['X-GitHub-Event']

    if event not in ('pull_request', 'issues'):
        return "Not a pull_request or issues event"

    # Parse the JSON sent by GitHub
    payload = json.loads(request.data)

    if 'installation' not in payload:
        return "No installation key found in payload"
    else:
        installation = payload['installation']['id']

    if event == 'pull_request':
        number = payload['pull_request']['number']
    elif event == 'issues':
        number = payload['issue']['number']
    else:
        return

    repository = payload['repository']['full_name']

    # TODO: cache handlers and invalidate the internal cache of the handlers on
    # certain events.
    pr_handler = PullRequestHandler(repository, number, installation)

    branch = pr_handler.head_branch
    repo_handler = RepoHandler(repository, branch, installation)

    # Run checks
    # TODO: in future, make this more generic so that any checks can be run.
    # we could have a registry of checks and concatenate the responses
    success, message = check_changelog_consistency(repo_handler, pr_handler)

    if success:
        pr_handler.submit_review('approve', message)
        pr_handler.set_status('success', 'All checks passed', 'changebot')
    else:
        pr_handler.submit_review('request_changes', message)
        pr_handler.set_status('failure', 'There were failures in checks - see '
                                         'comments by @astrochangebot above',
                                         'changebot')

    return message
