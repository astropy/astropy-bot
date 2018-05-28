import os
import re

from flask import current_app

from changebot.blueprints.changelog_helpers import check_changelog_consistency

from .pull_request_checker import pull_request_check

CHANGELOG_NOT_DONE = re.sub('(\w+)\n', r'\1', """
I see this is {status} pull request. I'll report back
 on the checks once the PR {is_done}.
""").strip()

CHANGELOG_BAD_LIST = re.sub('(\w+)\n', r'\1', """
I noticed the following issues with this pull request:
""").strip() + os.linesep + os.linesep

CHANGELOG_BAD_EPILOGUE = os.linesep + re.sub('(\w+)\n', r'\1', """
Would it be possible to fix these? Thanks!
""").strip()

CHANGELOG_GOOD = re.sub('(\w+)\n', r'\1', """
Everything looks good from my point of view! :+1:
""").strip()


@pull_request_check
def process_changelog_consistency(pr_handler, repo_handler):

    # No-op if user so desires
    if not repo_handler.get_config_value('changelog_check', True):
        return "Repo owner does not want to check change log"

    # Construct message

    message = current_app.pull_request_prolog.format(user=pr_handler.user)
    approve = False  # This is so that WIP and EXP shall not pass

    if 'Work in progress' in pr_handler.labels:
        message += CHANGELOG_NOT_DONE.format(
            status='a work in progress', is_done='is ready for review')

    elif 'Experimental' in pr_handler.labels:
        message += CHANGELOG_NOT_DONE.format(
            status='an experimental', is_done='discussion in settled')

    else:
        # Run checks
        issues = check_changelog_consistency(repo_handler, pr_handler)

        if len(issues) > 0:

            message += CHANGELOG_BAD_LIST
            for issue in issues:
                message += "* {0}\n".format(issue)

            message += CHANGELOG_BAD_EPILOGUE

            if len(issues) == 1:
                message = (message.replace('issues with', 'issue with')
                           .replace('fix these', 'fix this'))

        else:

            message += CHANGELOG_GOOD
            approve = True

    return [message], approve
