# Jon-Frost-DSP

This project is a Dash-based data analysis web app that lets a user:

- create an account and log in
- create and reopen saved analysis sessions
- upload CSV data to a session
- build multiple interactive Plotly visualisations
- persist uploaded data and chart configurations per session
- ask Gemini questions about the uploaded dataset and the user-made dashboard
- export dashboard charts as PNG files

## What the App Does

The application uses Flask as the underlying web server and Dash as the UI framework. A user logs in, creates a project session, uploads a dataset, and builds a dashboard from multiple chart cards. The uploaded data and chart definitions are saved to SQLite so the user can reopen a session later and continue from where they left off.

The app also connects to the Gemini API. When the user asks a question, the prompt includes:

- the dataset columns
- a user-controlled sample of CSV rows
- summary statistics for numeric columns
- the current dashboard chart definitions

This gives the assistant enough context to explain both the data and the dashboard visuals.

## Main Features

- User registration and login
- Session-based project management
- CSV upload and preview metadata
- Multi-chart dashboard builder
- Persistent session restore
- AI-assisted analysis with Gemini
- PNG export of dashboard charts

## Packages Used

These are the dependencies listed in [requirements.txt](c:/Users/JonFr/.Uni/Jon-Frost-DSP/requirements.txt) and why they are used:

- `dash`: Main framework used to build the web app UI and callbacks.
- `dash-bootstrap-components`: Optional UI helper components and Bootstrap compatibility for styling.
- `Flask`: Underlying Python web server used by Dash.
- `Flask-SQLAlchemy`: Integration layer between Flask and SQLAlchemy for database access.
- `google-genai`: Gemini API client used to send prompts and receive AI responses.
- `kaleido`: Static image engine used by Plotly to export charts as PNGs.
- `pandas`: Data loading, dataframe transformation, sampling, and descriptive statistics.
- `plotly`: Charting library used to build bar, line, scatter, histogram, and box plots.
- `python-dotenv`: Loads environment variables from a local `.env` file.
- `SQLAlchemy`: ORM and database toolkit used for users, sessions, and saved dashboard state.
- `Werkzeug`: Password hashing/checking utilities and Flask internals.

## Project Structure

- [app.py](c:/Users/JonFr/.Uni/Jon-Frost-DSP/app.py): Main Dash/Flask application, callbacks, Gemini integration, export logic.
- [src/layout.py](c:/Users/JonFr/.Uni/Jon-Frost-DSP/src/layout.py): Page layouts and reusable UI sections.
- [src/models.py](c:/Users/JonFr/.Uni/Jon-Frost-DSP/src/models.py): Database models and persistence helpers.
- [assets/styles.css](c:/Users/JonFr/.Uni/Jon-Frost-DSP/assets/styles.css): App styling loaded automatically by Dash.
- [data/](c:/Users/JonFr/.Uni/Jon-Frost-DSP/data): Example dataset(s).
- [instance/](c:/Users/JonFr/.Uni/Jon-Frost-DSP/instance): SQLite database storage created by Flask.

## Environment Variables

Create a `.env` file in the project root with at least:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

Notes:

- `GEMINI_API_KEY` is required for the AI assistant features.
- `FLASK_SECRET_KEY` is recommended for session security. If missing, the app falls back to a default value.

## First-Time Setup

Run these commands from the project root in PowerShell.

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file in the root directory and add your Gemini key and Flask secret key.

### 5. Start the app

```powershell
python app.py
```

The app should then be available at:

```text
http://127.0.0.1:8050
```

## Running the App Later

After the first setup, you usually only need:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Or without activation:

```powershell
.\.venv\Scripts\python.exe app.py
```

## Typical Workflow

1. Register or log in.
2. Create a new session from the home page.
3. Upload a CSV on the dashboard page.
4. Add visualisations to build a dashboard.
5. Ask Gemini questions about the data and dashboard.
6. Reopen a saved session later and continue working.
7. Export dashboard charts to PNG.

## Notes and Troubleshooting

- If PNG export fails, make sure the app is running from the same Python environment where `kaleido` is installed.
- If the browser cannot connect to `127.0.0.1:8050`, the app process is not currently running or failed during startup.
- If Gemini responses fail, verify that `GEMINI_API_KEY` is set correctly in `.env`.

## Install From Scratch Summary

If someone wants the full first-time sequence in one place:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
