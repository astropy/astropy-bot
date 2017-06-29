import os

from flask import Flask, redirect, url_for
from flask_dance.contrib.github import github, make_github_blueprint

from werkzeug.contrib.fixers import ProxyFix

app = Flask('astrochangebot')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ["GITHUB_OAUTH_CLIENT_ID"]
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ["GITHUB_OAUTH_CLIENT_SECRET"]
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login")


@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    return "You are @{login} on GitHub".format(login=resp.json()["login"])


if __name__ == "__main__":
    app.run()
