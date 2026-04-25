# Spec: Login and Logout

## Overview
Implement session-based login and logout for Spendly. The `GET /login` route already renders the form shell; this step wires up `POST /login` to verify credentials against the database and store the authenticated user's ID in Flask's server-side session. `GET /logout` clears the session and redirects to the landing page. After this step, every subsequent feature can gate access by checking `session.get("user_id")`. The nav bar in `base.html` is also updated to show a contextual "Sign out" link for logged-in users instead of the static "Sign in / Get started" pair.

## Depends on
- Step 01: Database setup — `users` table, `get_db()`, `init_db()`, `seed_db()` must exist.
- Step 02: Registration — `create_user()` and the `password_hash` column must exist; at least the demo user must be present in the DB.

## Routes
- `POST /login` — validates email + password, writes `user_id` and `user_name` to session, redirects to `/` on success — public
- `GET /logout` — clears session, redirects to `url_for('landing')` — public (safe to hit even when not logged in)

Note: `GET /login` already exists; only the `POST` handler is new.

## Database changes
No new tables or columns. One new DB helper is needed:

- `get_user_by_email(email)` — queries `users` by email, returns a `sqlite3.Row` (with `id`, `name`, `email`, `password_hash`) or `None` if not found.

## Templates
- **Modify:** `templates/login.html`
  - Change `action="/login"` to `action="{{ url_for('login') }}"` (uses `url_for`, not hardcoded path).
  - Replace the `{% if error %}` block with Flask's `get_flashed_messages()` pattern (consistent with `register.html`).
- **Modify:** `templates/base.html`
  - Nav links section: when `session.get('user_id')` is truthy, show the user's name and a "Sign out" link (`url_for('logout')`); otherwise show the existing "Sign in" and "Get started" links.

## Files to change
- `app.py` — add `POST` method to `/login` route with credential verification; implement `/logout` route (replace stub).
- `database/db.py` — add `get_user_by_email(email)` helper.
- `templates/login.html` — fix `action` attribute; switch error display to flash messages.
- `templates/base.html` — conditional nav links based on session state.

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.check_password_hash` (already installed via werkzeug).

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only.
- Parameterised queries only — never f-strings in SQL.
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext.
- Store only `user_id` (int) and `user_name` (str) in `session` — never store the password hash or the full Row object.
- `GET /logout` must call `session.clear()` (not `session.pop` per-key) so all session data is wiped in one call.
- `GET /logout` must redirect to `url_for('landing')` — never render a template.
- Invalid credentials (wrong email OR wrong password) must show a single, generic flashed error: "Invalid email or password." — do not reveal which field was wrong.
- All templates extend `base.html`.
- Use CSS variables — never hardcode hex values in new styles.
- Use `abort()` for unexpected HTTP errors, not bare string returns.
- Do not implement any stub route that is not part of this step (profile, add/edit/delete expense remain stubs).

## Definition of done
- [ ] Submitting the login form with the demo user credentials (`demo@spendly.com` / `demo123`) redirects to `/` and the nav shows "Sign out".
- [ ] Submitting with a valid email but wrong password shows "Invalid email or password." and does not set a session.
- [ ] Submitting with an unknown email shows "Invalid email or password." and does not set a session.
- [ ] Submitting with empty fields shows a validation error and does not attempt a DB lookup.
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/`.
- [ ] Visiting `/logout` while not logged in also redirects to `/` without error.
- [ ] The nav in `base.html` shows "Sign in" + "Get started" for unauthenticated visitors, and the user's name + "Sign out" for authenticated users.
- [ ] `login.html` uses `url_for('login')` in the form action — no hardcoded `/login`.
- [ ] `get_user_by_email()` uses a `?` placeholder — no string formatting in SQL.
- [ ] App starts without errors (`python app.py`).
