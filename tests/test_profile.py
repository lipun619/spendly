import pytest


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _login(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})


# ------------------------------------------------------------------ #
# GET /profile — unauthenticated                                      #
# ------------------------------------------------------------------ #

def test_profile_redirects_when_not_logged_in(client):
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_redirect_follows_to_login_page(client):
    response = client.get("/profile", follow_redirects=True)
    assert b"Sign in" in response.data


# ------------------------------------------------------------------ #
# GET /profile — authenticated                                        #
# ------------------------------------------------------------------ #

def test_profile_returns_200_when_logged_in(client):
    _login(client)
    response = client.get("/profile")
    assert response.status_code == 200


def test_profile_shows_user_name(client):
    _login(client)
    response = client.get("/profile")
    assert b"Demo User" in response.data


def test_profile_shows_user_email(client):
    _login(client)
    response = client.get("/profile")
    assert b"demo@spendly.com" in response.data


def test_profile_shows_member_since(client):
    _login(client)
    response = client.get("/profile")
    months = [b"January", b"February", b"March", b"April", b"May", b"June",
              b"July", b"August", b"September", b"October", b"November", b"December"]
    assert any(m in response.data for m in months)


def test_profile_shows_avatar_initials(client):
    _login(client)
    response = client.get("/profile")
    assert b"DU" in response.data


def test_profile_shows_currency_prefix(client):
    _login(client)
    response = client.get("/profile")
    assert "₹".encode() in response.data


def test_profile_shows_expenses_logged_label(client):
    _login(client)
    response = client.get("/profile")
    assert b"Expenses Logged" in response.data


def test_profile_shows_top_category(client):
    _login(client)
    response = client.get("/profile")
    assert b"Top Category" in response.data
    # Seeded data: Shopping has the highest total (2500)
    assert b"Shopping" in response.data


def test_profile_does_not_expose_password_hash(client):
    _login(client)
    response = client.get("/profile")
    assert b"password_hash" not in response.data
    assert b"pbkdf2" not in response.data
    assert b"scrypt" not in response.data


# ------------------------------------------------------------------ #
# Session injection                                                   #
# ------------------------------------------------------------------ #

def test_profile_with_injected_valid_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Demo User" in response.data


def test_profile_returns_404_for_nonexistent_user_id(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 999999
    response = client.get("/profile")
    assert response.status_code == 404


# ------------------------------------------------------------------ #
# Nav link in base.html                                               #
# ------------------------------------------------------------------ #

def test_nav_username_links_to_profile_when_logged_in(client):
    _login(client)
    response = client.get("/")
    assert b'href="/profile"' in response.data


def test_nav_username_not_present_when_logged_out(client):
    response = client.get("/")
    assert b'href="/profile"' not in response.data
