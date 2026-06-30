"""Extract motor supplier data from text and PDF sources."""

import re
import os
import json
import pdfplumber


def extract_from_text(raw_text):
    """Extract supplier data from unstructured text using regex patterns."""
    extracted = {}

    # Rated power (kW)
    power_match = re.search(r'(\d+[\.,]\d*)\s*kW', raw_text, re.IGNORECASE)
    if power_match:
        extracted['motor_rated_power_kw'] = float(power_match.group(1).replace(',', '.'))

    # Rated speed (rpm)
    speed_match = re.search(r'(\d{3,4})\s*r\.?p\.?m\.?', raw_text, re.IGNORECASE)
    if speed_match:
        extracted['motor_rated_speed_rpm'] = float(speed_match.group(1))

    # Output torque (N·m)
    torque_match = re.search(r'(\d+[\.,]\d*)\s*N\.?m\.?', raw_text, re.IGNORECASE)
    if torque_match:
        extracted['gearmotor_output_torque_nm'] = float(torque_match.group(1).replace(',', '.'))

    # Gear ratio
    ratio_match = re.search(r'[iI]\s*=\s*(\d+[\.,]\d*)', raw_text)
    if not ratio_match:
        ratio_match = re.search(r'ratio[:\s]+(\d+[\.,]\d*)', raw_text, re.IGNORECASE)
    if ratio_match:
        extracted['gearbox_internal_ratio'] = float(ratio_match.group(1).replace(',', '.'))

    # Output speed (rpm)
    output_speed_match = re.search(r'output\s+speed[:\s]+(\d+[\.,]\d*)\s*rpm', raw_text, re.IGNORECASE)
    if output_speed_match:
        extracted['gearmotor_output_speed_rpm'] = float(output_speed_match.group(1).replace(',', '.'))

    # IP rating
    ip_match = re.search(r'IP\s*(\d{2})', raw_text, re.IGNORECASE)
    if ip_match:
        extracted['protection_class'] = f"IP{ip_match.group(1)}"

    # Supply voltage
    voltage_match = re.search(r'(\d{3})\s*/\s*(\d{3})\s*V', raw_text)
    if voltage_match:
        extracted['supply_voltage_v'] = f"{voltage_match.group(1)} / {voltage_match.group(2)} V"
    else:
        voltage_match = re.search(r'(\d{3})\s*V', raw_text)
        if voltage_match:
            extracted['supply_voltage_v'] = f"{voltage_match.group(1)} V"

    # RAL colour
    ral_match = re.search(r'RAL\s*(\d{4})', raw_text)
    if ral_match:
        extracted['colour_ral'] = f"RAL {ral_match.group(1)}"

    # Corrosivity category
    corr_match = re.search(r'C[45][HhMm]', raw_text)
    if corr_match:
        extracted['corrosivity_category'] = corr_match.group(0).upper()

    # Weight (kg)
    weight_match = re.search(r'(\d+[\.,]\d*)\s*kg', raw_text, re.IGNORECASE)
    if weight_match:
        extracted['total_weight_kg'] = float(weight_match.group(1).replace(',', '.'))

    # Certifications
    certs = []
    if 'CE' in raw_text.upper():
        certs.append('CE')
    if re.search(r'EN\s*10204|3\.1', raw_text):
        certs.append('EN 10204 Type 3.1')
    if 'UL' in raw_text.upper():
        certs.append('UL')
    if 'CSA' in raw_text.upper():
        certs.append('CSA')
    if 'UKCA' in raw_text.upper():
        certs.append('UKCA')
    if certs:
        extracted['certifications'] = ', '.join(certs)

    # Duty cycle
    if 'S3' in raw_text:
        extracted['duty_cycle'] = 'S3-25%'

    # Efficiency class
    eff_match = re.search(r'IE([234])', raw_text)
    if eff_match:
        extracted['efficiency_class'] = f"IE{eff_match.group(1)}"

    # Cooling method
    if 'IC410' in raw_text or 'TENV' in raw_text:
        extracted['cooling_method'] = 'IC410 TENV'

    # Housing material
    if 'cast iron' in raw_text.lower():
        extracted['housing_material'] = 'Cast iron'

    return extracted


def extract_from_pdf(pdf_file):
    """Extract supplier data from PDF using pdfplumber."""
    extracted = {}

    try:
        with pdfplumber.open(pdf_file) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() or ""

            # Store original filename as source
            extracted['datasheet_source'] = pdf_file.name

            # Use text extraction method on concatenated text
            text_extracted = extract_from_text(full_text)
            extracted.update(text_extracted)

            # Try to extract drawing/document number
            doc_num_match = re.search(
                r'(?:drawing|document|drg|dwg)[^\d]*([A-Z]{2}\.\d{8})',
                full_text,
                re.IGNORECASE
            )
            if doc_num_match:
                extracted['datasheet_source'] = doc_num_match.group(1)

            # Try to extract motor frame size
            frame_match = re.search(r'IEC\s*(\d{2,3})', full_text)
            if frame_match:
                # Could store in a field if needed
                pass

            # Try to extract mounting code
            mount_match = re.search(r'\b(M[2-9]|B[145])\b', full_text)
            if mount_match:
                extracted['mounting_position'] = mount_match.group(1)

    except Exception as e:
        extracted['error'] = str(e)

    return extracted


def use_openai_extraction(raw_text):
    """
    Optional: Use OpenAI GPT to extract supplier data from unstructured text.
    Requires OPENAI_API_KEY environment variable to be set.
    Falls back to regex extraction if API call fails.
    """
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return None

    try:
        import openai
        openai.api_key = api_key

        prompt = f"""Extract motor supplier data from the following text and return a JSON object with these fields (use null for missing values):

{{
    "supplier_name": "string",
    "motor_model": "string",
    "datasheet_source": "string",
    "motor_rated_power_kw": number,
    "motor_rated_speed_rpm": number,
    "gearmotor_output_torque_nm": number,
    "gearmotor_output_speed_rpm": number,
    "gearbox_internal_ratio": number,
    "protection_class": "string",
    "supply_voltage_v": "string",
    "supply_frequency_hz": "string",
    "efficiency_class": "string",
    "housing_material": "string",
    "duty_cycle": "string",
    "cooling_method": "string",
    "heater_spec": "string",
    "certifications": "string",
    "temperature_range": "string",
    "corrosivity_category": "string",
    "colour_ral": "string",
    "painting_system": "string",
    "winding_connection": "string",
    "rotation": "string",
    "starting_method": "string",
    "gearbox_structural_capacity_nm": number
}}

Text to extract from:
{raw_text[:3000]}  # Limit to first 3000 chars to save tokens

Return ONLY the JSON object, no other text."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical data extraction assistant. Extract specifications from supplier datasheets."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        json_str = response['choices'][0]['message']['content'].strip()
        extracted = json.loads(json_str)

        # Clean up None values
        return {k: v for k, v in extracted.items() if v is not None}

    except Exception as e:
        # Silently fail and fall back to regex
        return None
