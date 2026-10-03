import pytest
from pydantic import ValidationError

from app.schemas import FeedbackRequest, UserInput


def test_valid_profile_and_feedback():
    profile = UserInput(name="  Jamie  ", user_id="jamie-7", age=25, weight=60, goal="Endurance", intensity="High")
    assert profile.name == "Jamie"
    assert FeedbackRequest(user_id="jamie-7", feedback="Add more rest days").feedback == "Add more rest days"


@pytest.mark.parametrize("overrides", [
    {"name": " "}, {"user_id": "bad id"}, {"age": 8}, {"weight": 0},
    {"goal": "Marathon in one week"}, {"intensity": "Extreme"},
])
def test_invalid_profile_rejected(overrides):
    values = {"name": "Jamie", "user_id": "jamie7", "age": 25, "weight": 60, "goal": "Endurance", "intensity": "Medium"}
    values.update(overrides)
    with pytest.raises(ValidationError):
        UserInput(**values)


def test_empty_feedback_rejected():
    with pytest.raises(ValidationError):
        FeedbackRequest(user_id="jamie7", feedback=" ")
