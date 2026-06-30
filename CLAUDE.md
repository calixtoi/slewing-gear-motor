# SlewingMotorSelector — Project Context

## What This Is

Django 6.x web application for sizing and verifying slewing drive motors for industrial offshore cranes.

**Objective:** Size a single motor to meet the electrical requirements of all PM010 crane variants (PF120, PF160, PF200) and the PM401 crane type.

**Key Concept:** Rather than design the motor to carry the full peak structural load, it is sized conservatively to deliver a minimum 30% share thereof. This approach is validated by proven PF200 historical performance (35% historical share) and ensures cost-effective motor selection while maintaining robust operation across all variants. The gearbox is nevertheless sized to withstand the full structural peak torque for overload protection.

**Sizing Basis:** The worst-case requirement across all variants is the Substation operation scenario on PM401 (62 kNm peak torque), making it the governing dimensioning constraint.

### Development Environment
- **Local dev server:** `py manage.py runserver 127.0.0.1:8080` → http://127.0.0.1:8080/
- **Repository:** https://github.com/calixtoi/slewing-gear-motor
- **Local clone:** `C:\Users\CALIXTOI\Downloads\Github\slewing-gear-motor`
- **Network mirror (read-only):** `\\satsbgc13fil21\ba\Marine\BU_Marine_Wind\02_Design_Wind\02_PROJECTS\PF_range\PF Redesign\10_Steuerung\Slewing Gear Motor\`

---

## Technology Stack

- **Backend:** Python 3.13, Django 4.2+, SQLite3 (`db.sqlite3`)
- **Frontend:** Bootstrap 5.3.3, Bootstrap Icons 1.11.3 (CDN)
- **Utilities:** pdfplumber 0.11.9 (PDF extraction), openai 1.0.0 (optional AI extraction)
- **Static files:** WhiteNoise 6.5.0 for production serving
- **Note:** Use `py` (Python Launcher) — NOT `python` or `pip` directly (Windows alias)

---

## Application Architecture

### Six Specialized Django Apps

| App | Purpose | Key Model | Key View |
|---|---|---|---|
| **core** | Landing page / dashboard | — | `HomeView` (TemplateView) |
| **cover** | Design parameters configuration | `DesignParameters` (pk=1 singleton) | `CoverView` (UpdateView) |
| **motor_cycle_calc** | 4-step motor sizing calculation | — | `MotorCycleCalcView` (TemplateView) |
| **ideal_parameters** | Specification requirement table (36 rows) | — | `IdealParametersView` (TemplateView) |
| **motor_verification** | Supplier datasheet comparison & validation | `MotorSupplier` (50+ fields) | `MotorVerificationListView` (ListView) |
| **formula_library** | Formula reference (all 8 formulas) | — | `FormulaLibraryView` (TemplateView) |

### Core Model: DesignParameters

A singleton model (pk=1) storing all design inputs that drive every calculation:

| Field | Default | Unit | Purpose |
|---|---|---|---|
| `crane_peak_torque_pf200_kNm` | 42.0 | kNm | Historical PF200 reference (for comparison) |
| `crane_peak_torque_tp_kNm` | 43.0 | kNm | PM010 Transport Position worst case |
| `crane_peak_torque_substation_kNm` | 62.0 | kNm | **PM401 Substation worst case (governing constraint)** |
| `slewing_ring_ratio_pm401` | 110.0 | — | Slewing ring gear ratio (110:1) |
| `slewing_ring_efficiency` | 0.40 | fraction | Slewing ring mechanical efficiency (40%) |
| `slewing_ring_ratio_pf200_ref` | 121.0 | — | PF200 reference ratio (for comparison) |
| `motor_torque_share_fraction` | 0.30 | fraction | Motor share of peak torque (30% design minimum) |
| `crane_max_slewing_speed_rpm` | 0.40 | rpm | Maximum crane slewing speed |
| `crane_min_slewing_speed_rpm` | 0.20 | rpm | Minimum crane slewing speed |

---

## Calculation Engine (Motor Cycle Calculation)

All results are computed dynamically in real time from DesignParameters. No stored calculated values.

### Step 1: Torque Cycle

| Variable | Formula | Result |
|---|---|---|
| Motor torque share | `0.30 × 62,000` | 18,600 N·m |
| Gearmotor output torque (duty) | `18,600 ÷ 110` | **169.1 N·m** (minimum requirement) |
| Gearmotor structural torque | `62,000 ÷ 110` | **563.6 N·m** (gearbox capacity) |
| Motor shaft torque (equiv.) | `169.1 ÷ 27.82` | 6.08 N·m (at 27.82 gearbox ratio) |

### Step 2: Speed Cycle

| Variable | Range | Unit |
|---|---|---|
| Gearmotor output speed | **22 – 44** | rpm |
| Gearbox internal ratio | **31.59 – 66.59** | — |
| Motor rated speed band (4-pole) | 1390 – 1465 | rpm |

### Step 3: Power & Motor Selection

| Variable | Calculation | Unit |
|---|---|---|
| Gearbox mechanical efficiency | constant | 0.90 (90%) |
| Required motor power | `169.1 × 44 ÷ 9550 ÷ 0.90` | **0.866 kW** |
| Selected motor power | round UP to 0.25 kW step | **1.00 kW** (IEC standard) |

### Step 4: Duty Cycle & Thermal

| Variable | Value | Unit |
|---|---|---|
| Duty class | S3-25% | — |
| Thermal-equivalent S1 power | `0.866 × √0.25` | **0.433 kW** |

---

## Specification Requirements (Ideal Parameters)

A 36-row table organized into 6 groups, with computed min/max values updated live from DesignParameters:

### Groups

1. **Gear data** (10 rows): series, output speed, output torque, internal ratio, flange, shaft, keyway, paint, colour
2. **Input side** (3 rows): type, mounting, flange
3. **Motor data** (10 rows): housing, duty, efficiency, power, speed, torque, voltage, frequency, winding, protection
4. **Further motor executions** (2 rows): cooling, heater
5. **General** (8 rows): certifications, corrosivity, temperature, rotation, starting, heater blocks, structural capacity, speed window

### Computed Fields (Blue-Highlighted)

- Gearmotor output speed range: 22 – 44 rpm
- Gearmotor output torque: ≥ 169.1 N·m
- Gearbox internal ratio: 31.59 – 66.59
- Motor rated power: 0.75 – 1.50 kW
- Motor rated torque: 4.89 – 10.31 N·m
- Gearbox structural capacity: ≥ 563.6 N·m
- Crane slewing speed window: 0.20 – 0.40 rpm

---

## Motor Verification: Supplier Comparison

### MotorSupplier Model

50+ fields grouped into 7 categories:
- **Gear data** (gearmotor output speed/torque, gearbox ratio, flange, shaft, keyway, paint, colour)
- **Input side** (flange description)
- **Motor data** (housing, duty, efficiency, power, speed, voltage, frequency, winding, protection, cable entries)
- **Further executions** (cooling, heater, weight)
- **General** (certifications, temperature, corrosivity, rotation, starting, heater blocks, structural capacity)
- **Metadata** (supplier name, motor model, datasheet source, notes, created/updated timestamps)

### Validation Rules

18+ automated validation checks (via `validate_supplier()` in `validators.py`):

**Numeric specs:**
- Output speed: must be within 22 – 44 rpm
- Output torque: must be ≥ 169.1 N·m
- Gearbox internal ratio: must be within 31.59 – 66.59
- Motor rated power: must be within 0.75 – 1.50 kW
- Motor rated speed: must be within 1390 – 1465 rpm
- Motor rated torque (computed): must fall within required envelope
- Structural capacity: must be ≥ 563.6 N·m
- Crane slewing speed (derived): must be within 0.20 – 0.40 rpm

**Categorical specs:**
- Protection class: IP66 required
- Efficiency class: IE2 or IE3
- Housing material: Cast iron expected
- Duty cycle: S3-25% expected
- Corrosivity category: C5H expected
- Certifications: CE, EN 10204 Type 3.1, etc.
- Cooling method: IC410 TENV expected

**Status Badges:**
- **PASS** (green): Meets requirement
- **CHECK** (amber): Needs manual review or not provided
- **FAIL** (red): Does not meet requirement

### Supplier Summary

Overall result badge per supplier:
- **SUITABLE** (green): Zero FAILs and fewer than 5 CHECKs
- **REVIEW** (amber): Zero FAILs but 5 or more CHECKs
- **NOT FIT** (red): One or more FAILs

### Data Entry Methods (Three Tabs)

1. **Manual Entry:** Standard Django form with 50+ fields grouped into sections
2. **Paste Text:** Extract supplier data from unstructured text (email, quote, PDF copy-paste)
   - Regex-based extraction with 20+ patterns
   - Optional AI extraction via OpenAI GPT (if `OPENAI_API_KEY` is set)
3. **Upload PDF:** Extract from PDF datasheet
   - Uses pdfplumber to extract text from all pages
   - Applies same extraction logic as text mode
   - Stores original PDF filename as source reference

### Extraction Patterns

Regex patterns extract:
- Rated power (kW): `(\d+[\.,]\d*)\s*kW`
- Rated speed (rpm): `(\d{3,4})\s*r\.?p\.?m\.?`
- Output torque (N·m): `(\d+[\.,]\d*)\s*N\.?m\.?`
- Gear ratio: `[iI]\s*=\s*(\d+[\.,]\d*)` or `ratio:\s*(\d+[\.,]\d*)`
- IP rating: `IP\s*(\d{2})`
- Supply voltage: `(\d{3})\s*/\s*(\d{3})\s*V`
- RAL colour: `RAL\s*(\d{4})`
- Corrosivity: `C[45][HhMm]`
- Weight: `(\d+[\.,]\d*)\s*kg`
- Certifications: keywords (CE, UL, UKCA, EN 10204, 3.1)
- Duty cycle: S3 keyword
- Efficiency class: IE2, IE3 keywords
- Cooling: IC410, TENV keywords

---

## Formula Library

All 8 formulas with:
- Symbolic representation
- Full plain-English explanation (no abbreviations)
- Variable definitions
- Example calculations
- Source and usage cross-references

### Formulas Included

| ID | Name | Usage |
|---|---|---|
| F01 | Motor torque share of crane peak load | Step 1 |
| F02 | Required gearmotor output torque | Step 1 (result) |
| F03 | Required gearmotor structural torque | Step 1 (capacity) |
| F04 | Gearmotor output speed range | Step 2 |
| F05 | Gearbox internal ratio speed window | Step 2 (envelope) |
| F06 | Required motor rated power | Step 3 |
| F07 | Selected standard motor power rating | Step 3 (IEC selection) |
| F08 | Thermal-equivalent S1 power at S3-25% | Step 4 (duty cycle) |

---

## Key Files & Structure

```
slewing-gear-motor/
├── slewing_calculator/              # Django project settings
│   ├── settings.py                  # Installed apps, middleware, DB config
│   ├── urls.py                      # Route definitions (11 URLs)
│   ├── wsgi.py
│   └── asgi.py
├── core/                            # App 1: Home page
│   ├── views.py                     # HomeView (TemplateView)
│   └── templates/core/home.html     # Dashboard with 5 app cards + status banner
├── cover/                           # App 2: Design Parameters
│   ├── models.py                    # DesignParameters singleton model (9 fields)
│   ├── forms.py                     # DesignParametersForm (ModelForm)
│   ├── views.py                     # CoverView (UpdateView)
│   ├── migrations/
│   └── templates/cover/cover.html   # Executive summary, key results, form
├── motor_cycle_calc/                # App 3: Calculation Engine
│   ├── views.py                     # MotorCycleCalcView (TemplateView, 14 calculated values)
│   └── templates/motor_cycle_calc/calc.html   # 4-step results with badges
├── ideal_parameters/                # App 4: Spec Table
│   ├── views.py                     # IdealParametersView (36-row spec table)
│   └── templates/ideal_parameters/parameters.html   # Accordion-grouped table
├── motor_verification/              # App 5: Supplier Verification
│   ├── models.py                    # MotorSupplier (50+ fields)
│   ├── forms.py                     # MotorSupplierForm, PdfUploadForm, TextPasteForm
│   ├── views.py                     # 6 views (list, add, edit, delete, extract)
│   ├── validators.py                # validate_supplier() + get_supplier_summary()
│   ├── extractors.py                # extract_from_text() + extract_from_pdf()
│   ├── migrations/
│   └── templates/motor_verification/
│       ├── list.html                # Comparison table (scrollable side-by-side)
│       ├── add_edit.html            # 3-tab entry form
│       └── confirm_delete.html      # Delete confirmation
├── formula_library/                 # App 6: Formula Reference
│   ├── views.py                     # FormulaLibraryView (8 formulas + search)
│   └── templates/formula_library/formulas.html   # Cards with expandable definitions
├── templates/
│   └── base.html                    # Global template (navbar, breadcrumbs, footer)
├── manage.py                        # Django CLI
├── db.sqlite3                       # SQLite database
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                        # This file
└── SETUP_INSTRUCTIONS.md            # Setup & troubleshooting guide
```

---

## URL Routes

| URL | View | Purpose |
|---|---|---|
| `/` | `core.HomeView` | Home page / dashboard |
| `/cover/` | `cover.CoverView` | Edit design parameters, view key results |
| `/calc/` | `motor_cycle_calc.MotorCycleCalcView` | 4-step motor sizing calculation |
| `/parameters/` | `ideal_parameters.IdealParametersView` | 36-row specification table |
| `/verification/` | `motor_verification.MotorVerificationListView` | Supplier comparison |
| `/verification/add/` | `motor_verification.SupplierAddView` | Add new supplier |
| `/verification/<id>/edit/` | `motor_verification.SupplierEditView` | Edit supplier |
| `/verification/<id>/delete/` | `motor_verification.SupplierDeleteView` | Delete supplier |
| `/verification/extract-text/` | `motor_verification.ExtractFromTextView` | Extract from pasted text (AJAX) |
| `/verification/extract-pdf/` | `motor_verification.ExtractFromPdfView` | Extract from PDF upload (AJAX) |
| `/formulas/` | `formula_library.FormulaLibraryView` | Formula library with search |

---

## Development Notes

### Database & Migrations

- Initial migrations created and applied for `cover` and `motor_verification` apps
- DesignParameters singleton auto-created on first access to `/cover/` with default values
- All calculations fetch the singleton dynamically (no stale data)

### Static Files & CDN

- Bootstrap 5.3.3 CSS/JS via CDN
- Bootstrap Icons 1.11.3 via CDN
- No local CSS files needed for core functionality
- WhiteNoise configured for production static file serving

### Optional AI Integration

- If `OPENAI_API_KEY` environment variable is set, text extraction uses GPT-3.5-turbo
- Falls back gracefully to regex-based extraction if API unavailable
- Used on the "Paste Text" tab of motor verification form

### Color Scheme

- **PASS badge:** Bootstrap success (#198754 green)
- **CHECK badge:** Bootstrap warning (#ffc107 amber)
- **FAIL badge:** Bootstrap danger (#dc3545 red)
- **Header bars:** Bootstrap primary (#0d6efd blue)

---

## Crane Type Hierarchy

```
PF-Redesign (SAP: PM010)
├── PF120 (light variant)
├── PF160 (medium variant)
└── PF200 (heavy variant)

PM401 (separate product line, Substation focus)
```

**Motor Sizing Strategy:** One motor for ALL PM010 variants + PM401, sized to the worst-case requirement (PM401 Substation: 62 kNm peak).

---

## Next Steps for Development

1. **Run the server:** `py manage.py runserver 127.0.0.1:8080`
2. **Visit home page:** http://127.0.0.1:8080/
3. **Edit design parameters:** `/cover/` → adjust input values
4. **View calculations:** `/calc/` → auto-updates from DesignParameters
5. **Check spec table:** `/parameters/` → shows computed min/max
6. **Add suppliers:** `/verification/` → manual, text, or PDF entry
7. **Reference formulas:** `/formulas/` → full definitions + examples

---

## Contact & Support

**User Email:** ian.calixto@gmail.com  
**Git Repository:** https://github.com/calixtoi/slewing-gear-motor  
**For help:** See `SETUP_INSTRUCTIONS.md` or run `py manage.py --help`
