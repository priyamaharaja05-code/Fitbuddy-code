from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


GOALS = (
    "Weight Loss",
    "Muscle Gain",
    "General Wellness",
    "Flexibility",
    "Strength",
    "Endurance",
)
INTENSITIES = ("Low", "Medium", "High")


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    user_id: str = Field(min_length=2, max_length=40)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=300)
    goal: Literal[
        "Weight Loss", "Muscle Gain", "General Wellness", "Flexibility", "Strength", "Endurance"
    ]
    intensity: Literal["Low", "Medium", "High"]

    @field_validator("name")
    @classmethod
    def name_has_letters(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Please enter your name.")
        return value.strip()

    @field_validator("user_id")
    @classmethod
    def user_id_is_simple(cls, value: str) -> str:
        if not value.strip() or not all(c.isalnum() or c in "_-" for c in value):
            raise ValueError("Use only letters, numbers, hyphens, or underscores for User ID.")
        return value.strip()


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=2, max_length=40)
    feedback: str = Field(min_length=5, max_length=500)

    @field_validator("feedback", mode="before")
    @classmethod
    def feedback_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Please tell us what you would like to change.")
        return value.strip()
