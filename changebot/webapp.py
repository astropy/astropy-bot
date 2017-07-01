import os
import json

from flask import Flask, request

from werkzeug.contrib.fixers import ProxyFix

from changebot.changelog import check_changelog_consistency
from changebot.github_api import submit_review, set_status, fill_pull_request_from_issue


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
        return "No installation key found in payload: " + request.data.decode('utf-8')

    if 'issue' in payload and 'pull_request' not in payload:
        if 'pull_request' not in payload['issue']:
            return
        fill_pull_request_from_issue(payload)

    # Run checks
    # TODO: in future, make this more generic so that any checks can be run.
    # we could have a registry of checks and concatenate the responses
    success, message = check_changelog_consistency(payload)

    if success:
        submit_review(payload, 'accept', message)
        set_status(payload, 'pass', 'All checks passed', 'changebot')
    else:
        submit_review(payload, 'request_changes', message)
        set_status(payload, 'error', 'There were failures in checks - see '
                                     'comments by @astrochangebot above',
                                     'changebot')

    return message
