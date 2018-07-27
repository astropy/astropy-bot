from astropy_changelog import loads

from baldrick.plugins.utils import get_config_with_app_defaults
from baldrick.plugins.github_pull_requests import pull_request_handler


@pull_request_handler
def check_changelog_consistency(repo_handler, pr_handler):

    labels = pr_handler.labels

    # Changelog checks manually disabled for this pull request.
    # This is originally for post-release insertion of new changelog sections.
    if 'skip-changelog-checks' in labels:
        return {}

    cl_config = get_config_with_app_defaults(pr_handler, "changelog_checker", {})
    filename = cl_config.get("filename", 'CHANGES.rst')

    statuses = {}

    # Try different filenames - in future we could make
    try:
        changelog = repo_handler.get_file_contents(filename)
    except FileNotFoundError:
        statuses['changelog_milestone'] = {'description': f'Changelog {filename} not found',
                                           'state': 'failure'}
        return statuses

    # Parse changelog
    changelog = loads(changelog)

    # Find versions for the pull request we are looking at
    versions = changelog.versions_for_issue(pr_handler.number)

    if len(versions) > 1:

        statuses['changelog_milestone'] = {'description': f'Changelog entry present in multiple version sections ({", ".join(versions)})',
                                           'state': 'failure'}

    elif len(versions) == 1:

        if 'no-changelog-entry-needed' in pr_handler.labels:
            statuses['changelog_milestone'] = {'description': 'Changelog entry present but **no-changelog-entry-needed** label set',
                                               'state': 'failure'}
        elif 'Affects-dev' in pr_handler.labels:
            statuses['changelog_milestone'] = {'description': 'Changelog entry present but **Affects-dev** label set',
                                               'state': 'failure'}
        elif pr_handler.milestone and not pr_handler.milestone.startswith(versions[0]):
            statuses['changelog_milestone'] = {'description': 'Changelog entry section ({0}) '
                                                              'inconsistent with milestone ({1})'
                                                              .format(versions[0], pr_handler.milestone),
                                               'state': 'failure'}
        else:
            statuses['changelog_milestone'] = {'description': 'Changelog entry consistent with milestone',
                                               'state': 'success'}

    else:

        if 'Affects-dev' in pr_handler.labels:

            statuses['changelog_milestone'] = {'description': 'Changelog entry not present, as expected since the **Affects-dev** label is present',
                                               'state': 'success'}

        elif 'no-changelog-entry-needed' in pr_handler.labels:

            statuses['changelog_milestone'] = {'description': 'Changelog entry not present, as expected since the **no-changelog-entry-needed** label is present',
                                               'state': 'success'}

        else:

            statuses['changelog_milestone'] = {'description': 'Changelog entry not present, (or pull request number '
                                                              'missing) and neither the **Affects-dev** nor the '
                                                              '**no-changelog-entry-needed** label are set',
                                               'state': 'failure'}

    return statuses
