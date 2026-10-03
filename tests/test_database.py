from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_all_plans, get_all_users, get_original_plan, save_plan, save_user, update_plan
from app.generator import generate_nutrition_tip, generate_workout


def test_database_crud_round_trip():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    data = {"name": "Morgan", "user_id": "morgan_1", "age": 31, "weight": 72.0, "goal": "Strength", "intensity": "Low"}
    with Session(engine, expire_on_commit=False) as db:
        user = save_user(db, data)
        assert get_all_users(db)[0].user_id == "morgan_1"
        plan = generate_workout(data)
        record = save_plan(db, user, plan, generate_nutrition_tip(data["goal"]))
        found = get_original_plan(db, "morgan_1")
        assert found is not None and found[1].id == record.id
        updated = generate_workout(data)
        update_plan(db, record, updated, "shorter sessions please")
        assert record.feedback == "shorter sessions please"
        assert len(get_all_plans(db)) == 1
    Base.metadata.drop_all(engine)
    engine.dispose()
