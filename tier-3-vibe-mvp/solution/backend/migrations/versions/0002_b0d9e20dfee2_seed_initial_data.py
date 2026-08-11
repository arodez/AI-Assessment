"""seed initial data

Revision ID: b0d9e20dfee2
Revises: 50c9ab63da9c
Create Date: 2026-08-07 12:14:51.751493

Data-only migration: loads the fixture users/events/registrations from
scripts/seed_data.py and copies the 7 mockup cover photos into
uploads/events/. Kept as a separate revision (not folded into 0001) so the
schema-only migration stays pure DDL, and so a future "reset seed data
without touching schema" need has something to alembic downgrade/upgrade
against on its own.

Uses SQLAlchemy Core (sa.table/sa.column, op.bulk_insert), not the ORM
models: a migration must stay pinned to the schema shape it was written
against, which the ORM classes are free to move on from in later phases.
"""

from collections.abc import Sequence
from datetime import UTC

import sqlalchemy as sa
from alembic import op

from scripts.seed_data import EVENTS, REGISTRATIONS, USERS, copy_seed_photos

# revision identifiers, used by Alembic.
revision: str = "b0d9e20dfee2"
down_revision: str | Sequence[str] | None = "50c9ab63da9c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


users_table = sa.table(
    "users",
    sa.column("id", sa.Integer),
    sa.column("first_name", sa.String),
    sa.column("last_name", sa.String),
    sa.column("email", sa.String),
    sa.column("is_admin", sa.Boolean),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)

events_table = sa.table(
    "events",
    sa.column("id", sa.Integer),
    sa.column("title", sa.String),
    sa.column("start", sa.DateTime),
    sa.column("end", sa.DateTime),
    sa.column("spots", sa.Integer),
    sa.column("event_type", sa.String),
    sa.column("location_type", sa.String),
    sa.column("description", sa.Text),
    sa.column("image", sa.String),
    sa.column("location", sa.JSON),
    sa.column("host_name", sa.String),
    sa.column("host_team", sa.String),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)

users_events_table = sa.table(
    "users_events",
    sa.column("id", sa.Integer),
    sa.column("user_id", sa.Integer),
    sa.column("event_id", sa.Integer),
    sa.column("status", sa.String),
    sa.column("sign_up_at", sa.DateTime),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)


def _with_timestamps(rows: list[dict], now) -> list[dict]:
    return [{**row, "created_at": now, "updated_at": now} for row in rows]


def upgrade() -> None:
    """Load fixture data."""
    copy_seed_photos()

    # bulk_insert needs real Python datetime values, not a SQL expression
    # like func.current_timestamp() — compute one "now" instant here so
    # created_at/updated_at are populated and consistent across the batch.
    from datetime import datetime

    now = datetime.now(UTC).replace(tzinfo=None)

    op.bulk_insert(users_table, _with_timestamps(USERS, now))
    op.bulk_insert(events_table, _with_timestamps(EVENTS, now))
    op.bulk_insert(users_events_table, _with_timestamps(REGISTRATIONS, now))


def downgrade() -> None:
    """Remove the seeded rows, by their natural keys (not raw DELETE-all,
    in case future data has been added alongside the fixtures)."""
    conn = op.get_bind()
    conn.execute(
        users_events_table.delete().where(
            users_events_table.c.id.in_([row["id"] for row in REGISTRATIONS])
        )
    )
    conn.execute(
        events_table.delete().where(
            events_table.c.title.in_([row["title"] for row in EVENTS])
        )
    )
    conn.execute(
        users_table.delete().where(
            users_table.c.email.in_([row["email"] for row in USERS])
        )
    )
