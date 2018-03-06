import json
import time
import requests
from humanize import naturaltime, naturaldelta
from changebot.github.github_api import IssueHandler, RepoHandler, HOST
from changebot.github.github_auth import github_request_headers


from flask import Blueprint, request, current_app

commit_status = Blueprint('commit_status', __name__)


@commit_status.route('/circleci', methods=['POST'])
def circleci_handler():
    if not request.data:
        print("No payload recieved")

    payload = json.loads(request.data)

    # Validate we have the keys we need, otherwise ignore the push
    required_keys = {'vcs_revision',
                     'username',
                     'reponame',
                     'status'}

    optional_keys = {}

    print(payload)
    if not required_keys.issubset(payload.keys()):
        return 'Payload missing {}'.format(' '.join(required_keys - payload.keys()))

    # invalid_keys = payload.keys() - (required_keys | optional_keys)
    # if invalid_keys:
    #     return f"Received unknown values {' '.join(invalid_keys)}."

    if "target_url" not in payload:
        payload['target_url'] = None


    # set_commit_status(**payload)

    return "All good"


def set_status(repository, commit_hash, state, description, context, *, headers, target_url=None):
    """
    Set status message in a pull request on GitHub.

    Parameters
    ----------
    state : { 'pending' | 'success' | 'error' | 'failure' }
        The state to set for the pull request.

    description : str
        The message that appears in the status line.

    context : str
        A string used to identify the status line.

    target_url : str or `None`
        Link to bot comment that is relevant to this status, if given.

    """

    data = {}
    data['state'] = state
    data['description'] = description
    data['context'] = context

    if target_url is not None:
        data['target_url'] = target_url

    url = f'{HOST}/repos/{repository}/statuses/{commit_hash}'
    response = requests.post(url, json=data, headers=headers)
    assert response.ok, response.content


def set_commit_status(repository, installation, commit_hash, state, description, target_url):

    headers = github_request_headers(installation)

    repo = RepoHandler(repository, 'master', installation)
    allowed_url_regex = repo.get_config_value('commit_status_url_regex', '*')

    print(repository, installation, commit_hash)
