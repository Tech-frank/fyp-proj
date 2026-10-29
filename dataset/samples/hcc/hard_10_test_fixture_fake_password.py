# test_login.py
import pytest

from accounts.service import authenticate

TEST_PASSWORD = "not-a-real-password-123"


@pytest.fixture
def user(db_session):
    return db_session.create_user("alice@example.com", TEST_PASSWORD)


def test_login_succeeds(user):
    assert authenticate("alice@example.com", TEST_PASSWORD)
