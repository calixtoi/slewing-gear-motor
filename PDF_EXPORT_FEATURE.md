# PDF Export Feature — Motor Specifications

## Overview
The Motors app now includes **professional PDF export** functionality that generates detailed specification sheets for any motor in the database. PDFs are automatically formatted with explanations, performance metrics, and compliance status.

## Features

### PDF Content
Each PDF includes:

1. **Header Section**
   - Motor model number and name
   - Compliance status badge (✓ Compliant or ✗ Non-Compliant)

2. **Motor Specifications Table** (17+ parameters)
   - Power rating, speed, torque (rated & starting)
   - Voltages (50Hz & 60Hz) with frequency support
   - Frame size, flange type, shaft specifications
   - Cooling, IP rating, insulation & efficiency class
   - Ambient temperature range
   - Heater, coating, color options

3. **Gearbox Specifications Table** (10+ parameters)
   - Model, gear ratio, output speed & torque
   - Nominal & starting torque ratings
   - Efficiency factor (CG)
   - Output flange & shaft specifications
   - Oil capacity & lubrication type

4. **Parameter Descriptions**
   - Each row includes a "Description" column
   - Explains engineering meaning and importance
   - Examples: "IP66 = sealed dust & water resistant", "IE2 = energy efficiency class"

5. **Performance Summary**
   - Input/output speed comparison
   - Input/output torque comparison
   - Speed reduction and torque multiplication ratios

6. **Professional Formatting**
   - Color-coded headers (blue background with white text)
   - Alternating row colors for readability
   - Proper alignment and spacing
   - Clean borders and sections
   - Professional footer with generation timestamp

## Usage

### Download from Web Interface
1. Navigate to motor detail page: `http://127.0.0.1:8080/motors/<model_number>/`
2. Click the **"Download PDF"** button in the top-right corner
3. File downloads as `<model_number>_specs.pdf`

### Direct PDF URL
Access PDF directly via: `http://127.0.0.1:8080/motors/<model_number>/pdf/`

Example for Zsystems motor:
```
http://127.0.0.1:8080/motors/ZK43CV%20DM90-4%20TS%20P2%20(V2)/pdf/
```

## Technical Details

### Files
- `motors/pdf_export.py` — PDF generation utility using ReportLab
- `motors/views.py` — `motor_pdf_export()` view function
- `motors/urls.py` — PDF route added
- `motors/templates/motors/motor_detail.html` — Download button

### PDF Library
- **ReportLab** (reportlab): Professional PDF generation
- Supports tables, styles, colors, custom fonts
- Generates landscape-compatible layout

### PDF Specifications
- **Format**: PDF 1.4
- **Size**: ~6-8 KB per motor (depends on content)
- **Pages**: 2 pages per motor
- **Encoding**: UTF-8 with embedded fonts

## Zsystems Motor PDF

The Zsystems ZK43CV DM90-4 TS P2 (V2) PDF includes:

**Motor Section:**
- 1.5 kW S3-15% @ 1415 rpm
- 10.2 Nm rated torque, 67.877 Nm starting torque (Ma/Mn=2.90)
- IEC 90 B5 frame, Ø165 mm bolt circle
- Ø32k6 × 50 mm output shaft
- 400V/690V (50Hz) & 400V/480V/690V (60Hz)
- IP66, Class H insulation, IE2+ efficiency
- IC410/TENV cooling, 24V standstill heater
- C5H coating (EN 12944-5), RAL7035 light gray
- −20…+45°C ambient temperature range

**Gearbox Section:**
- ZK43 model with 38.17:1 ratio
- 37 rpm output, 390 Nm output torque
- 760 Nm nominal torque, 1131 Nm starting (max)
- 1326 Nm tip-over (stall) torque
- 1.90 CG efficiency factor
- Ø200 mm output flange, Ø40×80 shaft
- 1.8 L CLP VG220 mineral oil

**Compliance:**
- ✓ Fully compliant with PF crane requirements
- Meets motor, gearbox, cooling, and environmental specifications

## Future Enhancements

### Possible Additions
1. **Multi-language support** — German, French, Spanish, Mandarin
2. **Bulk PDF export** — Download specs for multiple motors at once
3. **Custom report builder** — Select which sections to include
4. **Logo/watermark** — Add Palfinger/company branding
5. **Email delivery** — Send PDF by email
6. **Cloud storage** — Save to Google Drive, OneDrive, etc.

### Performance Optimization
- Cache generated PDFs for faster delivery
- Lazy-load PDF generation on request
- Compress PDFs for smaller file sizes

## Installation

ReportLab is already installed:
```bash
pip install reportlab
```

If needed to reinstall:
```bash
pip install reportlab --upgrade
```

## Support

- **Issue**: PDF doesn't download
  → Ensure browser allows PDF downloads
  → Check browser console for errors

- **Issue**: PDF looks wrong
  → Clear browser cache
  → Verify motor data is complete in database

- **Issue**: Slow PDF generation
  → Normal for first request (ReportLab rendering)
  → Subsequent requests may be cached by browser

## Files Modified/Created

| File | Status | Purpose |
|---|---|---|
| `motors/pdf_export.py` | **Created** | PDF generation engine |
| `motors/views.py` | **Modified** | Added motor_pdf_export() view |
| `motors/urls.py` | **Modified** | Added PDF route |
| `motors/templates/motors/motor_detail.html` | **Modified** | Added Download button |
| `requirements.txt` | **Check** | Verify reportlab listed |

## Testing

```bash
# Test PDF generation from Django shell
python manage.py shell

from motors.models import SupplierMotor
from motors.pdf_export import generate_motor_pdf

motor = SupplierMotor.objects.first()
pdf = generate_motor_pdf(motor)
print(pdf.getvalue()[:100])  # Print first 100 bytes
```

## License & Attribution
- ReportLab: BSD License (permissive, commercial use allowed)
- PDF generation custom code: Palfinger 2026
