import pytest


# --- POST /login ---

def test_login_success_redirects_to_landing(client):
    response = client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123",
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_success_sets_session(client):
    with client.session_transaction() as sess:
        assert "user_id" not in sess
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123",
    })
    with client.session_transaction() as sess:
        assert sess["user_id"] is not None
        assert sess["user_name"] == "Demo User"


def test_login_wrong_password_shows_error(client):
    response = client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert b"Invalid email or password." in response.data


def test_login_wrong_password_does_not_set_session(client):
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "wrongpassword",
    })
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_login_unknown_email_shows_error(client):
    response = client.post("/login", data={
        "email": "nobody@example.com",
        "password": "anything",
    }, follow_redirects=True)
    assert b"Invalid email or password." in response.data


def test_login_unknown_email_does_not_set_session(client):
    client.post("/login", data={
        "email": "nobody@example.com",
        "password": "anything",
    })
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_login_empty_fields_shows_validation_error(client):
    response = client.post("/login", data={
        "email": "",
        "password": "",
    }, follow_redirects=True)
    assert b"All fields are required." in response.data


def test_login_empty_email_shows_validation_error(client):
    response = client.post("/login", data={
        "email": "",
        "password": "somepassword",
    }, follow_redirects=True)
    assert b"All fields are required." in response.data


def test_login_empty_password_shows_validation_error(client):
    response = client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "",
    }, follow_redirects=True)
    assert b"All fields are required." in response.data


# --- GET /logout ---

def test_logout_while_logged_in_redirects_to_landing(client):
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123",
    })
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_while_logged_in_clears_session(client):
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123",
    })
    client.get("/logout")
    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_name" not in sess


def test_logout_while_not_logged_in_redirects_to_landing(client):
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_while_not_logged_in_does_not_error(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


# --- Auth guards ---

def test_login_page_redirects_when_already_logged_in(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_register_page_redirects_when_already_logged_in(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/register", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


# --- Nav link changes ---

def test_nav_shows_signin_when_not_logged_in(client):
    response = client.get("/")
    assert b"Sign in" in response.data
    assert b"Get started" in response.data
    assert b"Sign out" not in response.data


def test_nav_shows_signout_when_logged_in(client):
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123",
    })
    response = client.get("/")
    assert b"Sign out" in response.data
    assert b"Demo User" in response.data
