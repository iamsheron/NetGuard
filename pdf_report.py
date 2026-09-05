from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from core import shared_state
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import mm
from datetime import datetime


def generate_security_report(
    filename,
    devices,
    alerts,
    online_devices,
    offline_devices,
    rogue_devices,
    last_scan,
    scan_duration,
):

    document = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=15,
        spaceBefore=14,
        spaceAfter=8,
    )

    story = []

    # ==========================================
    # HEADER
    # ==========================================

    story.append(
        Paragraph(
            "NETGUARD SECURITY REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            subtitle_style
        )
    )

    # ==========================================
    # NETWORK SUMMARY
    # ==========================================

    story.append(
        Paragraph(
            "Network Summary",
            heading_style
        )
    )

    summary_data = [
        ["Metric", "Value"],
        ["Online Devices", str(online_devices)],
        ["Offline Devices", str(offline_devices)],
        ["Rogue Devices", str(rogue_devices)],
        ["Last Scan", str(last_scan)],
        ["Scan Duration", str(scan_duration)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[70 * mm, 90 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(summary_table)

    # ==========================================
    # DEVICES
    # ==========================================

    story.append(
        Paragraph(
            "Network Devices",
            heading_style
        )
    )

    device_data = [
        [
            "Device",
            "IP",
            "MAC",
            "Type",
            "Status",
        ]
    ]

    for device in devices:

        device_data.append([
            str(device.get("device_name", "Unknown")),
            str(device.get("ip", "Unknown")),
            str(device.get("mac", "Unknown")),
            str(device.get("device_type", "Unknown")),
            str(device.get("security_status", "Unknown")),
        ])

    if len(device_data) == 1:
        device_data.append(
            ["No devices found", "-", "-", "-", "-"]
        )

    device_table = Table(
        device_data,
        repeatRows=1,
        colWidths=[
            35 * mm,
            30 * mm,
            42 * mm,
            25 * mm,
            30 * mm,
        ],
    )

    device_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(device_table)

    # ==========================================
    # SECURITY EVENTS
    # ==========================================

    story.append(
        Paragraph(
            "Security Events",
            heading_style
        )
    )

    alert_data = [
        [
            "Severity",
            "Event",
            "Message",
            "Time",
        ]
    ]

    for alert in alerts:

        alert_data.append([
            str(alert.get("level", "UNKNOWN")),
            str(alert.get("title", "Security Event")),
            str(alert.get("message", "")),
            str(alert.get("time", "")),
        ])

    if len(alert_data) == 1:
        alert_data.append([
            "INFO",
            "No Security Events",
            "No security events have been recorded.",
            "-",
        ])

    alert_table = Table(
        alert_data,
        repeatRows=1,
        colWidths=[
            25 * mm,
            40 * mm,
            75 * mm,
            35 * mm,
        ],
    )

    alert_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(alert_table)

    # ==========================================
    # SECURITY STATUS
    # ==========================================

    story.append(
        Paragraph(
            "Security Status",
            heading_style
        )
    )

    if rogue_devices > 0:
        status_text = (
            "⚠ SECURITY WARNING: "
            f"{rogue_devices} rogue device(s) detected."
        )
    elif any(
        alert.get("level") == "CRITICAL"
        for alert in alerts
    ):
        status_text = (
            "🚨 CRITICAL SECURITY EVENTS DETECTED."
        )
    else:
        status_text = (
            "✓ No critical security threats detected "
            "during the recorded scan period."
        )

    story.append(
        Paragraph(
            status_text,
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated by NetGuard",
            subtitle_style
        )
    )

    document.build(story)

def generate_current_security_report(filename):
    """
    Generate a PDF using the current NetGuard shared state.
    """

    devices = shared_state.devices
    alerts = shared_state.alerts

    online_devices = shared_state.online_devices
    offline_devices = shared_state.offline_devices

    rogue_devices = sum(
        1
        for device in devices
        if not device.get("is_trusted", True)
    )

    last_scan = shared_state.last_scan
    scan_duration = shared_state.scan_duration

    generate_security_report(
        filename=filename,
        devices=devices,
        alerts=alerts,
        online_devices=online_devices,
        offline_devices=offline_devices,
        rogue_devices=rogue_devices,
        last_scan=last_scan,
        scan_duration=scan_duration,
    )