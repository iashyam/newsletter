#!.venv/bin/python


import sys
import functools

import click

from src.core.exceptions import AppException


def handle_errors(f):
    """Decorator that catches AppException and exits cleanly instead of showing a traceback."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppException as e:
            click.secho(f"Error: {e.message}", fg="red", err=True)
            sys.exit(1)
    return wrapper


@click.group()
def cli():
    """Newsletter CLI — write in markdown, send beautifully."""
    pass


# ---------------------------------------------------------------------------
# send
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Render and save a preview HTML without sending.")
@handle_errors
def send(markdown_file, dry_run):
    """Render MARKDOWN_FILE and send to all active subscribers."""
    from src.modules.newsletter import service as newsletter_service
    from src.modules.subscribers import service as subscriber_service

    click.echo(f"Rendering {markdown_file}...")
    newsletter = newsletter_service.render(markdown_file)

    for warning in newsletter.warnings:
        click.secho(f"  ⚠  {warning}", fg="yellow")

    click.echo(f"  Subject : {newsletter.subject}")

    if dry_run:
        preview_path = markdown_file.replace(".md", "_preview.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(newsletter.html)
        click.secho(f"Dry run — preview saved to {preview_path}", fg="cyan")
        return

    subscribers = subscriber_service.get_active()
    if not subscribers:
        click.secho("No active subscribers found.", fg="yellow")
        return

    click.echo(f"Sending to {len(subscribers)} subscriber(s)...")
    result = newsletter_service.send(newsletter, subscribers)

    click.secho(f"  Sent     : {result.success_count}", fg="green")
    if result.failed:
        click.secho(f"  Failed   : {len(result.failed)}", fg="red")
        for failure in result.failed:
            click.secho(f"    {failure.email} — {failure.error}", fg="red")


# ---------------------------------------------------------------------------
# subscribers
# ---------------------------------------------------------------------------

@cli.group()
def subs():
    """Manage newsletter subscribers."""
    pass


@subs.command("list")
@handle_errors
def subscribers_list():
    """List all subscribers."""
    from src.modules.subscribers import service as subscriber_service

    subs = subscriber_service.list_all()
    if not subs:
        click.echo("No subscribers yet.")
        return

    click.echo(f"\n{'EMAIL':<35} {'NAME':<25} {'ACTIVE'}")
    click.echo("-" * 68)
    for s in subs:
        active = click.style("yes", fg="green") if s.active else click.style("no", fg="red")
        click.echo(f"{s.email:<35} {s.name:<25} {active}")
    click.echo(f"\nTotal: {len(subs)}")


@subs.command("add")
@click.argument("email")
@click.option("--name", default="", help="Subscriber's name.")
@handle_errors
def subscribers_add(email, name):
    """Add a subscriber by EMAIL."""
    from src.modules.subscribers import service as subscriber_service
    from src.modules.subscribers.schema import SubscriberCreate

    subscriber_service.add(SubscriberCreate(email=email, name=name))
    click.secho(f"Added {email}", fg="green")


@subs.command("remove")
@click.argument("email")
@handle_errors
def subscribers_remove(email):
    """Remove a subscriber by EMAIL."""
    from src.modules.subscribers import service as subscriber_service

    if click.confirm(f"Remove {email}?"):
        subscriber_service.remove(email)
        click.secho(f"Removed {email}", fg="green")


@subs.command("import")
@click.argument("csv_file", type=click.Path(exists=True))
@handle_errors
def subscribers_import(csv_file):
    """Bulk import subscribers from a CSV_FILE (Google Sheets export)."""
    from src.modules.subscribers import service as subscriber_service

    click.echo(f"Importing from {csv_file}...")
    result = subscriber_service.import_from_csv(csv_file)
    click.secho(f"  Added   : {result.added}", fg="green")
    click.secho(f"  Skipped : {result.skipped}", fg="yellow")


if __name__ == "__main__":
    cli()
