import click
from flask.cli import with_appcontext

from app.config import BASE_DIR, ensure_runtime_dirs


@click.command("db-setup")
@with_appcontext
def db_setup_command() -> None:
    """One command to set up (or bring up to date) a fresh database.

    Ensures instance/ and uploads/events/ exist, then runs Alembic
    migrations to head — which creates the schema (0001) and loads the
    seed data (0002). Alembic itself remains directly usable for anything
    else (new revisions, downgrade, current) via `poetry run alembic ...`.
    """
    from alembic import command
    from alembic.config import Config as AlembicConfig

    ensure_runtime_dirs()

    alembic_cfg = AlembicConfig(str(BASE_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    command.upgrade(alembic_cfg, "head")
    click.echo("Database is up to date (schema + seed data).")
