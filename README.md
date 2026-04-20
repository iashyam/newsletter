# Newsletter CLI

A simple CLI to write newsletters in markdown and send them beautifully to subscribers via [Resend](https://resend.com). Subscribers are stored in MongoDB. Images are auto-uploaded to S3.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
```

### `.env` variables

| Variable | Description |
|---|---|
| `RESEND_API_KEY` | Your Resend API key |
| `FROM_EMAIL` | Sender email (must be verified in Resend) |
| `FROM_NAME` | Sender name shown in inbox |
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB` | Database name (default: `newsletter`) |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 image uploads |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 image uploads |
| `AWS_REGION` | S3 bucket region |
| `S3_BUCKET` | S3 bucket name |
| `S3_PUBLIC_BASE_URL` | Public base URL for the bucket |

### Docker deployment

The project includes a `Dockerfile` and `docker-compose.yml` for easy deployment. Use the provided `Makefile` to manage the container:

```bash
make build   # Build the image
make up      # Start the container in background
make logs    # Tail the logs
make down    # Stop the container
```

The web interface is available at `http://localhost:8000`.

## Usage

### Send a newsletter

```bash
python cli.py send my-newsletter.md
```

Local images in your markdown (e.g. `![alt](./images/photo.jpg)`) are automatically uploaded to S3 and replaced with public URLs before sending.

**Preview before sending:**

```bash
python cli.py send my-newsletter.md --dry-run
```

Saves a `_preview.html` file next to your markdown file. Open it in a browser to check how it looks on mobile before sending.

### Manage subscribers

```bash
# List all subscribers
python cli.py subscribers list

# Add a subscriber
python cli.py subscribers add someone@example.com
python cli.py subscribers add someone@example.com --name "Jane Doe"

# Remove a subscriber
python cli.py subscribers remove someone@example.com

# Bulk import from a Google Sheets CSV export
python cli.py subscribers import subscribers.csv
```

The CSV import auto-detects common column name formats from Google Forms (`Email`, `Email Address`, `Name`, `Full Name`, etc.).

## Writing newsletters

Write your newsletter as a standard markdown file. The first `# H1` heading becomes the email subject line.

```markdown
# My Newsletter — April 2024

Hello everyone!

Here's what's new this month...

## Section One

Some content with **bold**, _italic_, and [links](https://example.com).

![A photo](./images/photo.jpg)
```

## S3 image organization

Images are uploaded to `newsletters/YYYY-MM-DD/filename` in your S3 bucket. The bucket must allow public read access on objects.
