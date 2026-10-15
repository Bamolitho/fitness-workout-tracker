from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, ClassVar

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeEngine

from src.database.enums import Category, MuscleGroup, Status, SubscriptionPlan


def enum_values(e: type[StrEnum]) -> list[str]:
    return [m.value for m in e]


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    type_annotation_map: ClassVar[dict[type, TypeEngine[Any]]] = {datetime: DateTime(timezone=True)}


class Exercise(Base):
    """Catalog of exercises available in the application.

    Workouts reference them through workout_exercises.
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None]
    category: Mapped[Category] = mapped_column(
        SQLAlchemyEnum(
            Category,
            name="exercise_category",
            values_callable=enum_values,  # store "cardio", not "CARDIO"
        )
    )
    muscle_group: Mapped[MuscleGroup] = mapped_column(
        SQLAlchemyEnum(MuscleGroup, name="exercise_muscle_group", values_callable=enum_values)
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"Exercise(id={self.id}, name={self.name!r}, "
            f"category={self.category!r}, muscle_group={self.muscle_group!r})"
        )


class User(Base):
    """This table contains the information required to identify a user, authenticate them, and manage their subscription"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(200))
    phone_number: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        SQLAlchemyEnum(
            SubscriptionPlan, name="user_subscription_plan", values_callable=enum_values
        ),
        default=SubscriptionPlan.BASIC,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    subscription_started_at: Mapped[datetime] = mapped_column(server_default=func.now())

    workouts: Mapped[list[Workout]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, plan={self.subscription_plan!r})"


class Workout(Base):
    """A workout session belonging to a user, with its own date and status.

    Example: the workout planned for December 2, 2026, for Alice.
    """

    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[Status] = mapped_column(
        SQLAlchemyEnum(Status, name="workout_status", values_callable=enum_values),
        default=Status.PLANNED,
    )
    scheduled_at: Mapped[datetime]
    comments: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship(back_populates="workouts")
    items: Mapped[list[WorkoutExercise]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="WorkoutExercise.position",
    )

    def __repr__(self) -> str:
        return (
            f"Workout(id={self.id}, user_id={self.user_id}, "
            f"status={self.status.value!r}, scheduled_at={self.scheduled_at!r})"
        )


class WorkoutExercise(Base):
    """This is the association table between exercises and workouts.

    The values `reps`, `sets`, and `weight_kg` depend on the (workout, exercise) pair.
    """

    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    position: Mapped[int]
    sets: Mapped[int]
    reps: Mapped[int]
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    __table_args__ = (
        CheckConstraint("sets > 0", name="sets_positive"),
        CheckConstraint("reps > 0", name="reps_positive"),
        CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="weight_nonneg"),
        UniqueConstraint("workout_id", "position"),
    )

    workout: Mapped[Workout] = relationship(back_populates="items")
    exercise: Mapped[Exercise] = relationship()
