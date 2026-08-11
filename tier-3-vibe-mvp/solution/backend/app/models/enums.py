import enum


class EventType(str, enum.Enum):
    STUDY_GROUP = "study_group"
    AMA = "ama"
    WORKSHOP = "workshop"
    SOCIAL = "social"
    OTHER = "other"


class LocationType(str, enum.Enum):
    IN_PERSON = "in_person"
    HYBRID = "hybrid"
    VIRTUAL = "virtual"


class RegistrationStatus(str, enum.Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


# SQLite has no native ENUM type. SQLAlchemy's db.Enum(...) handles that by
# emitting a VARCHAR column, optionally plus a CHECK (col IN (...))
# constraint for DB-level enforcement.
#
# Two traps, both easy to get burned by silently:
#
# 1. By default SQLAlchemy persists the enum MEMBER NAME ("STUDY_GROUP"),
#    not its value ("study_group") — BRIEF's wire values are lowercase-
#    snake / mixed-case, not Pythonic UPPER_SNAKE member names. Every enum
#    column must pass values_callable, or the DB would silently store
#    "STUDY_GROUP" instead of "study_group".
#
# 2. As of SQLAlchemy 2.0, Enum's `create_constraint` default flipped from
#    True to False (a deliberate change — 1.x's default constraint made
#    autogenerate diffs noisy across upgrades). Found this the hard way:
#    without create_constraint=True, every enum column below is just a
#    bare VARCHAR with ZERO DB-level enforcement — an invalid string
#    inserts silently and only surfaces later, as a confusing LookupError
#    when SQLAlchemy tries to map the bad value back to a Python enum
#    member on read. Every enum column must pass create_constraint=True.
def enum_values(py_enum: type[enum.Enum]) -> list[str]:
    return [member.value for member in py_enum]
