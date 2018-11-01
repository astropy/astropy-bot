"""Tests for changelog helpers."""

import pytest
from unittest.mock import MagicMock, PropertyMock

from changebot.blueprints.changelog_helpers import (
    review_changelog, check_changelog_consistency)


def test_review_good_changelog():
    content = """
1.1.0 (unreleased)
==================

- I made some changes. They were good. [#10]

1.0.0 (11-11-2011)
==================

- Fixed a bug some other person made. Not my fault. [#2]
    """

    issues = review_changelog(10, content, True, 'v1.1.0', [])
    assert len(issues) == 0


def test_review_short_changelog():
    content = """
1.0.0 (unreleased)
==================

- It's a whole new thing here now. [#1]
    """

    issues = review_changelog(1, content, True, 'v1.0.0', [])
    assert len(issues) == 0


def test_review_long_changelog():
    content = """
1.1.0 (unreleased)
==================

New Features
------------

foo.bar.baz
~~~~~~~~~~~

- I made some changes. They were good. [#10]

foo.frob.blurg
~~~~~~~~~~~~~~

- Wow I don't know how I ever lived without this package. [#9]

Bug Fixes
---------

foo.bar.baz
~~~~~~~~~~~

- Oh man this was a really stupid bug. Glad I fixed it. [#11]

foo.frob.blurg
~~~~~~~~~~~~~~

- Who was the idiot who broke this? It wasn't me. [#12]

1.0.0 (11-11-2011)
==================

- My code never has bugs. [#2]
    """

    issues = review_changelog(12, content, True, 'v1.1.0', [])
    assert len(issues) == 0


@pytest.mark.parametrize('label', ['no-changelog-entry-needed',
                                   'Affects-dev',
                                   'skip-changelog-checks'])
def test_review_missing_with_tag(label):
    content = """
1.1.0 (unreleased)
==================

- I made some changes. They were good. [#10]

1.0.0 (11-11-2011)
==================

- Fixed a bug some other person made. Not my fault. [#2]
    """

    issues = review_changelog(11, content, False, 'v1.1.0', [label])
    assert len(issues) == 0


# https://github.com/astropy/astropy-bot/issues/59
def test_review_unnecessary_changelog():
    content = """
1.1.0 (unreleased)
==================

- I made some changes. They were good. [#10]
    """

    issues = review_changelog(11, content, True, 'v1.1.0',
                              ['no-changelog-entry-needed'])
    ans = "Changelog entry present but **no-changelog-entry-needed** label set"
    assert len(issues) == 1 and issues[0] == ans


def test_repo_no_changelog_okay():
    """
    Repo has no change log and this is okay.
    """
    repo = MagicMock()
    repo.get_file_contents.side_effect = FileNotFoundError

    pr = MagicMock()
    type(pr).labels = PropertyMock(
        return_value=['Docs', 'skip-changelog-checks'])

    assert check_changelog_consistency(repo, pr) == []


def test_repo_no_changelog_oops():
    """
    Repo has no change log and this is not expected.
    """
    repo = MagicMock()
    repo.get_file_contents.side_effect = FileNotFoundError

    pr = MagicMock()
    type(pr).labels = PropertyMock(return_value=['no-changelog-entry-needed'])

    assert check_changelog_consistency(repo, pr) == [
        "This repository does not appear to have a change log!"]
