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

The Flask app is set up on [Heroku](http://heroku.com), and we use the auto-deploy
functionality in Heroku to re-deploy the app anytime a change is made to this
repository. The only custom configuration on Heroku is that certain environment
variables are set through the Heroku admin interface. The main required
environment variables are::

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

### Requirements

This app requires Python 3.6 to run, and dependencies are listed in ``requirements.txt``
