import os

from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

from changebot.stale_issues import stale_issues
from changebot.stale_pull_requests import stale_prs
from changebot.changelog_consistency import changelog_consistency

app = Flask('astropy-bot')

app.wsgi_app = ProxyFix(app.wsgi_app)

app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']
app.cron_token = os.environ['CRON_TOKEN']
app.stale_issue_close = os.environ['STALE_ISSUE_CLOSE'].lower() == 'true'
app.stale_issue_close_seconds = float(os.environ['STALE_ISSUE_CLOSE_SECONDS'])
app.stale_issue_warn_seconds = float(os.environ['STALE_ISSUE_WARN_SECONDS'])
app.stale_prs_close = os.environ['STALE_PRS_CLOSE'].lower() == 'true'
app.stale_prs_close_seconds = float(os.environ['STALE_PRS_CLOSE_SECONDS'])
app.stale_prs_warn_seconds = float(os.environ['STALE_PRS_WARN_SECONDS'])

app.register_blueprint(changelog_consistency)
app.register_blueprint(stale_issues)
app.register_blueprint(stale_prs)


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Installation authorized"
