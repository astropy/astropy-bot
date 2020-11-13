[![Build Status](https://github.com/astropy/astropy-bot/workflows/CI/badge.svg)](https://github.com/astropy/astropy-bot/actions)
[![Coverage Status](https://codecov.io/gh/astropy/astropy-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/astropy/astropy-bot)

### About

This is a GitHub bot for the Astropy project that is based on
[baldrick](https://baldrick.readthedocs.io) and can be installed via GitHub
integrations. The bot uses the following built-in plugins from baldrick:

* Check for issues labeled as "Close?" that have become stale, and close them
  (with a warning period).

* Check for pull requests that have become stale, and close
  them (with a warning period).

* Check that pull requests are milestoned

and also defines a custom plugin that makes sure that the changelog is
consistent with the milestone and the labels.

A large fraction of the functionality that used to be in astropy-bot has been
generalized and moved to [baldrick](https://baldrick.readthedocs.io). We
recommend that you familiarize yourself with the baldrick documentation, and we
only cover things specific to this bot/repository in the rest of this README.

### Overall bot set-up

The **astropy-bot** app is set up on [Heroku](https://heroku.com) and is
available at http://astrochangebot.herokuapp.com.

For more details about how to
set up a baldrick app on Heroku, see [Setting up an app on Heroku](https://baldrick.readthedocs.io/en/latest/heroku.html), including the section
on setting up the scheduled jobs for the stale issue/pull request checkers. and
for details about creating the GitHub app, see
[Registering and installing a GitHub app](https://baldrick.readthedocs.io/en/latest/github.html).

For Astropy, the GitHub app for this bot is defined in the
[Astropy organization settings](https://github.com/organizations/astropy/settings/apps/astropy-bot)
(not everyone will be able to see this).

#### Install the bot in a repository

Go to https://github.com/apps/astropy-bot . Then, click on the big green "Install"
button. You can choose to install the bot on all or select repositories
under your account or organization. It is recommended to only install it for
select repositories by start typing a repository name and let auto-completion
do the hard work for you (repeat this once per repository). Once you are done,
click "Install".

After a successful installation, you will be taken to a
``https://github.com/settings/installations/<installation-number>`` page.
This page is also accessible from your account or organization settings in
"Applications", specifically under "Installed GitHub Apps".
You can change the installation settings by clicking the "Configure"
button next to the listed app, if desired.

For Astropy, the app can be added to specific repositories
under the **Your installations** tab, by clicking on the gearbox next to
**Astropy**, which goes to
[this page](https://github.com/organizations/astropy/settings/installations/36238)
(not everyone will be able to see this).

### Configuration

The default bot configuration for astropy-bot is given in the
[pyproject.toml](pyproject.toml) file in this repository. To override these
settings and/or enable additional plugins, you can create a ``pyproject.toml``
file in your repository with the following section:

    [tool.astropy-bot]

See [Available plugins and configuration](https://baldrick.readthedocs.io/en/latest/plugins.html) for details of the
configuration for the default baldrick plugins, including how to enable/disable
plugins.

For the custom plugin which checks the changelog, the following options are
available:

    [tool.astropy-bot.changelog_checker]
    enabled = true
    filename = "CHANGES.rst"

The plugin can be enabled/disabled using the ``enabled`` setting, and the
``filename`` setting should give the name of the changelog file (which defaults
  to ``CHANGES.rst``).

### Requirements

This app requires Python 3.6 to run, and dependencies are listed in
``requirements.txt``
