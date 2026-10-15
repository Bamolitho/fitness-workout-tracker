from enum import StrEnum


class Category(StrEnum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    OTHER = "other"


class MuscleGroup(StrEnum):
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    CORE = "core"
    FULL_BODY = "full_body"
    OTHER = "other"


class SubscriptionPlan(StrEnum):
    BASIC = "basic"
    PREMIUM = "premium"
    GOLD = "gold"


class Status(StrEnum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
