# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

CLI tool: write newsletters in Markdown, send to subscribers via Resend. Images auto-uploaded to S3. Subscribers stored in MongoDB.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in credentials
```

## Commands

```bash
# Preview newsletter (renders HTML, no emails sent)
python cli.py send sample/april-2026.md --dry-run

# Send newsletter to all active subscribers
python cli.py send sample/april-2026.md

# Subscriber management
python cli.py subscribers list
python cli.py subscribers add user@example.com --name "Jane"
python cli.py subscribers remove user@example.com
python cli.py subscribers import subscribers.csv
```

No test suite or linting config exists.

## Architecture

```
cli.py  →  src/modules/{newsletter,subscribers}/service.py
                ↓
        src/services/{renderer,email,s3}_service.py
                ↓
        Resend API / MongoDB / AWS S3
```

**Rendering pipeline** (`renderer_service.py`):
1. Read markdown file
2. Extract H1 as email subject (regex)
3. Find local image paths → upload to S3 → replace with public URLs
4. Convert markdown → HTML (`markdown` lib with extra/codehilite/nl2br)
5. Wrap in `_EMAIL_TEMPLATE` (inline CSS via `premailer`)

**Send pipeline** (`newsletter/service.py`):
1. Call `renderer_service.render()` → `RenderedNewsletter`
2. Fetch active subscribers from MongoDB
3. Personalize unsubscribe link per recipient
4. Call `email_service.send_email()` per subscriber
5. Return `SendResult` (success count + `FailedDelivery` list)

**Dry-run** saves `{filename}_preview.html` alongside the markdown file.

## Key Design Decisions

- `src/core/config.py`: Pydantic Settings singleton — fails fast if required env vars missing
- `src/core/exceptions.py`: Custom exception hierarchy; `cli.py` catches `AppException` and exits cleanly
- Subscriber emails are lowercased on insert
- CSV import auto-detects email/name columns (handles Google Forms exports)
- S3 uploads organized as `newsletters/YYYY-MM-DD/filename`

## Required Environment Variables

| Variable | Purpose |
|---|---|
| `RESEND_API_KEY` | Email delivery |
| `FROM_EMAIL` | Sender (must be verified in Resend) |
| `MONGODB_URI` | MongoDB connection |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 credentials |
| `S3_BUCKET` | S3 bucket name |
| `S3_PUBLIC_BASE_URL` | Public URL prefix for uploaded images |
