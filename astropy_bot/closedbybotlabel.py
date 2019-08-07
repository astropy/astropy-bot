from baldrick.blueprints.github import github_webhook_handler
from baldrick.github.github_api import IssueHandler


@github_webhook_handler
def handle_closed_by_bot_label(repo_handler, payload, headers):
    """
    Auto-apply closed-by-bot label when bot closes issue or pull request.
    """
    event = headers['X-GitHub-Event']

    # NOTE: Update this as needed
    closed_by_user = 'astropy-bot[bot]'
    label_name = 'closed-by-bot'

    if event not in ('pull_request', 'issues') or payload['action'] != 'closed':
        return "Not a closed pull_request or issues event"

    if event == 'pull_request':
        number = payload['pull_request']['number']
    elif event == 'issues':
        number = payload['issue']['number']
    else:
        return "Not an issue or pull request"

    # closed_by only accessible as Issue, not PullRequest
    handler = IssueHandler(repo_handler.repo, number, repo_handler.installation)
    if handler.json['closed_by']['login'] == closed_by_user:
        handler.set_labels(label_name)
        return f"Setting {label_name}"
