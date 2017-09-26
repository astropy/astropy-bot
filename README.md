About
=====

This is a GitHub app written using Flask for the Astropy project which can be
installed via GitHub integrations. This includes the following functionality:

* Check pull requests whenever they are changed to make sure the changelog
  is consistent with the milestone and the labels. This behavior is defined
  in ``changebot.blueprints.pull_request_checker``.

* Check issues labelled as 'Close?' to see whether any of them are 'stale' and
  could be closed, and either warn that the issue will be closed soon, or
  close it if a warning has already been posted in the past. This is intended to
  be run as a cron job.

* Check pull requests that haven't had any commits recently are automatically
  closed (with a warning period) after a certain amount of time. This is
  intended to be run as a cron job.

This requires Python 3.6 to run.

Dependencies are listed in ``requirements.txt``
