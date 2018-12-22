# For these tests, we patch the repo and pull request handler directly rather
# than the requests to the server, as we assume the repo and pull request
# handlers are tested inside baldrick.

from unittest.mock import MagicMock

from astropy_bot.changelog_checker import check_changelog_consistency


class TestPullRequestChecker:

    def setup_method(self, method):

        self.files = {}
        self.config = {}
        self.modified_files = ['astropy/subpackage/file.py']

        self.pr_handler = MagicMock()
        self.pr_handler.number = 1234
        self.pr_handler.labels = []
        self.pr_handler.milestone = None
        self.pr_handler.get_config_value = self.get_config_value
        self.pr_handler.get_modified_files = self.get_modified_files

        self.repo_handler = MagicMock()
        self.repo_handler.get_file_contents = self.get_file_contents
        self.repo_handler.get_config_value = self.get_config_value

    def get_file_contents(self, filename, branch=None):
        if filename in self.files:
            return self.files[filename]
        else:
            raise FileNotFoundError(filename)

    def get_config_value(self, name, default):
        return self.config.get(name, default)

    def get_modified_files(self):
        return self.modified_files

    def test_skip_changelog_checks(self, app):

        # If the skip-changelog-checks label is set, we don't do any checks

        self.pr_handler.labels = ['skip-changelog-checks']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert len(statuses) == 0

    def test_smart_skip_1(self, app):

        # Test case where changelog check is automatically skipped
        # only changelog itself is modified.

        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.modified_files = ['CHANGES.rst']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Only changelog itself modified',
                                          'state': 'success'}}

    def test_smart_skip_2(self, app):

        # Test case where changelog check is automatically skipped
        # when files of interest are not modified

        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.modified_files = ['.travis.yml', 'astropy/subpackage/tests/file.py']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog not required for these changes',
                                          'state': 'success'}}

    def test_missing_file(self, app):

        # Test case where the changelog file is missing

        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'This repository does not appear to have a change log! (expecting a file named CHANGES.rst)',
                                          'state': 'failure'}}

    def test_too_many_versions(self, app):

        # Test case where the PR appears in multiple sections

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n'
                     '\n'
                     '2.0 (2018-10-23)\n'
                     '----------------\n'
                     '* change2 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry present in multiple version sections (1.0, 2.0)',
                                          'state': 'failure'}}

    def test_one_version_no_changelog_entry_needed(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.labels = ['no-changelog-entry-needed']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry present but **no-changelog-entry-needed** label set',
                                          'state': 'failure'}}

    def test_one_version_affects_dev(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.labels = ['Affects-dev']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry present but **Affects-dev** label set',
                                          'state': 'failure'}}

    def test_one_version_inconsistent_milestone(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.milestone = '2.0'

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry section (1.0) inconsistent with milestone (2.0)',
                                          'state': 'failure'}}

    def test_one_version_valid(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.milestone = '1.0'

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry consistent with milestone',
                                          'state': 'success'}}

    def test_one_version_valid_withv(self, app):

        # As above, but where milestone includes a 'v' prefix
        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n'
                     '* change1 [#1234]\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.milestone = 'v1.0'

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry consistent with milestone',
                                          'state': 'success'}}

    def test_no_version_no_changelog_entry_needed(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.labels = ['no-changelog-entry-needed']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry not present, as expected since the **no-changelog-entry-needed** label is present',
                                          'state': 'success'}}

    def test_no_version_affects_dev(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}
        self.pr_handler.labels = ['Affects-dev']

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry not present, as expected since the **Affects-dev** label is present',
                                          'state': 'success'}}

    def test_no_version_failure(self, app):

        # Test case where there is a changelog entry but the
        # no_changelog_entry_needed label is present

        changelog = ('1.0 (2018-10-22)\n'
                     '----------------\n')

        self.files['CHANGES.rst'] = changelog
        self.config['changelog_checker'] = {'filename': 'CHANGES.rst'}

        with app.app_context():
            statuses = check_changelog_consistency(self.pr_handler, self.repo_handler)

        assert statuses == {'changelog': {'description': 'Changelog entry not present, (or PR number missing) and neither the **Affects-dev** nor the **no-changelog-entry-needed** label are set',
                                          'state': 'failure'}}
