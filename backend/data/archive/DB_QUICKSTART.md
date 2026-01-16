# DB + Alembic Quickstart (Source of Truth)

This project uses **PostgreSQL** and **Alembic** migrations.

## 1) Configure DB

Set `DATABASE_URL` in environment (recommended):

- `DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>`

If not set, the default from `backend/config/settings.py` is used.

## 2) Run migrations

Use the repo's venv python:

- `/Users/kunalranjan/edtech/question-generator/backend/venv/bin/python3 -m alembic upgrade head`

## 3) Import the Chapter 5 YAML bank into Postgres

This converts YAML (authoring format) into `question_bank_items` (runtime format).

- `/Users/kunalranjan/edtech/question-generator/backend/venv/bin/python3 -m tools.import_question_bank --yaml backend/data/class5_chapter5_bank.yaml --chapter factors_multiples`

## Tables introduced (Option A)

- `question_bank_items`: pre-generated question payloads (what SessionAdapter serves)
- `served_questions`: tracking of items served/answered per session
- `quiz_sessions`: SessionAdapter sessions persisted in DB
