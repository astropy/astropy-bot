from os import path, sep
from baldrick.plugins.github_pull_requests import pull_request_handler


@pull_request_handler
def autolabel_subpackages(pr_handler, repo_handler):
    files = pr_handler.get_modified_files()
    all_labels = repo_handler.get_all_labels()
    existing_labels = set(pr_handler.labels)

    for file in files:
        subdir = path.dirname(file)

        if subdir:
            root, *subpkg = subdir.split(sep)

            if subpkg:
                dot_name = '.'.join(subpkg)
                if dot_name in all_labels and dot_name not in existing_labels:
                    existing_labels.add(dot_name)

    pr_handler.set_labels(existing_labels)

    return None
