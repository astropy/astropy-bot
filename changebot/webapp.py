import os
import json

from flask import Flask, redirect, url_for, request

from flask_dance.contrib.github import github, make_github_blueprint

from github import Github
from github.GithubException import GithubException

from werkzeug.contrib.fixers import ProxyFix

app = Flask('astrochangebot')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ["GITHUB_OAUTH_CLIENT_ID"]
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ["GITHUB_OAUTH_CLIENT_SECRET"]
github_bp = make_github_blueprint(scope='repo:status,write:repo_hook')
app.register_blueprint(github_bp, url_prefix="/login")


@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    return "You are @{login} on GitHub".format(login=resp.json()["login"])


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


@app.route("/enable/<owner>/<repository>")
def enable(owner, repository):

    if not github.authorized:
        return redirect(url_for("github.login"))

    token = github.token['access_token']

    gh = Github(token)
    repo = gh.get_repo('{owner}/{repository}'.format(owner=owner, repository=repository))

    hook_config = {'url': request.url_root + 'hook',
                   'content_type': 'json'}

    try:
        repo.create_hook('web', hook_config,
                         events=['pull_request', 'push', 'issues'])
    except GithubException as exc:
        for error in exc.data['errors']:
            if 'Hook already exists' in error['message']:
                return "Hook already enabled for {owner}/{repository}".format(owner=owner, repository=repository)
        raise

    return "Hook enabled for {owner}/{repository}".format(owner=owner, repository=repository)


@app.route("/disable/<owner>/<repository>")
def disable(owner, repository):

    if not github.authorized:
        return redirect(url_for("github.login"))

    token = github.token['access_token']

    gh = Github(token)
    repo = gh.get_repo('{owner}/{repository}'.format(owner=owner, repository=repository))

    removed = False
    for hook in repo.get_hooks():
        if hook.config['url'] == request.url_root + '/hook':
            hook.delete()
            removed = True

    if removed:
        return "Hook disabled for {owner}/{repository}".format(owner=owner, repository=repository)
    else:
        return "No hook found for {owner}/{repository}".format(owner=owner, repository=repository)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
