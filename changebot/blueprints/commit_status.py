import json
import time
from humanize import naturaltime, naturaldelta
from changebot.github.github_api import IssueHandler, RepoHandler
from flask import Blueprint, request, current_app

commit_status = Blueprint('commit_status', __name__)


@commit_status.route('/commit_status', methods=['POST'])
def close_stale_issues():
    payload = json.loads(request.data)
    required_keys = {'repository', 'status_token', 'installation', 'commit_hash'}
    if payload.keys() <= required_keys:
        return 'Payload mising {}'.format(payload.keys() - required_keys)
    if not current_app.status_token or payload['status_token'] != current_app.status_token:
        return "Incorrect status_token"
    set_commit_status(payload['repository'], payload['installation'], payload['commit_hash'])
    return "All good"


def set_commit_status(repository, installation, commit_hash):

    repo = RepoHandler(repository, 'master', installation)
    allowed_url_regex = repo.get_config_value('commit_status_url_regex', '*')

    print(repository, installation, commit_hash)

