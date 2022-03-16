import logging
import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db.db import db

logger = logging.getLogger(__name__)


class MixinIdDate(db.Model):
    __abstract__ = True
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    create_at = db.Column(db.DateTime, default=db.func.now())
    update_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class User(MixinIdDate):
    __tablename__ = "users"

    email = db.Column(db.String(length=256), unique=True, nullable=False)
    password = db.Column(db.String(length=256), nullable=False)
    full_name = db.Column(db.String(length=256))
    phone_number = db.Column(db.String(length=12))
    auth_history = db.relationship(
        "AuthHistory",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    role_user = db.relationship(
        "UserRole",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Role(MixinIdDate):
    __tablename__ = "roles"

    name = db.Column(db.String, unique=True, nullable=False)
    role_user = db.relationship(
        "UserRole",
        backref="role",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class UserRole(MixinIdDate):
    __tablename__ = "user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE")
    )
    role_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("roles.id", ondelete="CASCADE")
    )


class AuthHistory(MixinIdDate):
    __tablename__ = "auth_history"
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE")
    )
    user_agent = db.Column(db.String, nullable=False)
    host = db.Column(db.String, nullable=False)
    auth_result = db.Column(db.String, nullable=False)
