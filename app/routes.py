import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import database
from app.database import get_db
from app.generator import generate_nutrition_tip, generate_workout, update_workout_plan
from app.schemas import FeedbackRequest, GOALS, INTENSITIES, UserInput

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def _render(request: Request, name: str, **context):
    status_code = context.pop("status_code", 200)
    return templates.TemplateResponse(request=request, name=name, context={"request": request, **context}, status_code=status_code)


def _validation_message(exc: ValidationError) -> str:
    first = exc.errors()[0]
    return str(first["msg"]).replace("Value error, ", "")


def _render_plan(record, updated=False):
    raw = record.updated_plan if updated and record.updated_plan else record.original_plan
    return json.loads(raw)


@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request):
    return _render(request, "index.html", goals=GOALS, intensities=INTENSITIES, error=None)


@router.post("/generate-workout", response_class=HTMLResponse, name="generate")
async def generate(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    try:
        user_data = UserInput(**dict(form)).model_dump()
    except ValidationError as exc:
        return _render(request, "index.html", goals=GOALS, intensities=INTENSITIES, error=_validation_message(exc), values=dict(form), status_code=422)
    try:
        user = database.save_user(db, user_data)
        plan = generate_workout(user_data)
        tip = generate_nutrition_tip(user_data["goal"])
        record = database.save_plan(db, user, plan, tip)
        return _render(request, "result.html", user=user, plan=plan, record=record, nutrition_tip=tip, success="Your 7-day plan is ready. Generated locally—no API key or internet connection was used.", updated=False)
    except Exception:
        db.rollback()
        logger.exception("Could not generate or save a workout plan")
        return _render(request, "error.html", message="We could not save your plan. Please try again.", status_code=500)


@router.post("/submit-feedback", response_class=HTMLResponse, name="feedback")
async def feedback(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    try:
        data = FeedbackRequest(**dict(form)).model_dump()
    except ValidationError as exc:
        found = database.get_original_plan(db, str(form.get("user_id", "")))
        if not found:
            return _render(request, "error.html", message="We couldn't find a saved plan for that User ID.", status_code=404)
        user, record = found
        return _render(request, "result.html", user=user, plan=_render_plan(record), record=record, nutrition_tip=record.nutrition_tip, error=_validation_message(exc), updated=False, status_code=422)
    try:
        found = database.get_original_plan(db, data["user_id"])
        if not found:
            return _render(request, "error.html", message="We couldn't find a saved plan for that User ID. Create a plan first.", status_code=404)
        user, record = found
        original = json.loads(record.original_plan)
        updated_plan = update_workout_plan(original, data["feedback"], user.intensity)
        database.update_plan(db, record, updated_plan, data["feedback"])
        return _render(request, "result.html", user=user, plan=updated_plan, record=record, nutrition_tip=record.nutrition_tip, success="Your plan was updated. The original plan remains saved in your history.", updated=True)
    except Exception:
        db.rollback()
        logger.exception("Could not update workout plan")
        return _render(request, "error.html", message="We couldn't update your plan just now. Please try again.", status_code=500)


@router.get("/view-all-users", response_class=HTMLResponse, name="all_users")
def view_all_users(request: Request, db: Session = Depends(get_db)):
    try:
        users = database.get_all_users(db)
        rows = []
        for user in users:
            for record in user.plans:
                rows.append({"user": user, "record": record, "original": json.loads(record.original_plan), "updated": json.loads(record.updated_plan) if record.updated_plan else None})
        return _render(request, "all_users.html", rows=rows)
    except Exception:
        logger.exception("Could not load admin dashboard")
        return _render(request, "error.html", message="We couldn't load the saved plans.", status_code=500)


@router.get("/health", name="health")
def health():
    return {"status": "ok", "generator": "local-rules", "external_api": False}
