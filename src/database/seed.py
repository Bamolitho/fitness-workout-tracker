from sqlalchemy.dialects.postgresql import insert

from src.database.enums import Category, MuscleGroup
from src.database.models import Exercise
from src.database.session import SessionLocal

EXERCISES = [
    {
        "name": "Bench Press",
        "description": "Barbell press lying on a bench",
        "category": Category.STRENGTH,
        "muscle_group": MuscleGroup.CHEST,
    },
    {
        "name": "Squat",
        "description": "Barbell squat",
        "category": Category.STRENGTH,
        "muscle_group": MuscleGroup.LEGS,
    },
    {
        "name": "Deadlift",
        "description": "Lift the barbell from the floor",
        "category": Category.STRENGTH,
        "muscle_group": MuscleGroup.BACK,
    },
    {
        "name": "Running",
        "description": None,
        "category": Category.CARDIO,
        "muscle_group": MuscleGroup.FULL_BODY,
    },
    {
        "name": "Hamstring Stretch",
        "description": None,
        "category": Category.FLEXIBILITY,
        "muscle_group": MuscleGroup.LEGS,
    },
]


def seed_exercises() -> None:
    stmt = (
        insert(Exercise)
        .values(EXERCISES)
        .on_conflict_do_nothing(index_elements=["name"])
        .returning(Exercise.name)
    )
    with SessionLocal.begin() as session:  # commit auto, rollback auto si erreur
        inserted = session.scalars(stmt).all()

    print(f"{len(inserted)} exercise(s) inserted, {len(EXERCISES) - len(inserted)} already present")


if __name__ == "__main__":
    seed_exercises()
