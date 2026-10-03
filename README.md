# FitBuddy — Offline Fitness Plan Generator

FitBuddy is a complete local web application for creating practical 7-day workout plans and general nutrition/recovery tips. It uses a deterministic, rule-based generator and stores plan history in SQLite. **It makes no API calls, needs no API key, and can run without internet access.**

> This is the API-free implementation requested for the project. The supplied brief described Gemini, which conflicts with the explicit requirement that the complete project work without any API. This build follows the no-API requirement; its plan suggestions are rule-based, not Gemini-generated AI.

## Features

- Responsive profile form: name, user ID, age, weight, fitness goal, and intensity.
- Seven-day plan with focus, warm-up, exercises, sets/repetitions, rest, and cooldown.
- Goal-aligned general nutrition/recovery tip.
- Local feedback adjustments for requests such as more cardio, yoga, shorter sessions, easier effort, more rest, or upper-body emphasis.
- Original plan retained when an adjusted version is saved.
- SQLite database with SQLAlchemy ORM for profiles and plan history.
- Saved-plans dashboard, Pydantic validation, friendly errors, and `/docs`.
- No external services, API credentials, analytics, or hosted fonts. All styles and plan generation work locally.

## Technologies

Python 3.10+, FastAPI, Uvicorn, SQLAlchemy 2, SQLite, Jinja2, HTML/CSS/JavaScript, Pydantic 2, pytest, and HTTPX.

## Architecture

1. Browser submits a standard HTML form to FastAPI.
2. `schemas.py` validates the submitted fields.
3. `generator.py` selects safe exercise templates from local rules; it has no network client.
4. `database.py` saves the profile and JSON plan records to SQLite.
5. Jinja templates render the result and saved history.
6. Feedback is applied by safe, explicit local rules; it never calls an AI service.

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI setup, static files, startup database creation
│   ├── routes.py           # Home, generation, feedback, dashboard, health routes
│   ├── database.py         # SQLite models, sessions, and CRUD helpers
│   ├── schemas.py          # Pydantic validation
│   └── generator.py        # Offline workout, tip, and feedback rules
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
├── static/
│   ├── css/style.css
│   └── js/script.js
├── tests/
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_database.py
│   └── test_schemas.py
├── data/                   # Created automatically; local database goes here
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml          # Pytest project-root and test discovery settings
├── run.py
└── README.md
```

## Step-by-step: open and run in VS Code (Windows)

1. Download and extract the project ZIP, then open the extracted **FitBuddy** folder in VS Code using **File → Open Folder**.
2. Open the integrated terminal with **Terminal → New Terminal** (`Ctrl` + `` ` ``). Confirm the prompt is in the `FitBuddy` directory. If not, run `cd path\to\FitBuddy`.
3. Create a Python virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate it in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, either use Command Prompt with `.venv\Scripts\activate.bat`, or run this once in the current PowerShell window: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
5. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. (Optional) Copy `.env.example` to `.env` and change `FITBUDDY_DATABASE_URL` if you want a different **local** SQLite file. The default `data/fitbuddy.db` is created automatically. No API key is needed.
7. Start the site:

   ```powershell
   uvicorn app.main:app --reload
   ```

8. Open **http://127.0.0.1:8000** in your browser. Use **http://127.0.0.1:8000/docs** for the FastAPI docs and **http://127.0.0.1:8000/view-all-users** for saved plan history.
9. Stop the server by focusing the terminal and pressing `Ctrl+C`.

### Windows command prompt alternative

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### macOS / Linux terminal

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If `py` is not recognized on Windows, use `python` instead. Python 3.10 or later is recommended.

## Environment settings

| Setting | Purpose | Default |
|---|---|---|
| `FITBUDDY_DATABASE_URL` | Local SQLAlchemy database URL | SQLite file at `data/fitbuddy.db` |

`.env.example` is optional. The app loads `.env` if `python-dotenv` is installed in this project. For a temporary PowerShell variable, use `$env:FITBUDDY_DATABASE_URL = 'sqlite:///./data/fitbuddy.db'`. **There are no Gemini settings or API keys.**

## Database

At startup, SQLAlchemy creates the `users` and `workout_plans` tables automatically. The default SQLite file appears at `data/fitbuddy.db` after the first app start. Each profile is identified by its user ID. Reusing an ID updates its profile; new generated plans are stored as separate history records. Feedback saves an updated plan alongside, not over, the original.

## How to use

1. Fill out your profile and pick a goal and intensity.
2. Select **Create my 7-day plan**. A local rules engine constructs the seven days and displays a recovery tip.
3. Enter a request in the feedback box (for example, “make workouts shorter and add yoga”) and select **Update my plan**.
4. Visit **Saved plans** to review original and updated plan history.

Recognized feedback is adapted using straightforward keyword-based rules. The app ignores feedback containing explicit unsafe signals such as pain, injury, extreme effort, starvation, or removing all rest. Because this is a local rule engine, free-form feedback is not interpreted by a language model.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Fitness profile form |
| POST | `/generate-workout` | Validate, generate, and save plan |
| POST | `/submit-feedback` | Create and save a safe local adjustment |
| GET | `/view-all-users` | Saved user and plan dashboard |
| GET | `/health` | JSON health status |
| GET | `/docs` | Interactive FastAPI documentation |

## Run tests

From the project root with the virtual environment active:

```bash
pytest -q
```

Tests use a temporary SQLite database and do not need an API key or external network. They cover page rendering, input validation, profile/plan persistence, feedback, missing users, and health status.

## Troubleshooting

- **`uvicorn` is not recognized:** activate `.venv` and run `python -m uvicorn app.main:app --reload`.
- **`ModuleNotFoundError`:** check that the terminal is in the project root, activate the environment, and run `pip install -r requirements.txt`.
- **Port 8000 is busy:** run `uvicorn app.main:app --reload --port 8001`, then visit `http://127.0.0.1:8001`.
- **Database locked:** stop any duplicate FitBuddy server processes and restart. SQLite supports local single-user demonstrations.
- **Plan feels unsuitable:** stop exercises that cause pain or unusual symptoms; adjust the profile or request a gentler plan. Seek qualified advice for medical concerns.

## Safety and privacy

FitBuddy plans are general wellness guidance, not medical advice. It does not diagnose conditions or prescribe treatment. Work at a comfortable level, rest when needed, and consult a qualified professional if you have concerns. User details and plans are stored unencrypted in a local SQLite database; do not use real sensitive health information in a classroom demonstration.

## Possible future enhancements

- User-selected equipment and workout duration.
- A richer local feedback parser and exercise library.
- Export a plan to printable PDF/CSV.
- Optional integrations can be added later, but are intentionally excluded from this offline version.
