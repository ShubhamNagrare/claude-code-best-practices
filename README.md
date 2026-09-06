# Spend Tracker

A simple expense tracking web app built with FastAPI, SQLModel (SQLite), and Jinja2 templates. Includes a login/register flow and a dashboard for adding, listing, and summarizing expenses.

## Features

- Login page with session-based auth (static demo credentials)
- Register page (demo only — points back to the static account)
- Dashboard to add, list, delete expenses and view spend summary by category
- REST API (`/expenses`, `/summary`) backed by SQLite via SQLModel

## Demo Credentials

- **Username:** `username`
- **Password:** `password`

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management, with dependencies declared in `pyproject.toml` and pinned in `uv.lock`.

```powershell
# Create the venv and install dependencies from uv.lock
uv sync

# Activate the virtual environment
.venv\Scripts\activate
```

## Run

```powershell
uv run uvicorn main:app --reload
```

Then open http://127.0.0.1:8000 in your browser — you'll be redirected to the login page.

## Project Structure

```
main.py              # FastAPI app: auth routes, dashboard, expense API
templates/           # Jinja2 templates (login, register, dashboard)
static/style.css     # App styling
pyproject.toml       # Project metadata and dependencies
uv.lock              # Locked dependency versions
```

## API Endpoints

| Method | Path              | Description                       |
|--------|-------------------|------------------------------------|
| GET    | /login            | Login page                         |
| POST   | /login            | Authenticate                       |
| GET    | /register         | Register page                      |
| POST   | /register         | Register (demo, static account)    |
| GET    | /logout           | Clear session                      |
| GET    | /dashboard        | Dashboard UI (requires login)      |
| POST   | /expenses         | Create an expense                  |
| GET    | /expenses         | List expenses                      |
| GET    | /expenses/{id}    | Get a single expense               |
| PUT    | /expenses/{id}    | Update an expense                  |
| DELETE | /expenses/{id}    | Delete an expense                  |
| GET    | /summary          | Total spend + breakdown by category|
