# Slewing Gear Calculator — Project Context

## What this is
Django 6.x web app for sizing slewing gear drivetrain motors on offshore cranes.
Local dev server: `py manage.py runserver` → http://127.0.0.1:8000/
Repo: https://github.com/calixtoi/slewing-gear-motor
Local clone: `C:\Users\CALIXTOI\Downloads\Github\slewing-gear-motor`
Network mirror (read-only reference): `\\satsbgc13fil21\ba\Marine\BU_Marine_Wind\02_Design_Wind\02_PROJECTS\PF_range\PF Redesign\10_Steuerung\Slewing Gear Motor\django_updates\`

## Stack
- Python 3.13, Django 6.x, SQLite3 (`db.sqlite3`)
- Bootstrap 5.3.3, Bootstrap Icons, KaTeX 0.16.11 (all via CDN)
- pdfplumber 0.11.9 for PDF extraction (`py -m pip install pdfplumber`)
- Use `py` (Python Launcher) — NOT `python` or `pip` directly (Windows alias issue)

## Key files
| File | Purpose |
|---|---|
| `calculator/models.py` | `MotorCalculation` model — all fields including spec fields |
| `calculator/forms.py` | `DrivetrainForm`, `MotorSpecsForm`, `SaveCalculationForm`, `DatasheetUploadForm`, `TextDatasheetForm` |
| `calculator/views.py` | All views; `_load_datasheet()`, `_effective_gearbox_speed()`, `FORMULAS` dict |
| `calculator/engine.py` | `drivetrain_sizing()` pure calculation; `SAFETY_FACTOR = 1.34` |
| `calculator/pdf_parser.py` | `parse_datasheet()`, `parse_text()`, `check_compliance()`, `_COMPLIANCE_RULES` |
| `calculator/urls.py` | URL routing |
| `calculator/templates/calculator/` | All HTML templates |
| `calculator/static/calculator/` | Static files (CSS, `bg.jpg` background) |

## No Django sessions
`settings.py` has no sessions middleware. Datasheet data passes between pages via hidden field `datasheet_data` (JSON). Helper: `_load_datasheet(request.POST)` in `views.py`.

## Crane types (model constants)
- `MotorCalculation.STANDARD_PF = 'standard_pf'`
- `MotorCalculation.PF_XXL = 'pf_xxl'`

---

## Implemented features

### Calculator (`/`)
- **DrivetrainForm** inputs: crane torques, worm ratio/efficiency, motor speed/torque/starting factor
- **Gearbox section**: `gearbox_output_speed` (optional) OR `gear_ratio` (optional) — at least one required
  - If `gear_ratio` is provided: `n_gear_out = n_motor / i` is computed automatically
  - Helper `_effective_gearbox_speed(d)` in `views.py` resolves which was given
  - `f4_inv` formula added: `n_gear_out = n_motor / i_bevel`
- **9-step calculation chain**: worm torques (max + nominal) → gearbox sizing → bevel ratio → slewing speed → motor torque check → motor power
- **Load spectrum gearbox sizing** (Steps GB1–GB4): optional, requires `M_Nenn`
- **Supplier data check**: margin and ratio deviation checks with PASS/MARGINAL/FAIL
- **Motor Specifications accordion**: 16 spec fields (compliance check against PF requirements)
- **Save to database**: saves full calculation + all spec fields

### Datasheet Import (`/upload/`)
- PDF upload → pdfplumber extraction → `parse_datasheet()`
- Text paste → `parse_text()`
- Both paths: compliance check, pre-fill spec form, show unrecognised fields for manual entry
- `crane_type` radio selector (Standard PF / PF-XXL)

### Motor Requirements (`/requirements/`)
- Design basis: M_Max = 62 000 Nm, i_worm = 150
- **Section 1** — Fixed parameters table
- **Section 2** — 8-row drivetrain requirements spec sheet; each row clickable → KaTeX formula + numeric derivation
  - Worm input torque M₂_max: 919–1181 Nm (η = 0.35–0.45)
  - Gearbox output speed: 37.5–52.5 rpm (n_slew = 0.25–0.35 rpm)
  - Bevel gear ratio (4-pole): 27.6–38.7
  - Required motor starting torque: 23.8–42.8 Nm
  - Motor rated torque: 6.8–14.3 Nm (Ma/Mn 3.0–3.5)
  - Starting factor: min 3.0, recommended 3.4
  - Motor rated power: 1.03–2.17 kW → IEC 1.1–2.2 kW (typical 1.5 kW)
  - Min gearbox catalogue torque (Step 3 method)
- **Section 3** — 15-row sizing matrix (5 η × 3 n_slew, Ma/Mn=3.4) with `↗ Verify` links that pre-fill the Calculator
- **Section 4** — Mechanical interface tables (motor side + gearbox/drive side)

### Formula Reference (`/formulas/`)
- Steps 1–9 with KaTeX, variable tables, purpose notes
- `f4_inv` inverse formula card: `n_gear_out = n_motor / i_bevel`
- Gearbox sizing load spectrum cards (GB1–GB4)
- Supplier check criteria

### Motor Comparison (`/comparison/`)
- All saved motors as columns, spec rows; filter tabs All / Standard PF / PF-XXL

### Saved Suppliers (`/suppliers/`)
- Per-crane-type lists; delete; detail view with full results

---

## Mechanical interface — PF crane (fixed constraints)

### Motor side
| Item | Value |
|---|---|
| Frame | IEC 90 B5 |
| Nominal flange disc | Ø160 mm |
| **Bolt circle (motor ↔ gearbox)** | **Ø165 mm** |
| Output shaft | Ø32k6 × 50 mm |
| Frame material | Cast Iron (GJL / GG) |

### Gearbox / drive side
| Item | Value |
|---|---|
| Gearbox input | IEC90 B5 · Ø165 mm (mates with motor) |
| **Gearbox output flange** | **Ø200 mm** (motor-side gearbox output) |
| Adapter flange | Ø200 mm → Ø165 mm |
| **Slewing drive input** | **Ø165 mm** (fixed constraint) |

> The Ø200 mm flange belongs to the bevel gearbox output shaft.
> It connects through an adapter flange before reaching the Ø165 mm slewing drive interface.
> These are two distinct flanges — do not confuse them.

---

## Motor compliance requirements (PF crane)

Checked by `check_compliance()` in `pdf_parser.py` (`_COMPLIANCE_RULES` list):

| Field key | Label | Required value |
|---|---|---|
| `spec_frame_material` | Motor Frame Material | Cast Iron (GJL / GG) |
| `spec_output_flange` | Motor Flange — IEC90 B5 | IEC90 B5 · Ø165 mm bolt circle |
| `spec_shaft` | Output Shaft | 32 × 50 mm (Ø32k6) |
| `spec_cooling_method` | Cooling Method | IC410 / TENV |
| `spec_ip_rating` | IP Rating | IP66 |
| `spec_ambient_temp` | Ambient Temperature | −20°C low end, +45°C high end |
| `spec_heater` | Standstill Heater | 24 VDC |
| `spec_coating` | Coating | C5H / EN 12944-5 |
| `spec_top_color` | Top Color | RAL7035 |
| `spec_voltage` | Voltage / Frequency | 400/690V 50Hz · 400/480/690V 60Hz |
| `spec_efficiency_class` | Efficiency Class | IE2 or higher |
| `spec_insulation_class` | Insulation Class | Class H |

---

## FORMULAS dict (views.py)
All raw LaTeX strings passed to every template via `**FORMULAS`:

| Key | Formula |
|---|---|
| `f1` | M₂_max = M_max / (i_worm × η) |
| `f2` | M₂_nom = M_nom / (i_worm × η) |
| `f3` | M_gear,req = M₂_nom × 1.34 |
| `f4` | i_bevel = n_motor / n_gear,out |
| `f4_inv` | n_gear,out = n_motor / i_bevel |
| `f5` | n_slew = n_gear,out / i_worm |
| `f6` | M_motor,req = M₂_max / i_bevel |
| `f7` | M_start = M_n × k_start |
| `f8` / `f8c` | Torque margin check |
| `f9` / `f9_inv` / `f9b` | P = M_n × n / 9550 |
| `fg1`–`fg4` / `fg4_exp` | Gearbox sizing (load spectrum) |
| `fs_margin` / `fs_ratio` | Supplier check criteria |

---

## Background image
Source: `\\Satsbgc13fil21\ba\Marine\BU_Marine_Wind\02_Design_Wind\02_PROJECTS\PF_range\PF Redesign\10_Steuerung\Slewing Gear Motor\20230602101923554.jpg`
Target: `calculator/static/calculator/bg.jpg`
Copy command: `Copy-Item "\\Satsbgc13fil21\ba\...\20230602101923554.jpg" "calculator\static\calculator\bg.jpg"`
