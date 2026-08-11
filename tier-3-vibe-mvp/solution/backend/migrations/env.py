import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Defensive: alembic.ini's prepend_sys_path=. covers the common case (run
# from solution/backend/), but this makes `app` importable regardless of
# the invoking CWD — both `poetry run alembic ...` and the `flask db-setup`
# command (which builds an AlembicConfig pointing at this env.py) rely on
# it being importable.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import models  # noqa: E402,F401 — registers tables on db.metadata
from app.config import Config, ensure_runtime_dirs  # noqa: E402
from app.extensions import db  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# instance/ must exist before SQLite can create the DB file there — needed
# both when Alembic runs standalone (`poetry run alembic ...`) and when
# invoked from app/cli.py's `flask db-setup`.
ensure_runtime_dirs()

# The single source of truth for the DB URL is app.config.Config (which
# reads DATABASE_URL from .env, falling back to instance/app.db) — not a
# URL duplicated in alembic.ini.
config.set_main_option("sqlalchemy.url", Config.SQLALCHEMY_DATABASE_URI)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = db.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite's ALTER TABLE support is very limited; batch mode has
        # Alembic recreate-and-swap the table for operations SQLite can't
        # do directly. The initial migration doesn't need it, but any
        # future schema change almost certainly will — cheap to set now.
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
