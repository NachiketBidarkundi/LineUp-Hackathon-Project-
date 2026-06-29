"""PDF scouting report generator using ReportLab."""
import io
from datetime import datetime, timezone
from typing import Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)

NAVY = colors.HexColor("#0A2540")
ACCENT = colors.HexColor("#007AFF")
GOLD = colors.HexColor("#D4A437")
GRAY = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#EFEFEF")
RED = colors.HexColor("#D7263D")
GREEN = colors.HexColor("#2BA84A")


def _radar_png(player: Dict[str, Any]) -> io.BytesIO:
    """Render a radar chart of percentile vs MLB to a PNG bytes buffer."""
    p = player.get("percentiles_vs_mlb", {})
    categories = ["Power", "Contact", "Speed", "Exit Velo", "Bat Speed", "Discipline"]
    values = [
        p.get("power", 50),
        p.get("contact_pct", 50),
        p.get("sprint_speed", 50),
        p.get("exit_velo_max", 50),
        p.get("bat_speed", 50),
        p.get("discipline", 50),
    ]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.6, 4.6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color="#007AFF", linewidth=2)
    ax.fill(angles, values, color="#007AFF", alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color="#888")
    ax.set_ylim(0, 100)
    ax.set_facecolor("#FAFAFA")
    ax.spines["polar"].set_color("#CCCCCC")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_report(player: Dict[str, Any], product_name: str = "LINEUP") -> bytes:
    """Returns the PDF as raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        topMargin=0.4 * inch, bottomMargin=0.4 * inch,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    h_brand = ParagraphStyle("brand", parent=styles["Normal"],
                             fontName="Helvetica-Bold", fontSize=18, textColor=colors.white, leading=22)
    h_name = ParagraphStyle("name", parent=styles["Normal"],
                            fontName="Helvetica-Bold", fontSize=16, textColor=colors.white,
                            alignment=TA_RIGHT, leading=20)
    label = ParagraphStyle("label", parent=styles["Normal"],
                           fontName="Helvetica", fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    big_num = ParagraphStyle("big", parent=styles["Normal"],
                             fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, alignment=TA_CENTER)
    section = ParagraphStyle("section", parent=styles["Normal"],
                             fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12)
    diag_body = ParagraphStyle("dbody", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=11)
    foot = ParagraphStyle("foot", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY)

    story = []

    # --- Header banner ---
    header_data = [[
        Paragraph(f"{product_name}<br/><font size=8 color='#A8C5E0'>SCOUTING REPORT</font>", h_brand),
        Paragraph(
            f"{player['name']}<br/><font size=9 color='#CCCCCC'>{player['position']} · "
            f"{player.get('school','')} · {datetime.now(timezone.utc).strftime('%b %d, %Y')}</font>",
            h_name,
        ),
    ]]
    header = Table(header_data, colWidths=[3.5 * inch, 4.0 * inch])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header)
    story.append(Spacer(1, 0.18 * inch))

    # --- Bio strip ---
    bio = (
        f"<b>Age</b> {player['age']}   "
        f"<b>HT</b> {player['height_in']//12}'{player['height_in']%12}\"   "
        f"<b>WT</b> {player['weight_lb']} lb   "
        f"<b>B/T</b> {player['bats']}/{player['throws']}   "
        f"<b>Region</b> {player['region']}"
    )
    story.append(Paragraph(bio, body))
    story.append(Spacer(1, 0.12 * inch))

    # --- Stats card (3 columns) ---
    s = player["stats"]
    p = player["percentiles_vs_mlb"]
    stat_card = [
        [Paragraph(f"{s['avg']:.3f}", big_num), Paragraph(f"{s['exit_velo_max']:.1f}", big_num), Paragraph(f"{s['sprint_speed']:.1f}", big_num)],
        [Paragraph("AVG / OBP / SLG", label), Paragraph("MAX EXIT VELO (mph)", label), Paragraph("SPRINT SPEED (ft/s)", label)],
        [Paragraph(f"{s['obp']:.3f} / {s['slg']:.3f}", body), Paragraph(f"{p['exit_velo_max']}th pct", body), Paragraph(f"{p['sprint_speed']}th pct", body)],
    ]
    stat_table = Table(stat_card, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch], rowHeights=[0.45 * inch, 0.22 * inch, 0.25 * inch])
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("LINEAFTER", (0, 0), (1, -1), 0.5, colors.HexColor("#D0D0D0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.18 * inch))

    # --- Radar chart + biomech / comp side-by-side ---
    radar_buf = _radar_png(player)
    radar_img = Image(radar_buf, width=3.4 * inch, height=3.4 * inch)

    biomech_block = [
        [Paragraph("<b>BIOMECH SCORE</b>", section)],
        [Paragraph(f"<font size=28 color='#0A2540'><b>{player['biomech_score']}</b></font><font size=10 color='#888'> / 100</font>", body)],
        [Spacer(1, 0.05 * inch)],
        [Paragraph("<b>MLB COMP</b>", section)],
        [Paragraph(f"<font size=14 color='#D4A437'><b>{player['mlb_comp']}</b></font>", body)],
        [Paragraph(f"Similarity: <b>{int(player['mlb_comp_similarity']*100)}%</b>", body)],
        [Spacer(1, 0.05 * inch)],
        [Paragraph("<b>FIT SCORE</b>", section)],
        [Paragraph(f"<font size=18 color='#007AFF'><b>{player['fit_score']}</b></font><font size=9 color='#888'> / 100</font>", body)],
    ]
    bio_table = Table(biomech_block, colWidths=[3.4 * inch])
    bio_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    combo = Table([[radar_img, bio_table]], colWidths=[3.6 * inch, 3.6 * inch])
    combo.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(combo)
    story.append(Spacer(1, 0.1 * inch))

    # --- Diagnostic section (if any biomech result attached) ---
    biomech = player.get("biomech_result")
    if biomech and biomech.get("diagnoses"):
        story.append(Paragraph("BIOMECH DIAGNOSES", section))
        for d in biomech["diagnoses"][:3]:
            color = RED if d["severity"] == "critical" else GOLD
            line = (
                f"<font color='{color.hexval()}'><b>[{d['severity'].upper()}]</b></font> "
                f"{d['message']} <i>(cost: {d['estimated_cost']})</i><br/>"
                f"<font color='#2BA84A'><b>FIX:</b></font> {d['fix']}"
            )
            story.append(Paragraph(line, diag_body))
            story.append(Spacer(1, 0.04 * inch))
    else:
        # Generic ceiling line
        story.append(Paragraph("PROJECTION", section))
        ceiling_evo = int(player["stats"]["exit_velo_max"] + 4)
        story.append(Paragraph(
            f"Projected ceiling: <b>{ceiling_evo} mph max exit velocity</b> with elite-level biomech refinement. "
            f"Current swing profiles to a <b>{player['mlb_comp']}</b>-style hitter at the next level.",
            diag_body,
        ))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        f"Generated by {product_name} · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"Confidential — for scouting use only.",
        foot,
    ))

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
