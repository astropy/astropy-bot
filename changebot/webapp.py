import os
import re

from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

from changebot.blueprints.stale_issues import stale_issues
from changebot.blueprints.stale_pull_requests import stale_pull_requests
from changebot.blueprints.pull_request_checker import pull_request_checker

app = Flask('astropy-bot')

app.wsgi_app = ProxyFix(app.wsgi_app)

app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']
app.cron_token = os.environ['CRON_TOKEN']
app.stale_issue_close = os.environ['STALE_ISSUE_CLOSE'].lower() == 'true'
app.stale_issue_close_seconds = float(os.environ['STALE_ISSUE_CLOSE_SECONDS'])
app.stale_issue_warn_seconds = float(os.environ['STALE_ISSUE_WARN_SECONDS'])
app.stale_pull_requests_close = os.environ['STALE_PULL_REQUEST_CLOSE'].lower() == 'true'
app.stale_pull_requests_close_seconds = float(os.environ['STALE_PULL_REQUEST_CLOSE_SECONDS'])
app.stale_pull_requests_warn_seconds = float(os.environ['STALE_PULL_REQUEST_WARN_SECONDS'])


"""
Configuration for the pull request checker.
"""

# This string is formatted with the pr_handler and repo_handler objects
app.pull_request_prolog = re.sub('(\w+)\n', r'\1', """
Hi there @{pr_handler.user} :wave: - thanks for the pull request! I'm just
 a friendly :robot: that checks for
 issues related to the changelog and making sure that this
 pull request is milestoned and labeled correctly. This is
 mainly intended for the maintainers, so if you are not
 a maintainer you can ignore this, and a maintainer will let
 you know if any action is required on your part :smiley:.
""").strip() + os.linesep + os.linesep


app.pull_request_epilog = os.linesep + os.linesep + re.sub('(\w+)\n', r'\1', """
*If there are any issues with this message, please report them
 [here](https://github.com/astropy/astropy-bot/issues).*
""").strip()

# This should be a substring of either the prolog or the epilog which is used
# to detect previous comments by the bot on the PR
# TODO: Make this automatically determined based on the prolog
app.pull_request_substring = "issues related to the changelog"

app.pull_request_passed = 'All checks passed'
app.bot_username = 'astropy-bot'
app.pull_request_failed = f'There were failures in checks - see comments by @{app.bot_username} above'

# Import this here to register the check with the pull request checker
from changebot.blueprints.changelog_checker import check_changelog_consistency

app.register_blueprint(pull_request_checker)
app.register_blueprint(stale_issues)
app.register_blueprint(stale_pull_requests)


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Installation authorized"
