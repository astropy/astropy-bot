from flask import current_app

from .pull_request_checker import pull_request_check


@pull_request_check
def process_milestone(pr_handler, repo_handler):
    """
    A very simple set a failing status if the milestone is not set.
    """
    if not pr_handler.milestone:
            pr_handler.set_status('failure', 'This pull request does not have a milestone set.', current_app.bot_username + ": milestone")
    else:
            pr_handler.set_status('success', 'This pull request has a milestone set.', current_app.bot_username + ": milestone")

    return [], None
