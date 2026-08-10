from app.extensions import db
from app.models.mixins import TimestampMixin


class User(TimestampMixin, db.Model):  # type: ignore[name-defined]
    __tablename__ = "users"

    # bigint (BRIEF) -> db.Integer, deliberately: SQLite's INTEGER storage
    # class is already 8-byte, and a PK is only aliased to SQLite's fast
    # native rowid (free auto-increment) when the DDL says exactly
    # "INTEGER PRIMARY KEY" — BigInteger would emit "BIGINT PRIMARY KEY",
    # which loses that rowid aliasing for zero benefit.
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.id} {self.email!r} admin={self.is_admin}>"
