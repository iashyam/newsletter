import click
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """Newsletter CLI — write in markdown, send beautifully."""
    pass


# ---------------------------------------------------------------------------
# send
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Render HTML and show a preview without sending.")
def send(markdown_file, dry_run):
    """Render MARKDOWN_FILE and send it to all active subscribers."""
    from renderer import render_markdown_to_html
    from db import get_active_subscribers
    from sender import send_newsletter

    click.echo(f"Rendering {markdown_file}...")
    html, subject, warnings = render_markdown_to_html(markdown_file)

    for w in warnings:
        click.secho(f"  ⚠  {w}", fg="yellow")

    click.echo(f"  Subject : {subject}")

    if dry_run:
        preview_path = markdown_file.replace(".md", "_preview.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html)
        click.secho(f"Dry run — preview saved to {preview_path}", fg="cyan")
        return

    subscribers = get_active_subscribers()
    if not subscribers:
        click.secho("No active subscribers found.", fg="yellow")
        return

    click.echo(f"Sending to {len(subscribers)} subscriber(s)...")
    result = send_newsletter(html, subject, subscribers)

    click.secho(f"  Sent successfully : {result['success']}", fg="green")
    if result["failed"]:
        click.secho(f"  Failed            : {len(result['failed'])}", fg="red")
        for f in result["failed"]:
            click.secho(f"    {f['email']} — {f['error']}", fg="red")


# ---------------------------------------------------------------------------
# subscribers
# ---------------------------------------------------------------------------

@cli.group()
def subscribers():
    """Manage newsletter subscribers."""
    pass


@subscribers.command("list")
def subscribers_list():
    """List all subscribers."""
    from db import list_subscribers

    subs = list_subscribers()
    if not subs:
        click.echo("No subscribers yet.")
        return

    click.echo(f"\n{'EMAIL':<35} {'NAME':<25} {'ACTIVE'}")
    click.echo("-" * 68)
    for s in subs:
        active = click.style("yes", fg="green") if s.get("active") else click.style("no", fg="red")
        click.echo(f"{s['email']:<35} {s.get('name', ''):<25} {active}")
    click.echo(f"\nTotal: {len(subs)}")


@subscribers.command("add")
@click.argument("email")
@click.option("--name", default="", help="Subscriber's name.")
def subscribers_add(email, name):
    """Add a subscriber by EMAIL."""
    from db import add_subscriber

    ok, msg = add_subscriber(email, name)
    if ok:
        click.secho(f"Added {email}", fg="green")
    else:
        click.secho(f"Skipped {email} — {msg}", fg="yellow")


@subscribers.command("remove")
@click.argument("email")
def subscribers_remove(email):
    """Remove a subscriber by EMAIL."""
    from db import remove_subscriber

    if click.confirm(f"Remove {email}?"):
        removed = remove_subscriber(email)
        if removed:
            click.secho(f"Removed {email}", fg="green")
        else:
            click.secho(f"Not found: {email}", fg="yellow")


@subscribers.command("import")
@click.argument("csv_file", type=click.Path(exists=True))
def subscribers_import(csv_file):
    """Bulk import subscribers from a CSV_FILE (Google Sheets export)."""
    from db import import_from_csv

    click.echo(f"Importing from {csv_file}...")
    added, skipped = import_from_csv(csv_file)
    click.secho(f"  Added   : {added}", fg="green")
    click.secho(f"  Skipped : {skipped}", fg="yellow")


if __name__ == "__main__":
    cli()
