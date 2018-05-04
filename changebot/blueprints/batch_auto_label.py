"""
Module for bot to retroactively apply automatic labelling.
For example, applying ``closed-by-bot`` label to issues/PRs
closed by the bot a long time ago.

.. todo:: This was written as a quick hack for one-time run.
          Will need to revisit for extra sentience points.

"""
from changebot.github.github_api import IssueHandler, RepoHandler


def retroactive_closed_by_bot(repository, installation):
    # Get issues that are closed
    repo = RepoHandler(repository, 'master', installation)
    issuelist = repo.get_issues('closed', exclude_pr=False)
    label_name = 'closed-by-bot'
    n_labeled = 0

    for n in issuelist:
        print(f'Checking {n}')
        yield f'Checking {n}'

        issue = IssueHandler(repository, n, installation)

        # Still open, nothing to do.
        if not issue.is_closed:
            continue

        # Only want issues/PRs closed by the bot. Any bot will do.
        # NOTE: If it needs to be case-sensitive, try "Bot" without lower().
        if issue.json['closed_by']['type'].lower() != 'bot':
            continue

        # Label already there, nothing to do.
        # Labels cost extra requests, so we check this last.
        if label_name in issue.labels:
            continue

        # Set the label.
        issue.set_labels(label_name)
        print(f'Added {label_name} to {n}')
        yield f'Added {label_name} to {n}'

        n_labeled += 1  # For sanity check

    print(f'Added {label_name} to {n_labeled} issues/PRs')
    yield f'Added {label_name} to {n_labeled} issues/PRs'
