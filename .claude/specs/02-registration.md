# Spec: Registration

## Overview
Implement user registration for Spendly. The `GET /register` route already renders the form shell; this step wires up `POST /register` to validate input, hash the password, insert the user into the database. On success the user is shown with a success message and redirect to the login page. It also sets up Flask's secret key and session infrastructure that all subsequent authenticated steps depend on.

## Depends on
- Step 01: Database setup — `users` table and `get_db()` must exist.

## Routes
- `POST /register` — processes registration form, creates user, redirects to `/login` on success — public

## Database changes
No new tables or columns. The `users` table from Step 01 already has all required columns (`name`, `email`, `password_hash`, `created_at`).

One new DB helper is needed:
- `create_user(name, email, password)` — inserts a row into `users`, returns the new `id`, raises `sqlite3.IntegrityError` on duplicate email.

## Templates
- **Modify:** `templates/register.html` — add `method="POST"` and `action="{{ url_for('register') }}"` to the form; add `name` attributes to all inputs; display flashed error/success messages.

## Files to change
- `app.py` — add `POST` method to `/register` route; import `flash`, `redirect`, `request`, `session`, `url_for`; set `app.secret_key`.
- `database/db.py` — add `create_user()` helper.
- `templates/register.html` — wire up the form and flash message display.

## Files to create
None.

## New dependencies
No new pip packages. Uses `werkzeug.security.generate_password_hash` (already installed).

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only.
- Parameterised queries only — never f-strings in SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext.
- `app.secret_key` must be set before any session or flash usage; use a hard-coded dev string for now (e.g. `"dev-secret-change-in-prod"`).
- All templates extend `base.html`.
- Use CSS variables — never hardcode hex values in new styles.
- Duplicate email must return a flashed error message, not a 500.
- Empty name, email, or password must return a flashed validation error.
- Password and confirm-password mismatch must return a flashed error.
- On success, redirect to `url_for('login')` with a flashed success message — do not log the user in yet (session login is Step 3).
- Use `abort()` for unexpected HTTP errors, not bare string returns.
- Do not implement any stub route that is not part of this step.

## Definition of done
- [ ] Submitting the registration form with valid data creates a new row in `users` with a hashed password.
- [ ] Registering with an email that already exists shows a flashed error and does not insert a duplicate row.
- [ ] Submitting with any empty field shows a flashed validation error.
- [ ] Submitting with mismatched passwords shows a flashed error.
- [ ] Successful registration redirects to `/login` with a success flash message visible.
- [ ] The demo user seeded in Step 01 (`demo@spendly.com`) can still log in after this step (no data corruption).
- [ ] App starts without errors (`python app.py`).
- [ ] All SQL in `create_user()` uses `?` placeholders — no string formatting.
