# Suppliers Motors App — Documentation

## Overview
The **Motors** app (`/motors/`) displays pre-configured supplier motor specifications and gearbox assemblies for the PF crane drivetrain. It includes the **Zsystems ZK43CV DM90-4 TS P2 (V2)** motor with full technical specifications.

## Features

### Motor List Page (`/motors/`)
- Table view of all available supplier motors
- Quick reference table showing:
  - Model number and name
  - Motor power (kW), speed (rpm), and torque (Nm)
  - Gearbox ratio, output speed, and output torque
  - "Details" button to view full specifications
- Responsive design with Bootstrap 5

### Motor Detail Page (`/motors/<model_number>/`)
- **Motor Specifications** (left column):
  - Power rating, speed, torque, starting torque
  - Voltage ratings (50Hz & 60Hz)
  - Frame size, flange type, output shaft
  - Cooling method, IP rating, insulation & efficiency class
  - Ambient temperature range
  - Heater, coating, color, power factor (when applicable)
  
- **Gearbox Specifications** (right column):
  - Model number, gear ratio, output speed & torque
  - Nominal torque, starting torque (max), tip-over torque (max)
  - Efficiency factor (CG), output flange & shaft specs
  - Oil capacity & oil type
  - Performance summary table (speed/torque reduction)

- **Compliance Status Badge**:
  - Green: ✓ Compliant — meets all PF crane requirements
  - Red: ✗ Non-compliant — with specific notes

- **Datasheet Link**: PDF link to supplier documentation (if available)

## Database Models

### `MotorSupplier`
Stores supplier information:
- `name`: Supplier name (e.g., "Zsystems")
- `country`: Supplier location

### `SupplierMotor`
Complete motor/gearbox assembly specification:

**Basic Info:**
- `model_number`: Unique model identifier
- `model_name`: Full product name
- `supplier`: Foreign key to MotorSupplier
- `crane_type`: STANDARD_PF or PF_XXL

**Motor Specs (20 fields):**
- Power, speed, torque (rated & starting)
- Voltages (50Hz & 60Hz)
- Frame, flange, shaft dimensions
- Cooling, IP rating, insulation & efficiency class
- Ambient temp range, heater, coating, color
- Power factor

**Gearbox Specs (12 fields):**
- Model, ratio, output speed & torque
- Nominal & starting torque
- Efficiency factor, flanges, shaft
- Oil capacity & type

**Compliance:**
- `compliant`: Boolean flag
- `compliance_notes`: Text description of compliance status
- `pdf_url`: Link to datasheet

**Metadata:**
- `created_at`: Timestamp
- `updated_at`: Timestamp

## URLs

```
/motors/                                          — Motor list (all suppliers)
/motors/<model_number>/                          — Motor detail page
```

## Admin Interface

Both models are registered in Django admin:
- Add/edit suppliers and motors
- Search by model number or name
- Filter by crane type and compliance status
- Organized fieldsets for easy data entry

## Initial Data — Zsystems ZK43CV DM90-4 TS P2 (V2)

**Motor:**
- 1.5 kW S3-15% @ 1415 rpm
- 10.2 Nm rated torque
- 67.877 Nm starting torque (Ma/Mn = 2.90)
- IEC 90 B5 frame, Ø165 mm bolt circle
- Ø32k6 × 50 mm output shaft
- 400V/690V (50Hz), 400V/480V/690V (60Hz)
- IP66, Class H insulation
- IC410/TENV cooling
- C5H coating (EN 12944-5), RAL7035 color
- 24V, 25W standstill heater
- −20…+45°C ambient range

**Gearbox (ZK43):**
- Ratio: 38.17:1
- Output: 37 rpm, 390 Nm
- Nominal torque: 760 Nm
- Starting torque (max): 1131 Nm
- Tip-over torque (max): 1326 Nm
- Efficiency factor (CG): 1.90
- Output flange: Ø200 mm
- Output shaft: Ø40×80 with keyway
- Oil: 1.8 L CLP VG220 mineral oil

**Compliance:** ✓ Fully compliant with PF crane requirements

## Management Command

Load initial data:
```bash
py manage.py load_zsystems
```

This creates the Zsystems supplier and the ZK43CV motor if they don't already exist.

## Integration

- **Navigation**: "Supplier Motors" link added to sidebar in calculator base template
- **Same look & feel**: Motors app shares the calculator's sidebar and styling
- **Easy access**: Link appears alongside Calculator, Datasheet Import, Comparison, Requirements, and Formulas

## Extending the App

### Adding New Suppliers

Option 1 — Via Django admin:
1. Navigate to `/admin/motors/motorsupplier/`
2. Click "Add Supplier"
3. Enter name and country
4. Save

Option 2 — Via management command (create a new command like `load_zsystems.py`)

### Adding New Motors

Option 1 — Via Django admin:
1. Navigate to `/admin/motors/suppliermotor/`
2. Click "Add Supplier Motor"
3. Fill in all motor and gearbox fields
4. Set compliance status and notes
5. Save

Option 2 — Create a management command (copy `load_zsystems.py` and modify)

Option 3 — Use a fixture or data migration

## Technical Notes

- Slug field: Motor list uses `model_number` as the URL slug (not auto-slug)
- Ordering: Motors ordered by `model_number` (alphabetically)
- NULL/BLANK fields: Most optional specs allow NULL values for motors without specific features
- Compliance: Boolean flag + text field allows detailed notes if non-compliant
- PDF URL: URLField allows internal file URLs or external links

## Files

| File | Purpose |
|---|---|
| `motors/models.py` | MotorSupplier & SupplierMotor models |
| `motors/views.py` | ListView & DetailView for motors |
| `motors/urls.py` | URL routing for motors app |
| `motors/admin.py` | Django admin registration |
| `motors/templates/motors/base.html` | Shared base template with sidebar |
| `motors/templates/motors/motor_list.html` | Motor list page |
| `motors/templates/motors/motor_detail.html` | Motor detail page |
| `motors/management/commands/load_zsystems.py` | Initial data loader |
