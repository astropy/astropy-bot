import os
import sys

from baldrick import create_app

# Configure the app
app = create_app('astropy-bot')

# Load plugins from baldrick
import baldrick.plugins.github_milestones  # noqa

# Load astropy-specific plugins
import astropy_bot.changelog_checker  # noqa

# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))

if '--skip-run' not in sys.argv:
    app.run(host='0.0.0.0', port=port, debug=False)
