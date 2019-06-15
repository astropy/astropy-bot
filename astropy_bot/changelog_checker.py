from astropy_changelog import loads

from baldrick.plugins.github_pull_requests import pull_request_handler


@pull_request_handler
def check_changelog_consistency(pr_handler, repo_handler):

    labels = pr_handler.labels

    # Changelog checks manually disabled for this pull request.
    # This is originally for post-release insertion of new changelog sections.
    if 'skip-changelog-checks' in labels:
        return {}

    cl_config = repo_handler.get_config_value("changelog_checker", {})
    filename = cl_config.get("filename", 'CHANGES.rst')

    statuses = {}

    # Try different filenames - in future we could make
    try:
        changelog = repo_handler.get_file_contents(filename)
    except FileNotFoundError:
        statuses['changelog'] = {'description': f'This repository does not appear to have a change log! (expecting a file named {filename})',
                                 'state': 'failure'}
        return statuses

    # Parse changelog
    changelog = loads(changelog)

    # Find versions for the pull request we are looking at
    versions = changelog.versions_for_issue(pr_handler.number)

    if len(versions) > 1:

        statuses['changelog'] = {'description': f'Changelog entry present in multiple version sections ({", ".join(versions)})',
                                 'state': 'failure'}

    elif len(versions) == 1:

        # Extract milestone and version
        milestone = pr_handler.milestone
        version = versions[0]

        # Strip any 'v' prefix from these
        if milestone is not None and milestone.startswith('v'):
            milestone = milestone[1:]
        if version.startswith('v'):
            version = version[1:]

        if 'no-changelog-entry-needed' in pr_handler.labels:
            statuses['changelog'] = {'description': 'Changelog entry present but **no-changelog-entry-needed** label set',
                                     'state': 'failure'}
        elif 'Affects-dev' in pr_handler.labels:
            statuses['changelog'] = {'description': 'Changelog entry present but **Affects-dev** label set',
                                     'state': 'failure'}
        elif milestone:
            if milestone == version:
                statuses['changelog'] = {'description': 'Changelog entry consistent with milestone',
                                         'state': 'success'}
            else:
                statuses['changelog'] = {'description': 'Changelog entry section ({0}) '
                                         'inconsistent with milestone ({1})'
                                         .format(version, milestone),
                                         'state': 'failure'}
        else:
            statuses['changelog'] = {'description': 'Cannot check for consistency of milestone since milestone is not set',
                                     'state': 'failure'}

    else:

        if 'Affects-dev' in pr_handler.labels:

            statuses['changelog'] = {'description': 'Changelog entry not present, as expected since the **Affects-dev** label is present',
                                     'state': 'success'}

        elif 'no-changelog-entry-needed' in pr_handler.labels:

            statuses['changelog'] = {'description': 'Changelog entry not present, as expected since the **no-changelog-entry-needed** label is present',
                                     'state': 'success'}

        else:

            statuses['changelog'] = {'description': 'Changelog entry not present, (or PR number '
                                     'missing) and neither the **Affects-dev** nor the '
                                     '**no-changelog-entry-needed** label are set',
                                     'state': 'failure'}

    return statuses
