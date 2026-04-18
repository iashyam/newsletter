import re
from datetime import datetime
from pathlib import Path

import markdown
from premailer import transform

from src.core.config import settings
from src.core.exceptions import MarkdownFileError, ImageNotFoundError
from src.modules.newsletter.schema import RenderedNewsletter
from src.services import s3_service

_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<style>
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
  .wrapper {{
    width: 100%;
    background-color: #f4f4f5;
    padding: 40px 16px;
    box-sizing: border-box;
  }}
  .card {{
    max-width: 600px;
    margin: 0 auto;
    background-color: #ffffff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
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
  .body {{
    padding: 40px;
  }}
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
  .body img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
    margin: 24px auto;
  }}
  .divider {{
    height: 1px;
    background-color: #e4e4e7;
    margin: 0 40px;
  }}
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
  @media only screen and (max-width: 600px) {{
    /* Full-width, edge-to-edge on mobile */
    .wrapper {{ padding: 0; }}
    .card {{ border-radius: 0; box-shadow: none; }}

    /* Tighter but still breathable padding */
    .header {{ padding: 20px 16px; }}
    .body {{ padding: 24px 16px; }}
    .footer {{ padding: 16px; }}
    .divider {{ margin: 0; }}

    /* Slightly smaller headings */
    .body h1 {{ font-size: 21px; }}
    .body h2 {{ font-size: 17px; margin-top: 24px; }}
    .body h3 {{ font-size: 15px; margin-top: 20px; }}

    /* Tighter paragraph and list spacing to reduce scroll */
    .body p {{ margin-bottom: 14px; }}
    .body ul, .body ol {{ margin-bottom: 14px; }}
    .body li {{ margin-bottom: 4px; }}
    .body hr {{ margin: 24px 0; }}

    /* Images full-width, no side margin */
    .body img {{ margin: 16px 0; border-radius: 6px; width: 100%; }}
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


def _resolve_images(md_content: str, md_dir: Path, newsletter_date: str) -> tuple[str, list[str]]:
    """Replace local image paths with S3 URLs. Returns (updated_content, warnings)."""
    warnings = []

    def replace(match):
        alt, src = match.group(1), match.group(2)
        if src.startswith(("http://", "https://")):
            return match.group(0)

        local_path = md_dir / src
        if not local_path.exists():
            warnings.append(ImageNotFoundError(src).message)
            return match.group(0)

        try:
            url = s3_service.upload_image(str(local_path), newsletter_date)
            return f"![{alt}]({url})"
        except Exception as e:
            warnings.append(str(e))
            return match.group(0)

    updated = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, md_content)
    return updated, warnings


def render(md_file_path: str) -> RenderedNewsletter:
    """Render a markdown file to a full HTML email."""
    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except OSError as e:
        raise MarkdownFileError(md_file_path, str(e))

    newsletter_date = datetime.now().strftime("%Y-%m-%d")
    md_content, warnings = _resolve_images(md_content, Path(md_file_path).parent, newsletter_date)

    subject = "Newsletter"
    h1_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if h1_match:
        subject = h1_match.group(1).strip()

    html_content = markdown.markdown(md_content, extensions=["extra", "codehilite", "nl2br"])

    full_html = _EMAIL_TEMPLATE.format(
        title=subject,
        newsletter_name=settings.from_name,
        date=datetime.now().strftime("%B %d, %Y"),
        content=html_content,
    )

    return RenderedNewsletter(
        html=transform(full_html),
        subject=subject,
        warnings=warnings,
    )
