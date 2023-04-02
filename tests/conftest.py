import pytest
from app import app


@pytest.fixture()
def app_test():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def web_client(app_test):
    return app_test.test_client()


@pytest.fixture()
def runner(app_test):
    return app_test.test_cli_runner()
