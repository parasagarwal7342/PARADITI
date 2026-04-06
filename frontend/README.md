# P Λ R Λ D I T I - Frontend

Static web UI for the P Λ R Λ D I T I (परादिति) government scheme recommender.

**Founder:** PARAS AGRAWAL

## Files

| File | Purpose |
|------|--------|
| `index.html` | Landing page; links to login/register |
| `login.html` | Login form; submits to `/api/login` |
| `register.html` | Registration + profile (age, state, income, category, occupation) |
| `dashboard.html` | Logged-in dashboard: Aditi AI Assistant, Smart Document Hub, Life Journey Timeline, Recommendations, Profile Modal |
| `styles.css` | Global styles (layout, navbar, cards, forms, modals) |
| `app.js` | API base URL, token in `localStorage`, auth check on dashboard, form handlers, scheme load/display, modals |

## Usage

The backend serves these files from `frontend/` at `http://localhost:5000`. Open the app in a browser; no build step required.

## API

All requests use `Authorization: Bearer <token>` for protected routes. Base URL is set in `app.js` (e.g. `http://localhost:5000/api`).
