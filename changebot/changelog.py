import re
import base64
import requests

from changebot.github_auth import github_request_headers

__all__ = ['check_changelog_consistency']


BLOCK_PATTERN = re.compile('\[#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')


def find_prs_in_changelog(content):
    issue_numbers = []
    for block in BLOCK_PATTERN.finditer(content):
        block_start, block_end = block.start(), block.end()
        block = content[block_start:block_end]
        for m in ISSUE_PATTERN.finditer(block):
            start, end = m.start(), m.end()
            issue_numbers.append(int(block[start:end][1:]))
    return issue_numbers


def find_prs_in_changelog_by_section(content):

    changelog_prs = {}
    version = None
    subcontent = ''
    previous = None

    for line in content.splitlines():
        if '-------' in line:
            if version is not None:
                for pr in find_prs_in_changelog(subcontent):
                    changelog_prs[int(pr)] = version
            version = previous.strip().split('(')[0].strip()
            if 'v' not in version:
                version = 'v' + version
            subcontent = ''
        elif version is not None:
            subcontent += line
        previous = line

    return changelog_prs


def check_changelog_consistency(webhook_payload):

    # Get pull request number
    pull_request = webhook_payload['number']

    # Figure out the URL to the changelog file for the PR head
    url_changes = webhook_payload['pull_request']['head']['repo']['contents_url'].replace('{+path}', 'CHANGES.rst')

    # Make sure we get the changes from the same branch.
    data = {}
    data['ref'] = webhook_payload['pull_request']['head']['ref']

    # Get the contents of the changelog file
    headers = github_request_headers(webhook_payload['installation'])
    response = requests.get(url_changes, params=data, headers=headers)
    changelog_base64 = response.json()['content']

    # Decode from base64
    changelog = base64.b64decode(changelog_base64)

    # Next, we need to get the milestone of the PR
    milestone = webhook_payload['milestone']['title']

    # Finally, we need to get the labels
    response = requests.get(webhook_payload['milestone']['labels_url'], headers=headers)
    labels = [label['name'] for label in response.json()]

    status, message = review_changelog(pull_request, changelog, milestone, labels)


def review_changelog(pull_request, changelog, milestone, labels):

    issues = []

    if milestone is None:
        issues.append("The milestone has not been set")

    sections = find_prs_in_changelog_by_section(changelog)
    changelog_entry = pull_request in sections
    if changelog_entry:
        if not milestone.startswith(sections[pull_request]):
            issues.append("Changelog entry section ({0}) inconsistent "
                          "with milestone ({1})".format(sections[pull_request], milestone))

    if 'no-changelog-entry-needed' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but **no-changelog-entry-needed** label set")
    elif 'Affects-dev' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but **Affects-dev** label set")
    else:
        if not changelog_entry:
            issues.append("Changelog entry not present (or pull request number "
                          "missing) and neither the **Affects-dev** nor the "
                          "**no-changelog-entry-needed** label are set")

    if len(issues) > 0:

        message = ("Hi there :wave: - I noticed the following issues with this "
                   "pull request:\n\n")
        for issue in issues:
            message += "* {0}\n".format(issue)

        message += "\nWould it be possible to fix these? Thanks! \n"

        if len(issues) == 1:
            message = (message.replace('issues with', 'issue with')
                       .replace('fix these', 'fix this'))

        message += ("\n*If you believe the above to be incorrect, you can ping "
                    "@astrofrog*\n")

        return False, message

    else:

        return True, "All good!"
