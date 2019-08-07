from unittest.mock import MagicMock, patch

import pytest
from baldrick.github.github_api import RepoHandler

from astropy_bot.closedbybotlabel import handle_closed_by_bot_label


class TestClosedByBotLabelHandler:
    def setup_class(cls):
        cls.repo = RepoHandler('test-repo', installation=123)
        cls.closed_by = 'astropy-bot[bot]'
        cls.label_name = 'closed-by-bot'

    def setup_method(self):
        self.requests_get_mock = patch('requests.get', self._requests_get)
        self.requests_post_mock = patch('requests.post')
        self.get_file_contents_mock = patch('baldrick.github.github_api.GitHubHandler.get_file_contents')
        self.get_installation_token_mock = patch('baldrick.github.github_auth.get_installation_token')
        self.set_labels_mock = patch('baldrick.github.github_api.IssueHandler.set_labels')

        self.requests_get = self.requests_get_mock.start()
        self.requests_post = self.requests_post_mock.start()
        self.get_file_contents = self.get_file_contents_mock.start()
        self.get_installation_token = self.get_installation_token_mock.start()
        self.set_labels = self.set_labels_mock.start()

        self.get_installation_token.return_value = 'abcdefg'

    def teardown_method(self):
        self.requests_get_mock.stop()
        self.requests_post_mock.stop()
        self.get_file_contents_mock.stop()
        self.get_installation_token_mock.stop()
        self.set_labels_mock.stop()

    def _requests_get(self, url, headers=None):
        req = MagicMock()
        req.ok = True
        if url == 'https://api.github.com/repos/test-repo/issues/1234':
            req.json.return_value = {'closed_by': {'login': self.closed_by}}
        else:
            raise ValueError('Unexepected URL: {0}'.format(url))
        return req

    @pytest.mark.parametrize(
        ('event', 'action', 'call_count'),
        [('pull_request', 'closed', 1),
         ('pull_request', 'opened', 0),
         ('issues', 'closed', 1),
         ('issues', 'opened', 0),
         ('fake_event', 'closed', 0)])
    def test_closed_label(self, event, action, call_count):
        headers = {'X-GitHub-Event': event}
        if event == 'issues':
            name = 'issue'
        else:
            name = event
        payload = {name: {'number': '1234'},
                   'repository': {'full_name': 'test-repo'},
                   'action': action,
                   'installation': {'id': '123'}}
        handle_closed_by_bot_label(self.repo, payload, headers)
        assert self.set_labels.call_count == call_count
        if call_count > 0:
            assert self.set_labels.call_args == ((self.label_name, ), )

    @pytest.mark.parametrize('event', ['pull_request', 'issues'])
    def test_closed_by_person(self, event):
        orig_closed_by = self.closed_by
        self.closed_by = 'chani'

        headers = {'X-GitHub-Event': event}
        if event == 'issues':
            name = 'issue'
        else:
            name = event
        payload = {name: {'number': '1234'},
                   'repository': {'full_name': 'test-repo'},
                   'action': 'closed',
                   'installation': {'id': '123'}}
        handle_closed_by_bot_label(self.repo, payload, headers)
        assert self.set_labels.call_count == 0

        self.closed_by = orig_closed_by
