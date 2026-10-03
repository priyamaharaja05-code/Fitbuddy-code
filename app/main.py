import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router

ROOT = Path(__file__).resolve().parent.parent
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FitBuddy — Local Fitness Planner", description="A privacy-friendly fitness planner that works without external APIs.", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.state.templates = Jinja2Templates(directory=ROOT / "templates")
app.include_router(router)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    templates = app.state.templates
    return templates.TemplateResponse(request=request, name="error.html", context={"request": request, "message": "That page or saved plan could not be found."}, status_code=404)
