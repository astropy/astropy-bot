from baldrick.plugins.github_pull_requests import pull_request_handler


@pull_request_handler(actions=['opened'])
def draft_pr_comment(pr_handler, repo_handler):
    if not pr_handler.draft:
        return

    pr_handler.submit_comment(
        '👋 Thank you for your draft pull request! Do you know that you can '
        'use `[ci skip]` or `[skip ci]` in your commit messages to skip '
        'running continuous integration tests until you are ready?')
