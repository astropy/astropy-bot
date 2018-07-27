import os
import re
import sys

from baldrick import create_app

# Configure the app
app = create_app('giles-dev')

# Load plugins from baldrick
import baldrick.plugins.github_milestones  # noqa

# Load astropy-specific plugins
import astropy_bot.changelog_checker  # noqa

# Define skipping of pull request checks based on labels
app.pull_requests_default = {}

app.pull_requests_default['skip_labels'] = ['Experimental', 'Work in progress']

app.pull_requests_default['skip_message_default'] = re.sub('(\w+)\n', r'\1', """
Hi there @{user} :wave: - thanks for the pull request! I'm just a friendly
:robot: that checks for issues related to the changelog and making sure that
this pull request is milestoned and labeled correctly. I see this pull request
is labelled as being experimental/a work in progress. I'll report back once this
PR is no longer labelled as such.
""").strip()

app.pull_requests_default['all_passed_message'] = re.sub('(\w+)\n', r'\1',"""
Hi there @{user} :wave: - thanks for the pull request! I'm just a friendly
:robot: that checks for issues related to the changelog and making sure that
this pull request is milestoned and labeled correctly. Everything looks good
from my point of view! :+1:.
""").strip()

app.pull_requests_default['fail_prologue'] = re.sub('(\w+)\n', r'\1',"""
Hi there @{user} :wave: - thanks for the pull request! I'm just a friendly
:robot: that checks for issues related to the changelog and making sure that
this pull request is milestoned and labeled correctly. This is mainly intended
for the maintainers, so if you are not a maintainer you can ignore this, and a
maintainer will let you know if any action is required on your part :smiley:.

I noticed the following issues with this pull request:
""").strip() + os.linesep + os.linesep

app.pull_requests_default['fail_epilogue'] = os.linesep * 2 + re.sub('(\w+)\n', r'\1', """
*If there are any issues with this message, please report them
 [here](https://github.com/astropy/astropy-bot/issues).*
""").strip()

app.pull_requests_default['pull_request_substring'] = "issues related to the changelog"

# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))

if '--skip-run' not in sys.argv:
    app.run(host='0.0.0.0', port=port, debug=False)
