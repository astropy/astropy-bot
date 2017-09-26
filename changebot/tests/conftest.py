import os

os.environ['GITHUB_APP_INTEGRATION_ID'] = '1234'
os.environ['GITHUB_APP_PRIVATE_KEY'] = 'ABCD'
os.environ['CRON_TOKEN'] = 'XYZ'
os.environ['STALE_ISSUE_CLOSE'] = 'TRUE'
os.environ['STALE_ISSUE_CLOSE_SECONDS'] = '120'
os.environ['STALE_ISSUE_WARN_SECONDS'] = '60'
os.environ['STALE_PRS_CLOSE'] = 'TRUE'
os.environ['STALE_PRS_CLOSE_SECONDS'] = '120'
os.environ['STALE_PRS_WARN_SECONDS'] = '60'
