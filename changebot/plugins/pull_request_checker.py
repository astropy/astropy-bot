import json
import os
import re

from flask import Blueprint, request

from flask import current_app

from baldrick.plugins.github_pull_requests import pull_request_handler


CHANGELOG_PROLOGUE = re.sub('(\w+)\n', r'\1', """
Hi there @{user} :wave: - thanks for the pull request! I'm just
 a friendly :robot: that checks for
 issues related to the changelog and making sure that this
 pull request is milestoned and labeled correctly. This is
 mainly intended for the maintainers, so if you are not
 a maintainer you can ignore this, and a maintainer will let
 you know if any action is required on your part :smiley:.
""").strip() + os.linesep + os.linesep

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

CHANGELOG_EPILOGUE = os.linesep + os.linesep + re.sub('(\w+)\n', r'\1', """
*If there are any issues with this message, please report them
 [here](https://github.com/astropy/astropy-bot/issues).*
""").strip()


def is_changelog_message(message):
    return 'issues related to the changelog' in message


@pull_request_handler
def process_changelog_consistency(pr_handler, repo_handler):

    # No-op if user so desires
    if not repo_handler.get_config_value('changelog_check', True):
        return "Repo owner does not want to check change log"

    # Construct message

    message = CHANGELOG_PROLOGUE.format(user=pr_handler.user)
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

    message += CHANGELOG_EPILOGUE

    comment_url = pr_handler.submit_comment(message, comment_id=comment_id,
                                            return_url=True)

    if approve:
        pr_handler.set_status('success', 'All checks passed', 'astropy-bot',
                              target_url=comment_url)
    else:
        pr_handler.set_status('failure', 'There were failures in checks - see '
                              'comments by @astropy-bot above', 'astropy-bot',
                              target_url=comment_url)

    return message
