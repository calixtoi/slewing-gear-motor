# Slewing Motor Selector — Setup Instructions

## Fresh Setup

### 1. Install Python 3.13+

Ensure Python 3.13 or later is installed on your system.

### 2. Install Dependencies

```bash
cd C:\Users\CALIXTOI\Downloads\Github\slewing-gear-motor
py -m pip install -r requirements.txt
```

### 3. Create Migrations (Already Done)

Migrations have been created and applied. To verify:

```bash
py manage.py showmigrations
```

All migrations should show as `[X]` (applied).

### 4. Create a Superuser (Admin Account)

If you want to access the Django admin panel:

```bash
py manage.py createsuperuser
```

Follow the prompts to create a username, email, and password.

Example:
```
Username: admin
Email: ian.calixto@gmail.com
Password: ••••••••
```

### 5. Initialize Design Parameters

The DesignParameters singleton will be created automatically on first access to the Cover page. Alternatively, create it manually:

```bash
py manage.py shell
```

Then in the shell:

```python
from cover.models import DesignParameters
dp = DesignParameters.get_or_create_default()
print(f"Design Parameters initialized: {dp}")
exit()
```

### 6. Run the Development Server

```bash
py manage.py runserver 127.0.0.1:8080
```

Open your browser to **http://127.0.0.1:8080/**

## URL Routes

- **Home**: http://127.0.0.1:8080/
- **Cover (Design Parameters)**: http://127.0.0.1:8080/cover/
- **Motor Cycle Calculation**: http://127.0.0.1:8080/calc/
- **Ideal Motor Parameters**: http://127.0.0.1:8080/parameters/
- **Motor Verification**: http://127.0.0.1:8080/verification/
- **Formula Library**: http://127.0.0.1:8080/formulas/
- **Django Admin**: http://127.0.0.1:8080/admin/ (requires superuser login)

## Project Structure

```
slewing-gear-motor/
├── slewing_calculator/          # Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # URL routing
│   ├── wsgi.py
│   └── asgi.py
├── core/                        # App 1: Landing page / dashboard
├── cover/                       # App 2: Design parameters
├── motor_cycle_calc/            # App 3: Motor sizing calculation
├── ideal_parameters/            # App 4: Specification table
├── motor_verification/          # App 5: Supplier comparison
├── formula_library/             # App 6: Formula reference
├── templates/                   # Global templates (base.html)
├── manage.py                    # Django management script
├── requirements.txt             # Python package dependencies
└── db.sqlite3                   # SQLite database
```

## Key Features

### 1. Cover Sheet
- Editable design parameters that control all calculations
- Executive summary and design principles
- Live calculation of key results
- All parameters are stored in a singleton DesignParameters model

### 2. Motor Cycle Calculation
- **Step 1**: Torque cycle (motor torque share, required output torque, structural torque)
- **Step 2**: Speed cycle (output speed range, gearbox ratio bounds)
- **Step 3**: Power calculation (required power, motor selection)
- **Step 4**: Duty cycle analysis (thermal equivalent S1 power at S3-25%)
- All values computed dynamically from DesignParameters

### 3. Ideal Motor Parameters
- 36 specification rows organized into 6 groups:
  - Gear data
  - Input side
  - Motor data
  - Further motor executions
  - General
- Min/max columns computed from DesignParameters (highlighted in blue)
- Static requirements for categorical specifications

### 4. Motor Verification
- Add motor suppliers via:
  - **Manual entry**: Fill out all fields
  - **Text extraction**: Paste supplier email/quote, extract with regex or AI
  - **PDF upload**: Extract from datasheet using pdfplumber
- Validation rules check:
  - Numeric specs (speed, torque, power, etc.)
  - Categorical specs (IP rating, efficiency class, certifications)
  - Derived values (motor rated torque, crane slewing speed)
- Colour-coded badges: **PASS** (green), **CHECK** (amber), **FAIL** (red)
- Supplier summary: SUITABLE / REVIEW / NOT FIT

### 5. Formula Library
- 8 core formulas with full symbolic and expanded English versions
- Variable definitions with no abbreviations
- Example calculations
- Source and usage cross-references
- Real-time search filtering

## Optional: OpenAI Integration

To enable AI-powered text extraction for motor verification:

1. Set the `OPENAI_API_KEY` environment variable:
   ```bash
   $env:OPENAI_API_KEY = 'sk-...'
   ```

2. On the "Paste Text" tab in Motor Verification, check "Use AI extraction"

3. The system will attempt to use GPT-3.5-turbo to extract data from unstructured text, falling back to regex if the API call fails.

## Troubleshooting

### `ModuleNotFoundError: No module named 'bootstrap5'`
→ Run `py -m pip install -r requirements.txt` again

### `TemplateDoesNotExist: base.html`
→ Ensure `TEMPLATES['DIRS']` in settings.py includes `BASE_DIR / 'templates'`

### Database locked error
→ Delete `db.sqlite3` and run `py manage.py migrate` again

### Port 8080 already in use
→ Use a different port: `py manage.py runserver 127.0.0.1:8000`

## Static Files (Production)

For production deployment, collect static files:

```bash
py manage.py collectstatic
```

This creates a `staticfiles/` directory with compressed, versioned assets using WhiteNoise.

## Git Workflow

To commit this new structure to git:

```bash
git add -A
git commit -m "refactor: rebuild application with new SlewingMotorSelector structure

- Create 6 specialized Django apps: core, cover, motor_cycle_calc, ideal_parameters, motor_verification, formula_library
- Implement DesignParameters singleton model for centralized configuration
- Add comprehensive motor sizing calculation engine with multi-step workflow
- Build motor verification system with validation rules and supplier comparison
- Implement text/PDF extraction for datasheet parsing (regex + optional OpenAI)
- Create formula library with full plain-English explanations
- Design responsive Bootstrap 5 UI with navigation and status warnings
- Configure SQLite database with all models and migrations"
```

## Next Steps

1. Start the development server: `py manage.py runserver 127.0.0.1:8080`
2. Visit http://127.0.0.1:8080/ to see the home page
3. Navigate to **Cover** to edit design parameters
4. Go to **Motor Cycle Calculation** to see the sizing results
5. Add suppliers in **Motor Verification** to compare options
6. Consult **Formula Library** for detailed calculations

---

**Built with:**
- Django 4.2+
- Bootstrap 5.3.3
- SQLite3
- pdfplumber (PDF extraction)
- Optional: OpenAI API (AI text extraction)
