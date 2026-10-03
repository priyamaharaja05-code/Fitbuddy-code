import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _database_url() -> str:
    configured = os.getenv("FITBUDDY_DATABASE_URL")
    if configured:
        return configured
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'fitbuddy.db'}"


DATABASE_URL = _database_url()
_engine_args = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **_engine_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    goal: Mapped[str] = mapped_column(String(40), nullable=False)
    intensity: Mapped[str] = mapped_column(String(12), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    plans: Mapped[list["WorkoutPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_pk: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_plan: Mapped[str] = mapped_column(Text, nullable=False)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    user: Mapped[User] = relationship(back_populates="plans")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db: Session, data: dict) -> User:
    user = db.scalar(select(User).where(User.user_id == data["user_id"]))
    if user is None:
        user = User(**data)
        db.add(user)
    else:
        for key in ("name", "age", "weight", "goal", "intensity"):
            setattr(user, key, data[key])
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


def save_plan(db: Session, user: User, plan: dict, nutrition_tip: str) -> WorkoutPlan:
    record = WorkoutPlan(user_pk=user.id, original_plan=__import__("json").dumps(plan), nutrition_tip=nutrition_tip)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_original_plan(db: Session, user_id: str) -> tuple[User, WorkoutPlan] | None:
    user = get_user(db, user_id)
    if user is None:
        return None
    record = db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_pk == user.id).order_by(WorkoutPlan.created_at.desc()))
    return (user, record) if record else None


def update_plan(db: Session, record: WorkoutPlan, plan: dict, feedback: str) -> WorkoutPlan:
    import json

    record.updated_plan = json.dumps(plan)
    record.feedback = feedback
    record.updated_at = utc_now()
    db.commit()
    db.refresh(record)
    return record


def get_all_plans(db: Session) -> list[WorkoutPlan]:
    return list(db.scalars(select(WorkoutPlan).order_by(WorkoutPlan.created_at.desc())).all())
