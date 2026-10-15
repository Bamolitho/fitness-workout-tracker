# fitness-workout-tracker

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/) [![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet)](https://docs.astral.sh/uv/) [![Ruff](https://img.shields.io/badge/code%20style-Ruff-d7ff64)](https://docs.astral.sh/ruff/) [![Pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest)](https://docs.pytest.org/) [![RESTful API](https://img.shields.io/badge/API-RESTful-02569B)](https://restfulapi.net/)

This project involves creating a backend system for a workout tracker application where users can sign up, log in, create workout plans, and track their progress. The system features JWT authentication, CRUD operations for workouts, and generate reports on past workouts.

> The idea of this project comes from the backend learning roadmap of [roadmap.sh](https://roadmap.sh/projects/fitness-workout-tracker)

The goal is to develop a RESTful API for a workout tracker application that allows users to manage their workouts and track their progress.

## What is involved in this project?

* backend system for an application,
* designing the database schema,
* implementing user authentication,
* creating RESTful API endpoints,
* unit testing and code documentation.

## Project structure

```text
src/
└── database/
    ├── config.py    # Settings (pydantic-settings), reads the .env file
    ├── enums.py     # Category, MuscleGroup, SubscriptionPlan, Status
    ├── models.py    # SQLAlchemy models: Exercise, User, Workout, WorkoutExercise
    ├── seed.py      # Use to feed the table Exercise
    └── session.py   # Engine + LocalSession
```

* **Stack**: PostgreSQL, SQLAlchemy 2.0 (typed `Mapped[...]` models), `psycopg` (v3), `pydantic-settings`, `uv`, `ruff`.
* **Configuration**: database credentials are read from a `.env` file at the root of the project (never committed).

```text
DB_NAME=mydb
DB_USER=my_user
DB_PASSWORD=change_me
DB_HOST=localhost
DB_PORT=5432
```

## Database schema (PostgreSQL)

A data seeder is used to populate the database with a list of exercises.

Conventions used in every table:

* The primary key is named `id` (foreign keys use the `<table>_id` form, for example `workouts.user_id`).
* Enumerations are native PostgreSQL `ENUM` types, mapped to Python `StrEnum` classes in `enums.py`. The values are stored in lowercase (`cardio`, not `CARDIO`).
* All `datetime` columns are `TIMESTAMP WITH TIME ZONE`.
* Constraints and indexes follow a naming convention (`pk_`, `fk_`, `uq_`, `ck_`, `ix_` prefixes), so that migrations are predictable.

### `exercises`

> Stores all the exercises available in the application. Workouts can reference these exercises through `workout_exercises`.

| Column         | Type                          | Constraints                | Description                                                                   |
| -------------- | ----------------------------- | -------------------------- | ----------------------------------------------------------------------------- |
| `id`           | `INTEGER`                     | `PK`, `NOT NULL`           | Unique identifier of the exercise                                             |
| `name`         | `VARCHAR(100)`                | `NOT NULL`, `UNIQUE`       | Name of the exercise                                                          |
| `description`  | `TEXT`                        | `NULL`                     | Description of the exercise                                                   |
| `category`     | `ENUM exercise_category`      | `NOT NULL`                 | Exercise category: `cardio`, `strength`, `flexibility`, or `other`            |
| `muscle_group` | `ENUM exercise_muscle_group`  | `NOT NULL`                 | Targeted muscle group: `chest`, `back`, `legs`, `shoulders`, `arms`, `core`, `full_body`, or `other` |
| `created_at`   | `TIMESTAMPTZ`                 | `NOT NULL`, `DEFAULT now()`| Date when the exercise was created                                            |

### `users`

> This table contains the information required to identify a user, authenticate them, and manage their subscription.

| Column                    | Type                           | Constraints                 | Description                                      |
| ------------------------- | ------------------------------ | --------------------------- | ------------------------------------------------ |
| `id`                      | `INTEGER`                      | `PK`, `NOT NULL`            | Unique identifier of the user                    |
| `full_name`               | `VARCHAR(200)`                 | `NOT NULL`                  | Full name of the user                            |
| `address`                 | `VARCHAR(200)`                 | `NULL`                      | User's address                                   |
| `phone_number`            | `VARCHAR(30)`                  | `NULL`                      | User's phone number                              |
| `email`                   | `VARCHAR(100)`                 | `NOT NULL`, `UNIQUE`        | User's email address                             |
| `password_hash`           | `VARCHAR(255)`                 | `NOT NULL`                  | Hashed user password                             |
| `subscription_plan`       | `ENUM user_subscription_plan`  | `NOT NULL`, `DEFAULT basic` | Subscription plan: `basic`, `premium`, or `gold` |
| `created_at`              | `TIMESTAMPTZ`                  | `NOT NULL`, `DEFAULT now()` | Date when the account was created                |
| `subscription_started_at` | `TIMESTAMPTZ`                  | `NOT NULL`, `DEFAULT now()` | Date when the subscription was started           |

### `workouts`

> A workout represents a specific workout session belonging to a user, with its own date, status, and exercises. This table allows us to retrieve, for example, a workout planned for December 2, 2026, for Alice.

For example:

* `id = 6` (6th workout session)
* `user_id = 34` (Alice)
* `status = planned`
* `scheduled_at = December 2, 2026`

| Column         | Type                    | Constraints                                 | Description                                            |
| -------------- | ----------------------- | ------------------------------------------- | ------------------------------------------------------ |
| `id`           | `INTEGER`               | `PK`, `NOT NULL`                            | Unique identifier of the workout                       |
| `user_id`      | `INTEGER`               | `FK`, `NOT NULL`, `INDEX`, `ON DELETE CASCADE` | User who owns the workout                           |
| `status`       | `ENUM workout_status`   | `NOT NULL`, `DEFAULT planned`               | Workout status: `planned`, `completed`, or `cancelled` |
| `scheduled_at` | `TIMESTAMPTZ`           | `NOT NULL`                                  | Scheduled date and time of the workout                 |
| `comments`     | `TEXT`                  | `NULL`                                      | Optional comments about the workout                    |
| `created_at`   | `TIMESTAMPTZ`           | `NOT NULL`, `DEFAULT now()`                 | Date when the workout was created                      |

If a user is deleted, their workouts are deleted too (`ON DELETE CASCADE`).

### `workout_exercises`

> This is the association table between `exercises` and `workouts`. The values `sets`, `reps`, and `weight_kg` depend on the `(workout, exercise)` pair.

| Column        | Type           | Constraints                                    | Description                                   |
| ------------- | -------------- | ---------------------------------------------- | --------------------------------------------- |
| `id`          | `INTEGER`      | `PK`, `NOT NULL`                               | Unique identifier of the row                  |
| `workout_id`  | `INTEGER`      | `FK`, `NOT NULL`, `INDEX`, `ON DELETE CASCADE` | Workout associated with the exercise          |
| `exercise_id` | `INTEGER`      | `FK`, `NOT NULL`                               | Exercise associated with the workout          |
| `position`    | `INTEGER`      | `NOT NULL`                                     | Order of the exercise within the workout      |
| `sets`        | `INTEGER`      | `NOT NULL`, `CHECK (sets > 0)`                 | Number of sets                                |
| `reps`        | `INTEGER`      | `NOT NULL`, `CHECK (reps > 0)`                 | Number of repetitions per set                 |
| `weight_kg`   | `NUMERIC(6,2)` | `NULL`, `CHECK (weight_kg >= 0)`               | Weight used in kilograms                      |

The pair `(workout_id, position)` is unique: two exercises cannot occupy the same position in the same workout session.

If a workout is deleted, its rows are deleted too (`ON DELETE CASCADE`). There is no cascade on `exercise_id`: an exercise still used by a workout cannot be deleted, so the history is preserved.

I no longer use `(workout_id, exercise_id)` as a composite primary key. A row has its own `id`, so the same exercise can appear more than once in the same workout session, at different positions.

For example:

```txt
Workout 1 + Bench Press → 4 sets × 10 reps × 60 kg
Workout 2 + Bench Press → 3 sets × 8 reps × 70 kg
```

The Bench Press remains the same exercise, but its configuration changes depending on the workout.

It therefore represents the configuration of an exercise within a workout.

```text
WORKOUT_EXERCISE =
"In this workout, this exercise is performed in this way."
```

For example:

```text
Workout 6
    |
    +--- 1. Bench Press
    |      4 sets
    |      10 reps
    |      60 kg
    |
    +--- 2. Squat
           3 sets
           8 reps
           100 kg
```

## Relational model

```text
USER (1) -------- (N) WORKOUT
                         |
                         | 1:N
                         v
                  WORKOUT_EXERCISE
                         ^
                         | N:1
                         |
                    EXERCISE
```

And therefore, indirectly, there is a many-to-many relationship:

```text
WORKOUT (N) <----------> (N) EXERCISE
```

Thus:

* **One user can have multiple workout sessions** (`one-to-many`):

```text
USER (1) -------- (N) WORKOUT

(id, user_id) = (7, 3), (9, 3)
```

The same user with ID `3` has workouts with IDs `7` and `9`.

* **One workout can contain multiple exercises** (`one-to-many` through the association table):

```text
WORKOUT (1) -------- (N) WORKOUT_EXERCISE

(workout_id, exercise_id) = (2, 1), (2, 4), (2, 8)
```

Exercises `1`, `4`, and `8` are all part of workout `2`.

* **The same exercise can be present in multiple workouts**:

```text
WORKOUT_EXERCISE (N) -------- (1) EXERCISE

(workout_id, exercise_id) = (2, 1), (4, 1), (5, 1)
```

Exercise `1` is part of workouts `2`, `4`, and `5`.

### SQLAlchemy relationships

```text
User.workouts          -> list[Workout]          (cascade: all, delete-orphan)
Workout.user           -> User
Workout.items          -> list[WorkoutExercise]  (ordered by position, cascade: all, delete-orphan)
WorkoutExercise.workout  -> Workout
WorkoutExercise.exercise -> Exercise
```

For example, `workout.items[0].exercise.name` gives the name of the first exercise of a workout.

## API endpoints

### User Authentication and Authorization

Users will be able to sign up, log in, and log out of the application. You should use JWTs for authentication and authorization. Only authenticated users should be able to create, update, and delete workout plans. Needless to say, users should only be able to access their own workout plans.

- **Sign-Up**: Allow users to create an account.
- **Login**: Allow users to log in to their account.
- **JWT**: Use JSON Web Tokens for authentication.

### Workout Management

Users will be able to create their workout plans. Workout plans should consist of multiple exercises, each with a set number of repetitions, sets, and weights. Users should be able to update and delete their workout plans. Additionally, users should be able to schedule workouts for specific dates and times.

- Create Workout: Allow users to create workouts composed of multiple exercises.
- Update Workout: Allow users to update workouts and add comments.
- Delete Workout: Allow users to delete workouts.
- Schedule Workouts: Allow users to schedule workouts for specific dates and times.
- List Workouts: List active or pending workouts sorted by date and time.
- Generate Reports: Generate reports on past workouts and progress.

## Constraints

- **Database**: Use a relational database to store user data, workout plans, and exercise data.
- **API**: Develop a RESTful API to interact with the database.
- **Security**: Implement JWT authentication to secure the API endpoints.
- **Testing**: Write unit tests to ensure the correctness of your code.
- **Documentation**: Learn about OpenAPI Specs. Document your API endpoints and provide examples of how to use them.
