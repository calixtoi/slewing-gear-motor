# Running the Slewing Gear Calculator

## Quick Start — Copy & Paste This

```powershell
cd C:\Users\CALIXTOI\Downloads\Github\slewing-gear-motor && py -m pip install django pdfplumber && py manage.py migrate && py manage.py runserver 127.0.0.1:8080
```

Then open your browser to: **http://127.0.0.1:8080/**

### What this does:
1. Navigates to the project directory
2. Installs dependencies (Django, pdfplumber)
3. Runs database migrations
4. Starts the server on http://127.0.0.1:8080/

## Prerequisites

- Python 3.13
- Django 6.x
- SQLite3 (`db.sqlite3`)
- pdfplumber (install with `py -m pip install pdfplumber`)

## Full Setup (First Time)

1. Navigate to the project directory:
   ```powershell
   cd C:\Users\CALIXTOI\Downloads\Github\slewing-gear-motor
   ```

2. Install dependencies (if needed):
   ```powershell
   py -m pip install django pdfplumber
   ```

3. Run database migrations:
   ```powershell
   py manage.py migrate
   ```

4. Start the server:
   ```powershell
   py manage.py runserver 127.0.0.1:8080
   ```

5. Open your browser:
   - http://127.0.0.1:8080/

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Hot Reload

The development server automatically watches for file changes and reloads the application. Simply edit and save your Python files—no restart needed.

## Static Files

Static files (CSS, images, Bootstrap icons, KaTeX) are served automatically in development mode. If styles don't update, clear your browser cache.

## Database

The SQLite database (`db.sqlite3`) is created automatically on first run. Saved calculations are stored in this local database.

## Troubleshooting

- **Port 8080 already in use**: Use a different port:
  ```powershell
  py manage.py runserver 127.0.0.1:8000
  ```

- **Missing dependencies**: Install with:
  ```powershell
  py -m pip install -r requirements.txt
  ```
  (if `requirements.txt` exists)

- **Database errors**: Reset with:
  ```powershell
  py manage.py migrate --run-syncdb
  ```
