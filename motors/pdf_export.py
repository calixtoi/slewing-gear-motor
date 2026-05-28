from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def generate_motor_pdf(motor):
    """Generate a simple, clean PDF specification sheet"""

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.2*cm, bottomMargin=1*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
    story = []

    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(motor.model_number, title_style))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    story.append(Paragraph(motor.model_name, subtitle_style))

    # Compliance Badge
    if motor.compliant:
        comp_text = "<font color='#155724' size=10><b>✓ COMPLIANT</b> with PF crane requirements</font>"
        comp_bg = colors.HexColor('#d4edda')
    else:
        comp_text = "<font color='#721c24' size=10><b>✗ NOT COMPLIANT</b></font>"
        comp_bg = colors.HexColor('#f8d7da')

    comp_style = ParagraphStyle('Comp', parent=styles['Normal'], alignment=TA_CENTER, backColor=comp_bg, leftIndent=8, rightIndent=8, topPadding=5, bottomPadding=5)
    story.append(Paragraph(comp_text, comp_style))
    story.append(Spacer(1, 0.4*cm))

    # ─── MOTOR SPECIFICATIONS ───
    story.append(Paragraph("MOTOR SPECIFICATIONS", ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, textColor=colors.white, backColor=colors.HexColor('#0d6efd'), spaceAfter=6, spaceBefore=0, fontName='Helvetica-Bold', leftIndent=6, rightIndent=6, topPadding=6, bottomPadding=6)))

    motor_data = [
        ["Power Rating", f"{motor.motor_power} kW (S3-15%)"],
        ["Rated Speed", f"{motor.motor_speed} rpm"],
        ["Rated Torque", f"{motor.motor_torque} Nm"],
        ["Starting Torque (Max)", f"{motor.motor_starting_torque} Nm"],
        ["Starting Factor (Ma/Mn)", f"{motor.motor_starting_factor}"],
        ["Voltage 50Hz", motor.motor_voltage_50hz],
        ["Voltage 60Hz", motor.motor_voltage_60hz],
        ["Power Factor (cosφ)", f"{motor.motor_power_factor if motor.motor_power_factor else '—'}"],
        ["Frame Size", motor.motor_frame],
        ["Flange Type", motor.motor_flange],
        ["Output Shaft", motor.motor_shaft],
        ["Cooling Method", motor.motor_cooling],
        ["IP Rating", motor.motor_ip_rating],
        ["Insulation Class", motor.motor_insulation_class],
        ["Efficiency Class", motor.motor_efficiency_class],
        ["Ambient Temperature", f"{motor.motor_ambient_temp_min}…{motor.motor_ambient_temp_max}°C"],
    ]

    if motor.motor_heater:
        motor_data.append(["Standstill Heater", motor.motor_heater])
    if motor.motor_coating:
        motor_data.append(["Coating (Corrosion Protection)", motor.motor_coating])
    if motor.motor_color:
        motor_data.append(["Color", motor.motor_color])

    motor_table = Table(motor_data, colWidths=[4.5*cm, 10*cm])
    motor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(motor_table)
    story.append(Spacer(1, 0.3*cm))

    # ─── GEARBOX SPECIFICATIONS ───
    story.append(Paragraph("GEARBOX SPECIFICATIONS", ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, textColor=colors.white, backColor=colors.HexColor('#0d6efd'), spaceAfter=6, spaceBefore=0, fontName='Helvetica-Bold', leftIndent=6, rightIndent=6, topPadding=6, bottomPadding=6)))

    gearbox_data = [
        ["Gearbox Model", motor.gearbox_model],
        ["Gear Ratio", f"{motor.gearbox_ratio}:1"],
        ["Output Speed", f"{motor.gearbox_output_speed} rpm"],
        ["Output Torque", f"{motor.gearbox_output_torque} Nm"],
    ]

    if motor.gearbox_nominal_torque:
        gearbox_data.append(["Nominal Torque (Rated)", f"{motor.gearbox_nominal_torque} Nm"])
    if motor.gearbox_starting_torque_max:
        gearbox_data.append(["Starting Torque (Max)", f"{motor.gearbox_starting_torque_max} Nm"])
    if motor.gearbox_tip_torque_max:
        gearbox_data.append(["Tip-Over Torque (Max)", f"{motor.gearbox_tip_torque_max} Nm"])
    if motor.gearbox_efficiency_factor:
        gearbox_data.append(["Efficiency Factor (CG)", f"{motor.gearbox_efficiency_factor}"])

    gearbox_data.extend([
        ["Output Flange Diameter", motor.gearbox_output_flange],
        ["Output Shaft", motor.gearbox_output_shaft],
    ])

    if motor.gearbox_oil_capacity:
        gearbox_data.append(["Oil Capacity", f"{motor.gearbox_oil_capacity} L"])
    if motor.gearbox_oil_type:
        gearbox_data.append(["Lubricant Type", motor.gearbox_oil_type])

    gearbox_table = Table(gearbox_data, colWidths=[4.5*cm, 10*cm])
    gearbox_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(gearbox_table)
    story.append(Spacer(1, 0.3*cm))

    # ─── PERFORMANCE SUMMARY ───
    story.append(Paragraph("PERFORMANCE SUMMARY", ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, textColor=colors.white, backColor=colors.HexColor('#0d6efd'), spaceAfter=6, spaceBefore=0, fontName='Helvetica-Bold', leftIndent=6, rightIndent=6, topPadding=6, bottomPadding=6)))

    perf_data = [
        ["Speed Input → Output", f"{motor.motor_speed} rpm → {motor.gearbox_output_speed} rpm (Ratio 1:{motor.gearbox_ratio:.2f})"],
        ["Torque Input → Output", f"{motor.motor_torque} Nm → {motor.gearbox_output_torque} Nm (Ratio 1:{motor.gearbox_ratio:.2f})"],
    ]

    perf_table = Table(perf_data, colWidths=[4.5*cm, 10*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 0.4*cm))

    # Footer
    footer_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    story.append(Paragraph(footer_text, footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
