from flask import Flask

from app.config import UPLOAD_DIR, Config, ensure_runtime_dirs
from app.extensions import cors, db, jwt


def create_app(config_class: type[Config] = Config, init_db: bool = False) -> Flask:
    """Application factory.

    Alembic (via `flask db-setup`, see app/cli.py) is the actual source of
    truth for schema + seed data — NOT db.create_all(). init_db defaults to
    False so a normal app boot (including `flask db-setup` itself, which
    builds the app via Flask's CLI loader before its command body runs)
    doesn't race db.create_all() against Alembic creating the same tables
    a moment later. Tests pass init_db=True explicitly to get a fast,
    isolated scratch schema without going through the migration runner
    (see tests/conftest.py for the rationale).
    """
    # static_folder/static_url_path repurpose Flask's built-in static-file
    # handling to serve uploads/ at /uploads/... — BRIEF's endpoint table
    # has no route for this, but Event.image paths need to be loadable
    # somehow. This app has no Jinja templates or other static assets, so
    # there's no conflict, and it comes with Flask's already-hardened
    # static handler (conditional GET/ETag, path-traversal protection) for
    # free instead of a hand-written send_from_directory route.
    app = Flask(
        __name__, static_folder=str(UPLOAD_DIR.parent), static_url_path="/uploads"
    )
    app.config.from_object(config_class)

    ensure_runtime_dirs()

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app, resources={r"/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}}
    )

    from app import models  # noqa: F401 — registers tables on db.metadata

    if init_db:
        with app.app_context():
            db.create_all()

    # Routes and error handlers are registered unconditionally (not gated
    # by init_db, which only ever controlled schema-creation strategy) —
    # the test fixture needs real routes too.
    from app.routes import register_blueprints

    register_blueprints(app)

    from app.errors import register_error_handlers

    register_error_handlers(app)

    from app.cli import db_setup_command

    app.cli.add_command(db_setup_command)

    return app
