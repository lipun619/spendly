# Spec: Profile Page Design

## Overview
Implement the `/profile` route for Spendly, replacing the current raw-string stub with a fully-designed, login-protected page. The profile page gives users a single place to see their account identity (name, email, member since) alongside a quick financial summary (total spent this month, all-time expense count, and top spending category). This is the first authenticated-only page in the app, establishing the pattern — redirect unauthenticated visitors to `/login` — that all future protected routes (`/expenses/add`, etc.) will follow.

## Depends on
- Step 01: Database setup — `users` and `expenses` tables, `get_db()` must exist.
- Step 02: Registration — `users` rows must exist with `name`, `email`, `created_at`.
- Step 03: Login and Logout — `session['user_id']` set on login; route must redirect to `/login` if not present.

## Routes
- `GET /profile` — fetches logged-in user's profile and expense stats, renders `profile.html` — logged-in only (redirect to `/login` if `session.get('user_id')` is falsy)

## Database changes
No new tables or columns. Two new DB helpers are needed:

- `get_user_by_id(user_id)` — queries `users` by `id`, returns a `sqlite3.Row` with `id`, `name`, `email`, `created_at` or `None` if not found.
- `get_user_stats(user_id)` — returns a plain `dict` with:
  - `total_this_month` (REAL) — sum of `amount` for the current calendar month; `0.0` if no expenses
  - `total_all_time` (REAL) — sum of all `amount` for the user; `0.0` if no expenses
  - `expense_count` (INTEGER) — total number of expense rows
  - `top_category` (TEXT or None) — category with the highest total amount; `None` if no expenses

## Templates
- **Create:** `templates/profile.html` — extends `base.html`, renders the profile page (see layout below)
- **Modify:** `templates/base.html` — wrap the `session.get('user_name')` username in the navbar inside an `<a href="{{ url_for('profile') }}">` so it acts as a nav link to the profile page

### Profile page layout
The page uses a two-zone layout:

1. **Profile header card** — full-width card at the top:
   - Avatar circle: a `<div>` showing the user's initials (first letter of first name + first letter of last name, or just first two letters of name if single-word), styled as a large circle with `--accent` background and white text
   - User's full name (DM Serif Display heading)
   - Email address (muted, with a small envelope icon)
   - "Member since" date formatted as `Month YYYY` (e.g. `April 2026`)

2. **Stats grid** — three stat cards below the header:
   - "This month" — `₹ X,XXX` total spent (tabular-nums)
   - "All time" — `₹ X,XXX` total spent
   - "Expenses logged" — count of expense records
   - "Top category" — name of highest-spend category or `—` if none

## Files to change
- `app.py` — implement `/profile` route: guard with session check, call `get_user_by_id` and `get_user_stats`, pass results to template.
- `database/db.py` — add `get_user_by_id(user_id)` and `get_user_stats(user_id)` helpers.
- `templates/base.html` — wrap nav username in a profile link.

## Files to create
- `templates/profile.html` — profile page template.
- `static/css/profile.css` — page-scoped styles (`.profile-*` prefix only).

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only.
- Parameterised queries only — never f-strings in SQL.
- Passwords hashed with `werkzeug` — not relevant here but never expose `password_hash` to the template.
- Use CSS variables — never hardcode hex values in `profile.css`; reference existing tokens (`--ink`, `--accent`, `--paper-card`, `--border`, etc.).
- All templates extend `base.html`.
- The `/profile` route must redirect to `url_for('login')` (with `abort` not used here — a redirect is correct UX for auth gates).
- `get_user_by_id` must call `abort(404)` in the route if it returns `None` (defensive guard against a stale session referencing a deleted user).
- `get_user_stats` must never raise — use `COALESCE` or Python fallbacks so missing data returns `0.0` / `None` cleanly.
- Avatar initials: derive in the Jinja2 template using `user.name.split()` — do not compute in Python.
- Currency display: always prefix amounts with `₹` and use `font-variant-numeric: tabular-nums`.
- `profile.css` must be linked via `{% block head %}` in `profile.html` using `url_for('static', ...)` — never inline `<style>`.
- Stat cards reuse `.feature-card` structural shape (white card, `--border`, `--radius-md`) — add only what's new in `profile.css`.
- Do not implement any other stub route as part of this step.

## Definition of done
- [ ] Visiting `/profile` while not logged in redirects to `/login`.
- [ ] Visiting `/profile` while logged in renders the page without errors.
- [ ] The profile header shows the correct name, email, and member-since month/year from the database.
- [ ] The avatar circle shows the correct initials for the logged-in user.
- [ ] "This month" stat reflects the sum of the current month's expenses for that user (₹ prefix, tabular-nums).
- [ ] "All time" stat reflects the sum of all expenses for that user.
- [ ] "Expenses logged" stat shows the correct count.
- [ ] "Top category" shows the correct highest-spend category name, or `—` when the user has no expenses.
- [ ] The nav username in `base.html` is now a clickable link to `/profile`.
- [ ] `get_user_by_id` and `get_user_stats` use `?` placeholders — no string formatting in SQL.
- [ ] No `password_hash` value is passed to or rendered in any template.
- [ ] `profile.css` contains no hardcoded hex values — CSS variables only.
- [ ] App starts without errors (`python app.py`).
