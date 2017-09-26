[![Build Status](https://travis-ci.org/astropy/astropy-bot.svg?branch=master)](https://travis-ci.org/astropy/astropy-bot)

### About

This is a GitHub bot written using Flask for the Astropy project which can be
installed via GitHub integrations. We use the concept of flask 'blueprints' to
separate the different functionality. Each blueprint is defined in a separate
file inside [changebot/blueprints](changebot/blueprints). The bot includes the
following functionality:

* Check pull requests whenever they are changed. For now the checks only
  include making sure the changelog is consistent with the milestone and the
  labels but this could be expanded in future. This is defined in
  [pull_request_checker.py](changebot/blueprints/pull_request_checker.py).

* Check for issues labelled as 'Close?' that have become stale, and close them
  (with a warning period). This is defined in
  [stale_issues.py](changebot/blueprints/stale_issues.py).

* Check for pull requests labelled as 'Close?' that have become stale, and close
  them (with a warning period). This is defined in
  [stale_pull_requests.py](changebot/blueprints/stale_pull_requests.py).

More details about the bot and its components is provided in the sections below.

### Overall bot set-up

The GitHub app is defined in the [Astropy organization settings](https://github.com/organizations/astropy/settings/apps/astropy-bot).
The two main settings, in addition to generating a private key, are:

* **User authorization callback URL**: http://astrochangebot.herokuapp.com/callback
* **Webhook URL**: http://astrochangebot.herokuapp.com/hook

The permissions of the app should be read/write access to **Commit statuses**,
**Issues** and **Pull requests**. The app can be added to specific repositories
under the **Your installations** tab, by clicking on the gearbox next to
**Astropy**, which goes to [this page](https://github.com/organizations/astropy/settings/installations/37176).

The ``astrochangebot.herokuapp.com`` server is a Flask app that is set up on
[Heroku](http://heroku.com). We use the auto-deploy functionality in Heroku
to re-deploy the app anytime a change is made to this repository. The only
custom configuration on Heroku is that certain environment variables are set
through the Heroku admin interface. The main required environment variables
are::

* ``GITHUB_APP_INTEGRATION_ID`` - this should be set to the integration ID
  provided by GitHub. For this app the integration ID is currently 3400 (this
  is not a secret).
* ``GITHUB_APP_PRIVATE_KEY`` - GitHub generates a private key when setting up
  a GitHub integration. This private key should look like:

      -----BEGIN RSA PRIVATE KEY-----
      <some random characters>
      -----END RSA PRIVATE KEY-----

  the whole key, including the ``BEGIN`` and ``END`` header and footer should be
  pasted into the field for the ``GITHUB_APP_PRIVATE_KEY`` environment variable.

* ``CRON_TOKEN`` - this should be set to a random string known only to the
  person or people who need to run cron jobs manually. Some of the functionality
  in the bot is not intended to be triggered by GitHub but instead by cron jobs.
  However, we don't want just anyone to be able to run these cron jobs, so
  this environment variable is the shared secret/password that allows certain
  actions to be triggered.

In addition to these environment variables, there are several other environment
variables required for specific components of the bot, described in the sections
below.

### Pull request checker

The pull request checker is intended to be triggered by GitHub whenever there
is a change in a pull request.  Currently the main code that gets run when this
happens is the ``check_changelog_consistency`` function, which makes sure that
the changelog is consistent with the pull request number, labels, and milestone.
The main logic is defined in
[pull_request_checker.py](changebot/blueprints/pull_request_checker.py) and
[changelog_helpers.py](changebot/blueprints/changelog_helpers.py)

### Stale issue and pull request checkers

The components to check for stale issues and pull requests are intended to be
triggered by a cron job rather than from GitHub. The main reasons for this are
because these tend to do more API calls than the single pull request checker
(because e.g. all open pull requests need to be queried) and because by
definition we are looking for *inactivity* rather than activity.

These components can be configured via the following environment variables on
Heroku:

* ``STALE_ISSUE_CLOSE`` - this should be set to ``TRUE`` or ``FALSE``. If
  ``FALSE``, this doesn't check for whether issues should be closed, only
  whether the warning about closing should be posted. The intent is that this
  should always be ``TRUE`` except the first time that this is run.

* ``STALE_ISSUE_WARN_SECONDS`` - the time in seconds from when an issue was
  labelled as **Close?** in order to be warned that it will be closed.

* ``STALE_ISSUE_CLOSE_SECONDS`` - the time in seconds from when an issue was
  labelled as **Close?** in order to be considered ready for closing. This
  should be larger than ``STALE_ISSUE_WARN_SECONDS``.

* ``STALE_PRS_CLOSE`` - this should be set to ``TRUE`` or ``FALSE``. If
  ``FALSE``, this doesn't check for whether pull requests should be closed, only
  whether the warning about closing should be posted. The intent is that this
  should always be ``TRUE`` except the first time that this is run.

* ``STALE_PRS_WARN_SECONDS`` - the time in seconds from the last commit in
  order to be warned that it will be closed.

* ``STALE_PRS_CLOSE_SECONDS`` - the time in seconds from the last commit in
  order to be considered ready for closing. This should be larger than
  ``STALE_PRS_WARN_SECONDS``.

For issues, removing the **Close?** label and adding it back resets the clock.
For pull requests, adding a new commit resets the clock, while adding the
**keep-open** label means that this pull request will not be touched by the bot.

To run these checks, you can access http://astrochangebot.herokuapp.com/close_stale_issues using a POST request and with the following parameters encoded in JSON:

* ``'repository'``: the name of the repository to run the checks for, including the owner (e.g. ``astropy/astropy``)
* ``'cron_token'``: this should be the same as the ``CRON_TOKEN`` environment variable
* ``'installation'``: this should be the installation ID (see the **Authentication** section). For the astropy organization repositories, this is 37176.

An example for how to do this with the requests package is:

```python
import requests

data = {'repository': 'astrofrog/test-bot',
        'cron_token': 'theactualtoken',
        'installation': '36238'}

requests.post(URL, json=data)
```

### GitHub API

The different components of the bot interact with GitHub via a set of helper
classes that live in [changebot/github/github_api.py](changebot/github/github_api.py).
These classes are ``RepoHandler``, ``IssueHandler``, and ``PullRequestHandler``. It
is possible to try these out locally, at least for the parts of the GitHub API that
do not require authentication. For example, the following should work:

```python
>>> from changebot.github.github_api import RepoHandler, IssueHandler, PullRequestHandler
>>> repo = RepoHandler('astropy/astropy')
>>> repo.get_issues('open', 'Close?')
[6025, 5193, 4842, 4549, 4058, 3951, 3845, 2603, 2232, 1920, 1024, 435, 383, 282]
>>> issue = IssueHandler('astropy/astropy', 6597)
>>> issue.labels
['Bug', 'coordinates']
>>> pr = PullRequestHandler('astropy/astropy', 6606)
>>> pr.labels
['Enhancement', 'Refactoring', 'testing', 'Work in progress']
>>> pr.last_commit_date
1506374526.0
```

However since these are being run un-authenticated, you may quickly run into the GitHub public API limits. If you are interested in authenticating locally, see the **Authentication** section below.

Code-wise, the authentication of the app is handled in the [changebot/github/github_auth.py](changebot/github/github_auth.py) file - the main function from there that is used in [changebot/github/github_api.py](changebot/github/github_api.py) is the ``github_request_headers`` function which returns headers for requests that contain the appropriate tokens.

### Authentication

In some cases, you may want to test the bot locally as if it was running on
Heroku. In order to do this you will need to make sure you have all the
environment variables described above set correctly.

The main ones to get right as far as authentication is concerned are:

* ``GITHUB_APP_INTEGRATION_ID`` - this ID can be found at the main GitHub app
  [settings page](https://github.com/organizations/astropy/settings/apps/astropy-bot). It should be 3400 at the time of writing this.
* ``GITHUB_APP_PRIVATE_KEY`` - don't be tempted to re-generate a key from the
  GitHub app settings. There is a key that is already generated that we should
  use - ask @astrofrog if you would like to know the key.

The last thing you will need is an **Installation ID** - a GitHub app can be
linked to different GitHub accounts, and for each account or organization, it
has a unique ID. You can find out this ID by going to **Your installations** and
then clicking on the settings box next to the account where you have a test
repository you want to interact with. The URL of the page you go to will look
like:

    https://github.com/settings/installations/36238

In this case, 37176 is the installation ID. Provided you set the environment
variables correctly, you should then be able to do e.g.:

```python
>>> from changebot.github.github_api import IssueHandler
>>> issue = IssueHandler('astrofrog/test-bot', 5, installation=36238)
>>> issue.submit_comment('I am alive!')
```

Use this power wisely! (and avoid testing out things on the main Astropy
repos...)

**Note:** authentication will not work properly if you have a ``.netrc`` file
in your home directory, so you will need to rename this file temporarily.

### Requirements

This app requires Python 3.6 to run, and dependencies are listed in ``requirements.txt``
