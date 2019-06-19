from baldrick.plugins.github_pull_requests import pull_request_handler


COPYEDITOR_GH_HANDLE = 'lglattly'


@pull_request_handler
def check_copyedit_docs(pr_handler, repo_handler):
    statuses = {}

    if 'docs' in pr_handler.labels:
        if 'copyedited' in pr_handler.labels:
            statuses['copyedit'] = {
                'description': "This PR has been copyedited.",
                'state': 'success'
            }

        else:
            statuses['copyedit'] = {
                'description': "This PR modifies the documentation and is "
                               "waiting for copyediting. No action is needed "
                               "from the contributor.",
                'state': 'failure'
            }

    else:
        return None

    if COPYEDITOR_GH_HANDLE not in pr_handler.json['assignees']:
        pr_handler.add_assignees(COPYEDITOR_GH_HANDLE)

    return statuses
