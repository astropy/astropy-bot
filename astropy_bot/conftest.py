from baldrick.conftest import app  # noqa


def pytest_configure(config):
    import baldrick
    baldrick.GLOBAL_TOML = '/tmp/not-a-real-file'
