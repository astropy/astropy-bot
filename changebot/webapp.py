import os

from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

from changebot.blueprints.stale_issues import stale_issues
from changebot.blueprints.stale_pull_requests import stale_pull_requests
from changebot.blueprints.pull_request_checker import pull_request_checker
from changebot.blueprints.circleci import circleci

app = Flask('astropy-bot')

app.wsgi_app = ProxyFix(app.wsgi_app)

app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']
app.cron_token = os.environ['CRON_TOKEN']
app.status_token = os.environ.get('STATUS_TOKEN', None)
app.stale_issue_close = os.environ['STALE_ISSUE_CLOSE'].lower() == 'true'
app.stale_issue_close_seconds = float(os.environ['STALE_ISSUE_CLOSE_SECONDS'])
app.stale_issue_warn_seconds = float(os.environ['STALE_ISSUE_WARN_SECONDS'])
app.stale_pull_requests_close = os.environ['STALE_PULL_REQUEST_CLOSE'].lower() == 'true'
app.stale_pull_requests_close_seconds = float(os.environ['STALE_PULL_REQUEST_CLOSE_SECONDS'])
app.stale_pull_requests_warn_seconds = float(os.environ['STALE_PULL_REQUEST_WARN_SECONDS'])

app.register_blueprint(pull_request_checker)
app.register_blueprint(stale_issues)
app.register_blueprint(stale_pull_requests)
app.register_blueprint(circleci)


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Installation authorized"
