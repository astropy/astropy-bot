from os import path, sep
from baldrick.plugins.github_pull_requests import pull_request_handler


def get_subpackage_labels(files, all_labels):
    labels = set()

    for file_ in files:
        subdir = path.dirname(file_)

        if subdir:
            root, *subpkg = subdir.split(sep)

            if subpkg:
                for i in range(len(subpkg)):
                    dot_name = '.'.join(subpkg[:i + 1])
                    if dot_name in all_labels:
                        labels.add(dot_name)

    return labels


@pull_request_handler
def autolabel(pr_handler, repo_handler):

    al_config = repo_handler.get_config_value("autolabel", {})
    files = pr_handler.get_modified_files()
    all_labels = repo_handler.get_all_labels()
    pr_labels = set(pr_handler.labels)
    new_labels = set()

    if al_config.get('subpackages', False):
        labels = get_subpackage_labels(files, all_labels)
        new_labels = new_labels.union(labels)

    # TODO: add other auto-labeling logic here

    if new_labels:
        pr_handler.set_labels(pr_labels.union(new_labels))

    return None
