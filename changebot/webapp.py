import os

from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

from changebot.blueprints.circleci import circleci

app = Flask('astropy-bot')

app.wsgi_app = ProxyFix(app.wsgi_app)

app.integration_id = int(os.environ['GITHUB_APP_INTEGRATION_ID'])
app.private_key = os.environ['GITHUB_APP_PRIVATE_KEY']
app.name = os.environ.get("GILES_NAME", "Giles")

app.register_blueprint(circleci)


@app.route("/")
def index():
    return "Nothing to see here"


@app.route("/installation_authorized")
def installation_authorized():
    return "Installation authorized"
