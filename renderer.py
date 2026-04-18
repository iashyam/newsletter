import os
import re
import boto3
from datetime import datetime
from pathlib import Path
import markdown
from premailer import transform
from dotenv import load_dotenv

load_dotenv()

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<style>
  /* Reset */
  body, table, td, p, a, li, blockquote {{
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
  }}
  body {{
    margin: 0;
    padding: 0;
    background-color: #f4f4f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1a1a1a;
  }}

  /* Wrapper */
  .wrapper {{
    width: 100%;
    background-color: #f4f4f5;
    padding: 40px 16px;
    box-sizing: border-box;
  }}

  /* Card */
  .card {{
    max-width: 600px;
    margin: 0 auto;
    background-color: #ffffff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}

  /* Header */
  .header {{
    background-color: #18181b;
    padding: 32px 40px;
    text-align: center;
  }}
  .header h1 {{
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
  }}
  .header p {{
    margin: 6px 0 0;
    font-size: 13px;
    color: #a1a1aa;
  }}

  /* Body */
  .body {{
    padding: 40px;
  }}

  /* Typography */
  .body h1 {{
    font-size: 26px;
    font-weight: 700;
    color: #18181b;
    margin: 0 0 8px;
    line-height: 1.3;
    letter-spacing: -0.5px;
  }}
  .body h2 {{
    font-size: 20px;
    font-weight: 600;
    color: #18181b;
    margin: 36px 0 10px;
    letter-spacing: -0.3px;
  }}
  .body h3 {{
    font-size: 17px;
    font-weight: 600;
    color: #18181b;
    margin: 28px 0 8px;
  }}
  .body p {{
    font-size: 16px;
    line-height: 1.7;
    color: #3f3f46;
    margin: 0 0 20px;
  }}
  .body a {{
    color: #7c3aed;
    text-decoration: underline;
  }}
  .body ul, .body ol {{
    font-size: 16px;
    line-height: 1.7;
    color: #3f3f46;
    padding-left: 24px;
    margin: 0 0 20px;
  }}
  .body li {{
    margin-bottom: 8px;
  }}
  .body blockquote {{
    border-left: 4px solid #e4e4e7;
    margin: 0 0 20px;
    padding: 12px 20px;
    background-color: #fafafa;
    border-radius: 0 6px 6px 0;
  }}
  .body blockquote p {{
    margin: 0;
    color: #71717a;
    font-style: italic;
  }}
  .body code {{
    background-color: #f4f4f5;
    border: 1px solid #e4e4e7;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 14px;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    color: #be185d;
  }}
  .body pre {{
    background-color: #18181b;
    border-radius: 8px;
    padding: 20px;
    overflow-x: auto;
    margin: 0 0 20px;
  }}
  .body pre code {{
    background: none;
    border: none;
    padding: 0;
    color: #e4e4e7;
    font-size: 14px;
  }}
  .body hr {{
    border: none;
    border-top: 1px solid #e4e4e7;
    margin: 36px 0;
  }}

  /* Images */
  .body img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
    margin: 24px auto;
  }}

  /* Divider */
  .divider {{
    height: 1px;
    background-color: #e4e4e7;
    margin: 0 40px;
  }}

  /* Footer */
  .footer {{
    padding: 28px 40px;
    text-align: center;
  }}
  .footer p {{
    font-size: 13px;
    color: #a1a1aa;
    margin: 0 0 6px;
  }}
  .footer a {{
    color: #7c3aed;
    text-decoration: none;
  }}

  /* Mobile */
  @media only screen and (max-width: 600px) {{
    .wrapper {{ padding: 16px 8px; }}
    .header {{ padding: 24px 20px; }}
    .body {{ padding: 28px 20px; }}
    .body h1 {{ font-size: 22px; }}
    .body h2 {{ font-size: 18px; }}
    .footer {{ padding: 20px; }}
    .divider {{ margin: 0 20px; }}
  }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <h1>{newsletter_name}</h1>
      <p>{date}</p>
    </div>
    <div class="body">
      {content}
    </div>
    <div class="divider"></div>
    <div class="footer">
      <p>You're receiving this because you subscribed to {newsletter_name}.</p>
      <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
    </div>
  </div>
</div>
</body>
</html>
"""


def upload_image_to_s3(local_path: str, newsletter_date: str) -> str:
    s3 = boto3.client(
        "s3",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    bucket = os.environ["S3_BUCKET"]
    base_url = os.environ["S3_PUBLIC_BASE_URL"].rstrip("/")

    filename = Path(local_path).name
    key = f"newsletters/{newsletter_date}/{filename}"

    content_type = "image/jpeg"
    ext = Path(local_path).suffix.lower()
    if ext == ".png":
        content_type = "image/png"
    elif ext in (".gif",):
        content_type = "image/gif"
    elif ext in (".webp",):
        content_type = "image/webp"

    s3.upload_file(
        local_path,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{base_url}/{key}"


def resolve_images(md_content: str, md_file_path: str, newsletter_date: str):
    """
    Find all local image references in markdown, upload to S3, replace with URLs.
    Returns (updated_md_content, list of warnings).
    """
    md_dir = Path(md_file_path).parent
    warnings = []

    def replace_image(match):
        alt = match.group(1)
        src = match.group(2)

        # Skip already-hosted images
        if src.startswith("http://") or src.startswith("https://"):
            return match.group(0)

        local_path = md_dir / src
        if not local_path.exists():
            warnings.append(f"Image not found, skipping: {src}")
            return match.group(0)

        try:
            url = upload_image_to_s3(str(local_path), newsletter_date)
            return f"![{alt}]({url})"
        except Exception as e:
            warnings.append(f"Failed to upload {src}: {e}")
            return match.group(0)

    updated = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, md_content)
    return updated, warnings


def render_markdown_to_html(md_file_path: str) -> tuple[str, str, list[str]]:
    """
    Renders a markdown file to a full HTML email.
    Returns (html, subject_line, warnings).
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    newsletter_date = datetime.now().strftime("%Y-%m-%d")

    # Upload local images to S3
    md_content, warnings = resolve_images(md_content, md_file_path, newsletter_date)

    # Extract subject from first H1
    subject = "Newsletter"
    h1_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if h1_match:
        subject = h1_match.group(1).strip()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=["extra", "codehilite", "nl2br"],
    )

    newsletter_name = os.environ.get("FROM_NAME", "Newsletter")
    date_display = datetime.now().strftime("%B %d, %Y")

    full_html = EMAIL_TEMPLATE.format(
        title=subject,
        newsletter_name=newsletter_name,
        date=date_display,
        content=html_content,
    )

    # Inline CSS for better email client compatibility
    full_html = transform(full_html)

    return full_html, subject, warnings
