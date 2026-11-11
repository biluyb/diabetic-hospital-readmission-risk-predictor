"""
GlucoShield CDSS — Capstone Presentation & Document Generator
Generates:
1. presentation/GlucoShield_Capstone_Presentation.pptx (9 slides, widescreen, professional styling, speaker notes)
2. presentation/GlucoShield_Presentation_Script.docx (complete verbatim speaking script with cues)
3. presentation/preview/*.png (slide preview images + overview grid)
4. presentation/README.md (presentation guide, checklist, instructions)
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

from docx import Document
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# Output paths
DIR_PRESENTATION = "presentation"
DIR_PREVIEWS = os.path.join(DIR_PRESENTATION, "preview")
PATH_PPTX = os.path.join(DIR_PRESENTATION, "GlucoShield_Capstone_Presentation.pptx")
PATH_DOCX = os.path.join(DIR_PRESENTATION, "GlucoShield_Presentation_Script.docx")
PATH_README = os.path.join(DIR_PRESENTATION, "README.md")

os.makedirs(DIR_PREVIEWS, exist_ok=True)

# ── Color Palette ─────────────────────────────────────────────────────────────
COLOR_BG = RGBColor(11, 18, 32)          # #0B1220 Deep Navy
COLOR_SURFACE = RGBColor(17, 24, 39)     # #111827 Dark Slate
COLOR_CARD = RGBColor(30, 41, 59)        # #1E293B Elevated Card
COLOR_CARD_BORDER = RGBColor(51, 65, 85) # #334155 Slate Border

COLOR_TEXT_MAIN = RGBColor(248, 250, 252)  # #F8FAFC
COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8

COLOR_PRIMARY_BLUE = RGBColor(37, 99, 235)  # #2563EB
COLOR_ACCENT_BLUE = RGBColor(96, 165, 250)  # #60A5FA
COLOR_TEAL = RGBColor(20, 184, 166)         # #14B8A6

COLOR_RISK_LOW = RGBColor(22, 163, 74)      # #16A34A Green
COLOR_RISK_BORDER = RGBColor(217, 119, 6)   # #D97706 Amber
COLOR_RISK_HIGH = RGBColor(220, 38, 38)     # #DC2626 Red

# ── Slide Construction Helpers ────────────────────────────────────────────────
def set_slide_background(slide, color=COLOR_BG):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, slide_num, title_text, category_text, time_text):
    # Top accent line
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.35), Inches(11.733), Inches(0.04))
    accent.fill.solid()
    accent.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    accent.line.fill.background()

    # Category and slide info
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(8.0), Inches(0.3))
    tf_cat = cat_box.text_frame
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = f"GLUCOSHIELD CDSS  |  {category_text.upper()}  |  SLIDE {slide_num} OF 9"
    p_cat.font.name = "Segoe UI"
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_TEAL

    # Timing badge
    time_box = slide.shapes.add_textbox(Inches(9.0), Inches(0.42), Inches(3.533), Inches(0.3))
    tf_time = time_box.text_frame
    p_time = tf_time.paragraphs[0]
    p_time.alignment = PP_ALIGN.RIGHT
    p_time.text = f"TIMING: {time_text}"
    p_time.font.name = "Segoe UI"
    p_time.font.size = Pt(9.5)
    p_time.font.bold = True
    p_time.font.color.rgb = COLOR_TEXT_MUTED

    # Main slide title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
    tf_title = title_box.text_frame
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Segoe UI"
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card

def add_kpi_card(slide, left, top, width, height, label, value, subtext, accent_color=COLOR_PRIMARY_BLUE):
    card = add_card(slide, left, top, width, height, COLOR_CARD, COLOR_CARD_BORDER)
    strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.06))
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(left + Inches(0.12), top + Inches(0.1), width - Inches(0.24), height - Inches(0.15))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = label.upper()
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(9)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_TEXT_MUTED

    p1 = tf.add_paragraph()
    p1.text = value
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN

    p2 = tf.add_paragraph()
    p2.text = subtext
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = COLOR_TEXT_MUTED

def attach_speaker_notes(slide, timing, say_script, understand_text, action_cue):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = (
        f"=== EXACT PRESENTATION TIMING: {timing} ===\n\n"
        f"[WHAT TO SAY - VERBATIM SCRIPT]:\n\"{say_script}\"\n\n"
        f"[KEY AUDIENCE TAKEAWAY]:\n{understand_text}\n\n"
        f"[PRESENTER ACTION / SLIDE CUE]:\n{action_cue}\n"
    )

# ─────────────────────────────────────────────────────────────────────────────
# BUILD THE 9 SLIDES IN PPTX
# ─────────────────────────────────────────────────────────────────────────────
def build_powerpoint():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 1: Title and Project Introduction (0:00–0:30)
    # ═════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_BG)

    # Accent decorative glow/bar
    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(0.12), Inches(3.2))
    dec.fill.solid()
    dec.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    dec.line.fill.background()

    # Brand badge
    b_card = add_card(s1, Inches(1.1), Inches(1.0), Inches(4.5), Inches(0.38), COLOR_SURFACE, COLOR_CARD_BORDER)
    b_tb = s1.shapes.add_textbox(Inches(1.15), Inches(1.02), Inches(4.4), Inches(0.35))
    b_tf = b_tb.text_frame
    bp = b_tf.paragraphs[0]
    bp.text = "FUSE AI-201 CAPSTONE  |  GROUP 04  |  YEEAP COHORT"
    bp.font.name = "Segoe UI"
    bp.font.size = Pt(9.5)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_TEAL

    # Main Title
    t_tb = s1.shapes.add_textbox(Inches(1.1), Inches(1.45), Inches(11.0), Inches(1.2))
    t_tf = t_tb.text_frame
    tp = t_tf.paragraphs[0]
    tp.text = "GlucoShield"
    tp.font.name = "Segoe UI"
    tp.font.size = Pt(46)
    tp.font.bold = True
    tp.font.color.rgb = COLOR_TEXT_MAIN

    tp2 = t_tf.add_paragraph()
    tp2.text = "AI-Powered Diabetes Hospital Readmission Risk Prediction"
    tp2.font.name = "Segoe UI"
    tp2.font.size = Pt(22)
    tp2.font.bold = True
    tp2.font.color.rgb = COLOR_ACCENT_BLUE

    # Subtitle
    sub_tb = s1.shapes.add_textbox(Inches(1.1), Inches(2.8), Inches(11.0), Inches(0.7))
    sub_tf = sub_tb.text_frame
    sub_tf.word_wrap = True
    sub_p = sub_tf.paragraphs[0]
    sub_p.text = "An Explainable Machine Learning Approach to 30-Day Hospital Readmission Risk Stratification."
    sub_p.font.name = "Segoe UI"
    sub_p.font.size = Pt(13)
    sub_p.font.color.rgb = COLOR_TEXT_MUTED

    # Presenter Information Card
    p_card = add_card(s1, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.4), COLOR_SURFACE, COLOR_PRIMARY_BLUE)
    p_tb = s1.shapes.add_textbox(Inches(1.0), Inches(4.55), Inches(5.2), Inches(2.1))
    p_tf = p_tb.text_frame
    p_tf.word_wrap = True
    
    pp0 = p_tf.paragraphs[0]
    pp0.text = "PRESENTER & CAPSTONE LEAD"
    pp0.font.name = "Segoe UI"
    pp0.font.size = Pt(9.5)
    pp0.font.bold = True
    pp0.font.color.rgb = COLOR_TEAL

    pp1 = p_tf.add_paragraph()
    pp1.text = "Bililign Yibgeta Amare"
    pp1.font.name = "Segoe UI"
    pp1.font.size = Pt(18)
    pp1.font.bold = True
    pp1.font.color.rgb = COLOR_TEXT_MAIN

    pp2 = p_tf.add_paragraph()
    pp2.text = "Team Lead · ML Modeling, Pipeline Architecture & Testing\nFUSE AI-201: AI Model Development & MLOps\nYouth Empowerment and Employment in AI Program (YEEAP)"
    pp2.font.name = "Segoe UI"
    pp2.font.size = Pt(10.5)
    pp2.font.color.rgb = COLOR_TEXT_MUTED

    # Quick Architecture Highlights Card
    h_card = add_card(s1, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.4), COLOR_SURFACE, COLOR_CARD_BORDER)
    h_tb = s1.shapes.add_textbox(Inches(7.0), Inches(4.55), Inches(5.3), Inches(2.1))
    h_tf = h_tb.text_frame
    h_tf.word_wrap = True
    
    hp0 = h_tf.paragraphs[0]
    hp0.text = "SYSTEM AT A GLANCE"
    hp0.font.name = "Segoe UI"
    hp0.font.size = Pt(9.5)
    hp0.font.bold = True
    hp0.font.color.rgb = COLOR_ACCENT_BLUE

    highlights = [
        "Clinical Dataset: 101,766 US Hospital Inpatient Records (1999–2008)",
        "Primary Engine: Calibrated XGBoost with L1/L2 Regularization",
        "Clinical Decision Cutoff: 0.45 (Prioritizes Sensitivity >= 65%)",
        "Interpretability: Real-Time TreeSHAP Local Factor Attribution",
        "Verification: 17/17 pytest Automated Tests & 5 Stage 8 Robustness Checks"
    ]
    for h in highlights:
        hp = h_tf.add_paragraph()
        hp.text = f"• {h}"
        hp.font.name = "Segoe UI"
        hp.font.size = Pt(10)
        hp.font.color.rgb = COLOR_TEXT_MAIN

    attach_speaker_notes(
        s1,
        timing="0:00 – 0:30 (30 seconds)",
        say_script=(
            "Good morning, esteemed evaluators, mentors, and colleagues. My name is Bililign Yibgeta Amare, "
            "and on behalf of Group 04 in the Youth Empowerment and Employment in AI Program, I am honored "
            "to present our FUSE AI-201 Capstone project: GlucoShield — an AI-powered Clinical Decision Support "
            "System for predicting 30-day hospital readmission risk among diabetic inpatients. "
            "Over the next nine minutes, I will walk you through our clinical problem, rigorous data preprocessing, "
            "model selection, threshold calibration, a live demonstration of our working Streamlit prototype, "
            "TreeSHAP explainability, and our MLOps drift monitoring pipeline. Let us begin with the problem."
        ),
        understand_text=(
            "GlucoShield is an explainable machine learning clinical decision support prototype developed for "
            "FUSE AI-201 by Group 04, led by Bililign Yibgeta Amare, predicting 30-day diabetic readmissions."
        ),
        action_cue="Start presentation in full-screen slide show mode; maintain steady, confident pace."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 2: Problem and Motivation (0:30–1:15)
    # ═════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, COLOR_BG)
    add_header(s2, 2, "Clinical Problem & Industry Motivation", "Problem Statement", "0:30 – 1:15 (45s)")

    # 3 Column Cards
    col_w = Inches(3.7)
    gap = Inches(0.3)
    top_pos = Inches(1.5)
    h_pos = Inches(3.6)

    # Card 1: Clinical Burden
    c1 = add_card(s2, Inches(0.8), top_pos, col_w, h_pos)
    tb1 = s2.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), col_w - Inches(0.3), h_pos - Inches(0.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "THE CLINICAL BURDEN"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    points1 = [
        "Diabetes affects over 537M adults worldwide, causing frequent multi-organ hospitalizations.",
        "Diabetic inpatients face 2x to 3x higher 30-day readmission rates than non-diabetic cohorts.",
        "Complex interactions between glycemic volatility, insulin titrations, and comorbidities (CHF, renal failure) make manual risk estimation unreliable."
    ]
    for pt in points1:
        p = tf1.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(4)

    # Card 2: Financial & Regulatory Penalty
    c2 = add_card(s2, Inches(0.8) + col_w + gap, top_pos, col_w, h_pos)
    tb2 = s2.shapes.add_textbox(Inches(0.95) + col_w + gap, top_pos + Inches(0.15), col_w - Inches(0.3), h_pos - Inches(0.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "REGULATORY & FINANCIAL RISK"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_BORDER

    points2 = [
        "Under the CMS Hospital Readmissions Reduction Program (HRRP), hospitals face penalties up to 3% of total Medicare reimbursements.",
        "Unplanned readmissions cost the US healthcare system over $17 Billion annually in preventable expenditures.",
        "Hospitals urgently need pre-discharge screening to allocate scarce transitional care resources effectively."
    ]
    for pt in points2:
        p = tf2.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(4)

    # Card 3: Limitations of Traditional Tools
    c3 = add_card(s2, Inches(0.8) + (col_w + gap)*2, top_pos, col_w, h_pos)
    tb3 = s2.shapes.add_textbox(Inches(0.95) + (col_w + gap)*2, top_pos + Inches(0.15), col_w - Inches(0.3), h_pos - Inches(0.3))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "LIMITATIONS OF CURRENT HEURISTICS"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    points3 = [
        "Traditional tools like the LACE index rely on static linear scoring (length of stay, acute admission, comorbidity, ED visits).",
        "They ignore critical glycemic markers (HbA1c tests, insulin dosage shifts, multi-drug therapies).",
        "Scores are computed at the moment of discharge—too late to coordinate specialized post-discharge care."
    ]
    for pt in points3:
        p = tf3.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(4)

    # Bottom Problem-to-Solution Flow Diagram
    flow_box = add_card(s2, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.7), COLOR_SURFACE, COLOR_PRIMARY_BLUE)
    ftb = s2.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.333), Inches(1.5))
    ftf = ftb.text_frame
    ftf.word_wrap = True

    fp0 = ftf.paragraphs[0]
    fp0.text = "GLUCOSHIELD SOLUTION: RISK-INFORMED DISCHARGE WORKFLOW"
    fp0.font.name = "Segoe UI"
    fp0.font.size = Pt(10)
    fp0.font.bold = True
    fp0.font.color.rgb = COLOR_TEAL

    fp1 = ftf.add_paragraph()
    fp1.text = (
        "Patient Inpatient History  ───▶  Machine Learning Risk Assessment (XGBoost)  ───▶  "
        "Explainable Risk Score (TreeSHAP)  ───▶  Informed Discharge Interventions\n"
        "(Demographics, labs, prior visits, meds)       (Non-linear interactions, calibrated cutoff)      "
        "(Quantified clinical drivers at bedside)       (Nurse visits, expedited clinic follow-up)"
    )
    fp1.font.name = "Segoe UI"
    fp1.font.size = Pt(11)
    fp1.font.color.rgb = COLOR_TEXT_MAIN
    fp1.space_after = Pt(4)

    fp2 = ftf.add_paragraph()
    fp2.text = "Notice: GlucoShield operates strictly as Clinical Decision Support (CDSS) to supplement, not replace, licensed clinical judgment."
    fp2.font.name = "Segoe UI"
    fp2.font.size = Pt(8.5)
    fp2.font.color.rgb = COLOR_TEXT_MUTED

    attach_speaker_notes(
        s2,
        timing="0:30 – 1:15 (45 seconds)",
        say_script=(
            "Diabetes mellitus affects over five hundred million patients globally. When hospitalized, diabetic "
            "patients experience acute multi-organ vulnerability—balancing unstable glucose, rapid medication adjustments, "
            "and chronic heart or kidney failure. In the United States, under the CMS Hospital Readmissions Reduction Program, "
            "hospitals face penalties of up to 3% of their total Medicare reimbursements for excessive 30-day readmissions, "
            "costing healthcare systems over seventeen billion dollars every year. "
            "Currently, discharge planners rely either on clinical intuition or static heuristics like the LACE index. "
            "These scoring tools suffer from three fatal flaws: they are linear, they completely ignore medication changes "
            "and glycemia, and they are calculated at the exit door—far too late to coordinate home care. "
            "GlucoShield bridges this gap: analyzing inpatient history with machine learning to produce an explainable risk score "
            "that mobilizes targeted discharge protocols before the patient leaves the hospital."
        ),
        understand_text=(
            "Diabetic readmissions impose huge financial and clinical costs. Static tools like LACE fail to capture "
            "glycemic dynamics. GlucoShield provides proactive, explainable risk assessment to guide discharge care."
        ),
        action_cue="Advance from Slide 1 to Slide 2; emphasize the Problem-to-Solution flow at the bottom."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 3: Dataset and Data Preparation (1:15–2:15)
    # ═════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, COLOR_BG)
    add_header(s3, 3, "Dataset Hygiene & Causal Engineering Pipeline", "Data Preparation", "1:15 – 2:15 (60s)")

    # 4 Pipeline Stage Cards
    col_w4 = Inches(2.75)
    gap4 = Inches(0.24)
    t4 = Inches(1.45)
    h4 = Inches(3.8)

    # Stage 1: Raw Ingestion
    add_card(s3, Inches(0.8), t4, col_w4, h4)
    tb = s3.shapes.add_textbox(Inches(0.92), t4 + Inches(0.12), col_w4 - Inches(0.24), h4 - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. RAW INGESTION"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    p1 = tf.add_paragraph()
    p1.text = "101,766 Encounters"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    items1 = [
        "UCI Diabetes 130-US Hospitals dataset (1999–2008).",
        "50 initial features: demographics, admission source, lab counts, 23 diabetes medications.",
        "Clinical inpatient cohort admitted with diagnosed diabetes."
    ]
    for it in items1:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Stage 2: Causal Leakage Audit
    add_card(s3, Inches(0.8) + col_w4 + gap4, t4, col_w4, h4)
    tb = s3.shapes.add_textbox(Inches(0.92) + col_w4 + gap4, t4 + Inches(0.12), col_w4 - Inches(0.24), h4 - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. CAUSAL AUDIT"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_BORDER

    p1 = tf.add_paragraph()
    p1.text = "69,990 Clean Cohort"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    items2 = [
        "Removed 2,423 expired/hospice records: readmission is causally impossible; inclusion leaks outcome.",
        "Deduplicated to unique patient first index encounters (69,990 rows) to eliminate patient-level cross-split leak.",
        "Preserved causal validity of discharge risk."
    ]
    for it in items2:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Stage 3: Clinical Grouping & Features
    add_card(s3, Inches(0.8) + (col_w4 + gap4)*2, t4, col_w4, h4)
    tb = s3.shapes.add_textbox(Inches(0.92) + (col_w4 + gap4)*2, t4 + Inches(0.12), col_w4 - Inches(0.24), h4 - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. FEATURE ENGINEERING"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    p1 = tf.add_paragraph()
    p1.text = "9 Organ Systems"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    items3 = [
        "Mapped 800+ raw ICD-9 codes to 9 clinically validated categories (Circulatory, Respiratory, Diabetes, etc.).",
        "Engineered 13 clinical ratios: procedure intensity, medication count per day, prior utilization.",
        "Medication titration tracking: captured insulin dosage changes ('Up', 'Down', 'Steady')."
    ]
    for it in items3:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Stage 4: Holdout Split & Imbalance
    add_card(s3, Inches(0.8) + (col_w4 + gap4)*3, t4, col_w4, h4)
    tb = s3.shapes.add_textbox(Inches(0.92) + (col_w4 + gap4)*3, t4 + Inches(0.12), col_w4 - Inches(0.24), h4 - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "4. HOLDOUT EVALUATION"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p1 = tf.add_paragraph()
    p1.text = "13,998 Test Holdout"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    items4 = [
        "Severe class imbalance: only 8.98% readmitted <30 days (6,293 total positive cases).",
        "Strict 80/20 train/test split: 55,992 train vs 13,998 holdout test records.",
        "Preprocessing transformer fitted strictly on training split to guarantee zero test leakage."
    ]
    for it in items4:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Bottom Pipeline Summary Strip
    bot_card = add_card(s3, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.5), COLOR_SURFACE, COLOR_CARD_BORDER)
    btb = s3.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.3))
    btf = btb.text_frame
    btf.word_wrap = True

    bp0 = btf.paragraphs[0]
    bp0.text = "METHODOLOGICAL SAFEGUARD SUMMARY"
    bp0.font.name = "Segoe UI"
    bp0.font.size = Pt(10)
    bp0.font.bold = True
    bp0.font.color.rgb = COLOR_TEAL

    bp1 = btf.add_paragraph()
    bp1.text = (
        "• Causal Leakage Prevented: Deceased/hospice patients removed (readmission impossible).\n"
        "• Data Leakage Prevented: Only first patient encounters used; preprocessor fitted solely on training split.\n"
        "• Dimensionality Controlled: 800+ ICD-9 codes condensed into 9 clinically sound diagnostic groups."
    )
    bp1.font.name = "Segoe UI"
    bp1.font.size = Pt(10)
    bp1.font.color.rgb = COLOR_TEXT_MAIN

    attach_speaker_notes(
        s3,
        timing="1:15 – 2:15 (60 seconds)",
        say_script=(
            "To build an honest healthcare model, data hygiene must be uncompromising. "
            "We utilized the gold-standard UCI 130-US Hospitals dataset, comprising 101,766 inpatient encounters. "
            "First, we conducted a causal cohort audit: 2,423 patients expired in the hospital or were discharged to hospice. "
            "Keeping deceased patients in readmission modeling introduces severe causal leakage—readmission is logically impossible. "
            "We removed them. Next, to prevent patient-level test leakage, we deduplicated repeat encounters, retaining solely each "
            "patient's first indexed admission, yielding a clean cohort of 69,990 encounters. "
            "Third, raw ICD-9 codes spanned over eight hundred discrete numbers. One-hot encoding all eight hundred would create an explosion "
            "of sparse noise. We collapsed them into nine clinically sound organ-system categories—such as Circulatory, Respiratory, "
            "and Diabetes with complications—and engineered composite clinical ratios like medication intensity and prior hospital utilization. "
            "Finally, our clean cohort exhibited acute class imbalance: only 8.98% readmitted within 30 days. "
            "We split the data strictly 80/20, locking away 13,998 patients for untouched holdout evaluation."
        ),
        understand_text=(
            "The data pipeline applied causal filtering (removing expired patients), patient deduplication, "
            "ICD-9 grouping to 9 categories, and strict 80/20 train/test separation to guarantee zero leakage."
        ),
        action_cue="Point to each of the 4 pipeline stages from left to right."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 4: Model Development and Selection (2:15–3:15)
    # ═════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, COLOR_BG)
    add_header(s4, 4, "Model Benchmarking & Architectural Selection", "Model Selection", "2:15 – 3:15 (60s)")

    # Left: Model Comparison Table Container
    left_w = Inches(6.8)
    top_pos4 = Inches(1.4)
    h_pos4 = Inches(5.6)
    c_tbl = add_card(s4, Inches(0.8), top_pos4, left_w, h_pos4)

    tb_tbl = s4.shapes.add_textbox(Inches(1.0), top_pos4 + Inches(0.15), left_w - Inches(0.4), Inches(0.4))
    tf_tbl = tb_tbl.text_frame
    p = tf_tbl.paragraphs[0]
    p.text = "BENCHMARK ON 20% TEST SET (n=13,998)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    # Insert PowerPoint Table
    rows = 6
    cols = 4
    table_shape = s4.shapes.add_table(rows, cols, Inches(1.0), top_pos4 + Inches(0.6), left_w - Inches(0.4), Inches(2.6))
    table = table_shape.table
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(1.3)
    table.columns[2].width = Inches(1.3)
    table.columns[3].width = Inches(1.4)

    headers = ["Model Family", "Holdout AUC", "Recall @ 0.45", "Evaluation Note"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_BORDER
        for para in cell.text_frame.paragraphs:
            para.font.name = "Segoe UI"
            para.font.size = Pt(9.5)
            para.font.bold = True
            para.font.color.rgb = COLOR_TEXT_MAIN

    table_data = [
        ("Majority Class Baseline", "0.500", "0.0%", "Zero readmissions caught"),
        ("Logistic Regression (L2)", "0.647", "53.1%", "Linear lower bound"),
        ("Random Forest (100 Trees)", "0.646", "43.9%", "Train AUC 0.805 (Overfit)"),
        ("LightGBM", "0.647", "53.7%", "Balanced gradient booster"),
        ("XGBoost (Selected Primary)", "0.647", "65.71%", "Optimal sensitivity & L2 reg")
    ]
    for row_idx, row in enumerate(table_data, start=1):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            if row_idx == 5:
                cell.fill.fore_color.rgb = RGBColor(20, 45, 80) # highlighted row
            else:
                cell.fill.fore_color.rgb = COLOR_SURFACE
            for para in cell.text_frame.paragraphs:
                para.font.name = "Segoe UI"
                para.font.size = Pt(9)
                if row_idx == 5:
                    para.font.bold = True
                    para.font.color.rgb = COLOR_ACCENT_BLUE
                else:
                    para.font.color.rgb = COLOR_TEXT_MAIN

    # Explanatory card below table
    tb_why = s4.shapes.add_textbox(Inches(1.0), top_pos4 + Inches(3.3), left_w - Inches(0.4), Inches(2.1))
    tf_why = tb_why.text_frame
    tf_why.word_wrap = True
    p = tf_why.paragraphs[0]
    p.text = "WHY XGBOOST WAS CHOSEN AS THE OPERATIONAL ENGINE:"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    reasons = [
        "1. Superior Readmission Recall: 65.71% sensitivity at 0.45 cutoff—capturing 12% more true readmissions than Logistic Regression or LightGBM.",
        "2. Controlled Generalization: Strict L1 (reg_alpha=0.5) and L2 (reg_lambda=2.0) penalties prevented the severe tree memorization seen in Random Forest.",
        "3. High-Speed Interpretability: Native integration with TreeSHAP achieves sub-15ms patient attribution for real-time clinical deployment."
    ]
    for r in reasons:
        p = tf_why.add_paragraph()
        p.text = r
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(2)

    # Right: ROC Curve Visual
    right_left = Inches(8.0)
    right_w = Inches(4.533)
    c_roc = add_card(s4, right_left, top_pos4, right_w, h_pos4)
    tb_roc = s4.shapes.add_textbox(right_left + Inches(0.15), top_pos4 + Inches(0.15), right_w - Inches(0.3), Inches(0.4))
    tf_roc = tb_roc.text_frame
    p = tf_roc.paragraphs[0]
    p.text = "HOLDOUT ROC CURVES (n=13,998)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    if os.path.exists("plots/roc_curve.png"):
        s4.shapes.add_picture("plots/roc_curve.png", right_left + Inches(0.2), top_pos4 + Inches(0.6), right_w - Inches(0.4), Inches(4.7))

    attach_speaker_notes(
        s4,
        timing="2:15 – 3:15 (60 seconds)",
        say_script=(
            "With an 8.98% positive prevalence, a naive model predicts zero for everyone, claiming 91% accuracy "
            "while catching zero readmissions. We instituted a reproducible experiment tracking pipeline, evaluating "
            "five model architectures on our untouched holdout test set of 13,998 patients. "
            "Our trivial baseline scored 0.50 ROC-AUC. Logistic Regression established a solid linear baseline at 0.647 ROC-AUC. "
            "Random Forest achieved an apparent 0.805 on the training set but plummeted to 0.646 on holdout test data, demonstrating "
            "severe memorization of hospital administrative noise. LightGBM and XGBoost achieved identical 0.647 holdout discrimination. "
            "However, we selected XGBoost as our primary operational model for three definitive reasons: "
            "first, when calibrated at our 0.45 threshold, it yielded the highest clinical sensitivity at 65.71%—catching 12% more at-risk patients; "
            "second, strong L1 and L2 regularization eliminated overfitting; "
            "and third, its tree architecture connects natively with TreeSHAP for sub-fifteen-millisecond clinical explainability."
        ),
        understand_text=(
            "Five models were rigorously benchmarked. XGBoost won because of maximum sensitivity (65.71%), "
            "effective regularization against overfitting, and seamless TreeSHAP interpretability."
        ),
        action_cue="Highlight the XGBoost row in the table, then gesture to the ROC curves on the right."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 5: Model Evaluation and Threshold Calibration (3:15–4:15)
    # ═════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, COLOR_BG)
    add_header(s5, 5, "Holdout Evaluation & Clinical Threshold Calibration", "Model Evaluation", "3:15 – 4:15 (60s)")

    # 5 Metric Cards across top
    kw = Inches(2.2)
    kg = Inches(0.18)
    kt = Inches(1.35)
    kh = Inches(1.3)
    k_data = [
        ("ROC-AUC", "0.6465", "Holdout set (n=13,998)", COLOR_PRIMARY_BLUE),
        ("PR-AUC", "0.158", "Low prevalence (8.98%)", COLOR_TEAL),
        ("Recall @ 0.45", "65.71%", "826 readmissions caught", COLOR_RISK_LOW),
        ("Specificity", "54.54%", "6,949 non-readmissions", COLOR_ACCENT_BLUE),
        ("Precision", "12.48%", "Accepted clinical trade-off", COLOR_RISK_BORDER),
    ]
    for idx, (lbl, val, sub, col) in enumerate(k_data):
        add_kpi_card(s5, Inches(0.8) + (kw + kg)*idx, kt, kw, kh, lbl, val, sub, col)

    # Left: Confusion Matrix Display
    cm_left = Inches(0.8)
    cm_top = Inches(2.8)
    cm_w = Inches(5.8)
    cm_h = Inches(4.2)
    add_card(s5, cm_left, cm_top, cm_w, cm_h)

    cm_tb = s5.shapes.add_textbox(cm_left + Inches(0.15), cm_top + Inches(0.15), cm_w - Inches(0.3), Inches(0.4))
    cm_tf = cm_tb.text_frame
    p = cm_tf.paragraphs[0]
    p.text = "CONFUSION MATRIX AT 0.45 DECISION CUTOFF"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    if os.path.exists("plots/confusion_matrix.png"):
        s5.shapes.add_picture("plots/confusion_matrix.png", cm_left + Inches(0.2), cm_top + Inches(0.55), cm_w - Inches(0.4), Inches(3.45))

    # Right: Threshold Calibration Rationale
    r_left = Inches(6.8)
    r_w = Inches(5.733)
    r_h = Inches(4.2)
    add_card(s5, r_left, cm_top, r_w, r_h)

    r_tb = s5.shapes.add_textbox(r_left + Inches(0.2), cm_top + Inches(0.15), r_w - Inches(0.4), r_h - Inches(0.3))
    r_tf = r_tb.text_frame
    r_tf.word_wrap = True

    p = r_tf.paragraphs[0]
    p.text = "CLINICAL RATIONALE FOR 0.45 DECISION THRESHOLD"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    calib_points = [
        "1. Asymmetric Clinical Costs: Missing an at-risk diabetic patient (False Negative) can lead to severe relapse, diabetic ketoacidosis, or death. Conversely, scheduling an unnecessary nurse telephone check-in (False Positive) is safe and clinically benign.",
        "2. Significant Sensitivity Gain: Operating at default 0.50 cutoff catches only 51.9% of readmissions (48% missed!). Calibrating down to 0.45 increases recall to 65.71%—capturing 826 of 1,257 true readmissions.",
        "3. False Negative Error Audit: Analysis of the 431 missed cases revealed they averaged only 0.04 prior inpatient visits and shorter stays. They looked clinically stable upon discharge, implying their readmissions were driven by unrecorded outpatient factors (copay costs, social isolation)—confirming AI must augment, not replace, clinical case managers."
    ]
    for pt in calib_points:
        p = r_tf.add_paragraph()
        p.text = pt
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(4)

    attach_speaker_notes(
        s5,
        timing="3:15 – 4:15 (60 seconds)",
        say_script=(
            "In clinical screening, not all errors are equal. A False Negative—sending home a patient who needed "
            "nursing care—can result in severe decompensation, emergency readmission, or death. "
            "A False Positive—calling a patient at home who turns out to be doing fine—is safe, proactive preventive care. "
            "At the default threshold of 0.50, our XGBoost model achieved 51.9% recall, missing nearly half of all readmissions. "
            "By systematically evaluating threshold sweeps, we calibrated our operational decision boundary to 0.45. "
            "Operating at 0.45 boosted our clinical sensitivity to 65.71%, successfully catching 826 out of 1,257 true readmissions "
            "in our holdout test set. We accept a precision of 12.48% because the prevalence of 30-day readmission is naturally low at 8.98%. "
            "We also conducted an error audit on the 431 False Negatives: these patients had virtually zero prior admissions (averaging 0.04) "
            "and brief hospital stays. They appeared outwardly healthy upon discharge, pointing to post-discharge social determinants "
            "like medication unaffordability or lack of home caregivers. This is why AI must support, never replace, bedside clinicians."
        ),
        understand_text=(
            "The 0.45 threshold prioritizes sensitivity (65.71% recall, 826 readmissions caught) because missing a patient "
            "carries far higher clinical risk than a false positive follow-up call. Precision is 12.48% due to low base rate."
        ),
        action_cue="Walk through the 5 KPI cards at top, point to the 826 True Positives, and explain the False Negative audit."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 6: Live Application Demonstration (4:15–6:45)
    # ═════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, COLOR_BG)
    add_header(s6, 6, "Live Clinical Prototype Demonstration", "Prototype Demo", "4:15 – 6:45 (2m 30s)")

    # Callout banner: Switching to browser
    banner = add_card(s6, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.7), RGBColor(30, 58, 138), COLOR_ACCENT_BLUE)
    btb = s6.shapes.add_textbox(Inches(1.0), Inches(1.42), Inches(11.333), Inches(0.55))
    btf = btb.text_frame
    p = btf.paragraphs[0]
    p.text = "LIVE SYSTEM DEMONSTRATION: SWITCHING TO STREAMLIT APPLICATION (http://localhost:8501)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN

    # 3 Clinical Demonstration Scenario Cards
    col_w3 = Inches(3.7)
    gap3 = Inches(0.3)
    t3 = Inches(2.2)
    h3 = Inches(4.7)

    # Scenario 1: Low Risk
    add_card(s6, Inches(0.8), t3, col_w3, h3)
    # Status Pill
    sp1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), t3 + Inches(0.18), Inches(1.5), Inches(0.3))
    sp1.fill.solid()
    sp1.fill.fore_color.rgb = COLOR_RISK_LOW
    sp1.line.fill.background()
    p = sp1.text_frame.paragraphs[0]
    p.text = "LOW RISK"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER

    tb = s6.shapes.add_textbox(Inches(1.0), t3 + Inches(0.55), col_w3 - Inches(0.4), h3 - Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Scenario 1: Stable Patient"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN

    p = tf.add_paragraph()
    p.text = "Risk Probability: 27.1%\nPrediction: NEGATIVE (< 0.45)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_LOW
    p.space_after = Pt(6)

    s1_pts = [
        "Patient Profile: 45 y/o male, first hospital admission, 2 days length of stay.",
        "Clinical Glycemia: HbA1c normal, zero dosage titration, stable metformin regimen.",
        "Discharge Protocol: Routine diabetes nutrition education and standard 14–30 day primary care follow-up."
    ]
    for pt in s1_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(4)

    # Scenario 2: High Risk
    add_card(s6, Inches(0.8) + col_w3 + gap3, t3, col_w3, h3)
    sp2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0) + col_w3 + gap3, t3 + Inches(0.18), Inches(1.5), Inches(0.3))
    sp2.fill.solid()
    sp2.fill.fore_color.rgb = COLOR_RISK_HIGH
    sp2.line.fill.background()
    p = sp2.text_frame.paragraphs[0]
    p.text = "HIGH RISK"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER

    tb = s6.shapes.add_textbox(Inches(1.0) + col_w3 + gap3, t3 + Inches(0.55), col_w3 - Inches(0.4), h3 - Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Scenario 2: Recurrent Inpatient"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN

    p = tf.add_paragraph()
    p.text = "Risk Probability: 72.7%\nPrediction: POSITIVE (>= 0.45)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_HIGH
    p.space_after = Pt(6)

    s2_pts = [
        "Patient Profile: 75 y/o female, 3 prior inpatient stays, 6-day stay, 22 medications.",
        "Clinical Comorbidity: Congestive heart failure primary diagnosis, HbA1c >8, insulin up-titrated.",
        "Discharge Protocol: Intensive transition bundle—home health nurse within 48h, clinical pharmacist reconciliation, 7-day expedited clinic follow-up."
    ]
    for pt in s2_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(4)

    # Scenario 3: Borderline Risk
    add_card(s6, Inches(0.8) + (col_w3 + gap3)*2, t3, col_w3, h3)
    sp3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0) + (col_w3 + gap3)*2, t3 + Inches(0.18), Inches(1.5), Inches(0.3))
    sp3.fill.solid()
    sp3.fill.fore_color.rgb = COLOR_RISK_BORDER
    sp3.line.fill.background()
    p = sp3.text_frame.paragraphs[0]
    p.text = "BORDERLINE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER

    tb = s6.shapes.add_textbox(Inches(1.0) + (col_w3 + gap3)*2, t3 + Inches(0.55), col_w3 - Inches(0.4), h3 - Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Scenario 3: Threshold Ambiguity"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN

    p = tf.add_paragraph()
    p.text = "Risk Probability: 48.3%\nPrediction: POSITIVE (>= 0.45)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_BORDER
    p.space_after = Pt(6)

    s3_pts = [
        "Patient Profile: 65 y/o male, ischemic heart disease, 1 prior ER visit, 4-day stay.",
        "Clinical Nuance: Probability lands at 48.3%—above 0.45 threshold, classified as POSITIVE, but placed in BORDERLINE tier (40–50%).",
        "Discharge Protocol: Prompts clinician to review discharge medications and schedule a 48h phone check-in."
    ]
    for pt in s3_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(4)

    attach_speaker_notes(
        s6,
        timing="4:15 – 6:45 (2 minutes 30 seconds)",
        say_script=(
            "[PRESENTER SWITCHES SCREEN TO RUNNING STREAMLIT BROWSER]\n\n"
            "Let us now examine GlucoShield in action through our working Streamlit clinical prototype. "
            "Notice first our clean clinical dashboard and prominent educational prototype disclaimer: "
            "the system clearly informs users it is an academic decision support aid, not an autonomous device. "
            "To demonstrate real hospital workflows, we have embedded three clinical presets in the sidebar. "
            "First, Scenario 1: our Low-Risk, Negative case. A 45-year-old male on his first hospital stay with normal HbA1c. "
            "Clicking 'Assess Readmission Risk' processes the input through our validation pipeline. "
            "Our XGBoost model outputs a 27.1% readmission risk. Because this is below 0.45, the system assigns a green LOW RISK badge "
            "and populates a standard discharge checklist: routine nutrition coaching and standard 14 to 30 day outpatient follow-up. "
            "Next, Scenario 2: our High-Risk, Positive case. A 75-year-old female with congestive heart failure comorbidity, 3 prior admissions, "
            "and insulin up-titrated during a 6-day stay. Clicking assess yields a 72.7% readmission risk—triggering a red HIGH RISK alert. "
            "The system automatically activates an intensive transition bundle: assigning a home health nurse within 48 hours, mandatory clinical "
            "pharmacist medication reconciliation, and an expedited 7-day clinic follow-up. "
            "Finally, Scenario 3: our Borderline case. A 65-year-old male with ischemic heart disease whose probability lands at 48.3%. "
            "Notice our dual-boundary logic: because 48.3% exceeds the 0.45 threshold, the operational prediction is POSITIVE, but the display "
            "shows BORDERLINE MODERATE RISK (40 to 50%), alerting the physician to review medications before finalizing discharge. "
            "[PRESENTER SWITCHES BACK TO SLIDES]"
        ),
        understand_text=(
            "The working prototype reliably stratifies patients across 3 presets: Low Risk (27.1%, Negative), High Risk (72.7%, Positive), "
            "and Borderline (48.3%, Positive). Operational cutoff 0.45 governs binary decisions; visual tiers triage urgency."
        ),
        action_cue=(
            "Alt-Tab to browser running http://localhost:8501. Walk through Scenario 1, Scenario 2, and Scenario 3. "
            "Show TreeSHAP and the discharge checklist. Alt-Tab back to PowerPoint."
        )
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 7: Explainable AI and MLOps (6:45–7:45)
    # ═════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, COLOR_BG)
    add_header(s7, 7, "Explainable AI (TreeSHAP) & MLOps Drift Monitoring", "XAI & MLOps", "6:45 – 7:45 (60s)")

    # Left: TreeSHAP Interpretability
    w7 = Inches(5.7)
    t7 = Inches(1.4)
    h7 = Inches(5.6)
    add_card(s7, Inches(0.8), t7, w7, h7)

    tb = s7.shapes.add_textbox(Inches(1.0), t7 + Inches(0.15), w7 - Inches(0.4), h7 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "REAL-TIME TreeSHAP LOCAL EXPLAINABILITY"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    shap_points = [
        "12ms Real-Time Bedside Attribution: TreeExplainer decomposes mathematical log-odds contribution of every clinical factor for the specific patient.",
        "Transparent Directional Drivers:\n• Factors Increasing Risk: Prior inpatient encounters (+), HbA1c >8 (+), insulin titration 'Up' (+), advanced age (+).\n• Factors Decreasing Risk: Shorter length of stay (-), stable metformin (-), absence of recent ER visits (-).",
        "Clinical Actionability: Clinicians do not adopt black boxes. Knowing that insulin titration drove a patient's score allows pharmacists to focus discharge counseling specifically on hypoglycemia prevention.",
        "Caveat Enforced: SHAP explains model predictive weights, not biological etiology or clinical causation."
    ]
    for pt in shap_points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(4)

    # Right: MLOps Drift Monitoring & Chart
    r_left7 = Inches(6.8)
    r_w7 = Inches(5.733)
    add_card(s7, r_left7, t7, r_w7, h7)

    tb = s7.shapes.add_textbox(r_left7 + Inches(0.2), t7 + Inches(0.15), r_w7 - Inches(0.4), Inches(0.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "POPULATION STABILITY INDEX (PSI) DRIFT AUDIT"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_BORDER

    if os.path.exists("plots/monitoring_drift.png"):
        s7.shapes.add_picture("plots/monitoring_drift.png", r_left7 + Inches(0.2), t7 + Inches(0.55), r_w7 - Inches(0.4), Inches(2.9))

    tb_drift = s7.shapes.add_textbox(r_left7 + Inches(0.2), t7 + Inches(3.55), r_w7 - Inches(0.4), Inches(1.9))
    tf_drift = tb_drift.text_frame
    tf_drift.word_wrap = True

    p = tf_drift.paragraphs[0]
    p.text = "EMPIRICAL DRIFT DETECTION (SIMULATED COHORTS):"
    p.font.name = "Segoe UI"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    drift_points = [
        "Month 1 (Stable Operations): PSI < 0.01 across all features -> Pipeline fully healthy.",
        "Month 2 (Simulated Winter Surge & Demographic Aging):\n• number_inpatient: PSI = 0.385 (Alert Threshold = 0.25)\n• age: PSI = 0.298  |  diag_1_group: PSI = 0.260\n• Retraining Review Triggered automatically.",
        "Academic Honesty: All monitoring batches are explicitly labelled as simulated cohorts for educational demonstration."
    ]
    for pt in drift_points:
        p = tf_drift.add_paragraph()
        p.text = pt
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(2)

    attach_speaker_notes(
        s7,
        timing="6:45 – 7:45 (60 seconds)",
        say_script=(
            "Healthcare professionals will never adopt a black box. In the right panel of our dashboard, we integrated "
            "TreeSHAP to provide sub-fifteen-millisecond local explainability. For our high-risk patient, TreeSHAP mathematically "
            "decomposes the log-odds, showing that prior inpatient admissions and insulin dosage titrations were the primary drivers "
            "pushing risk upward. This allows attending physicians to validate the clinical rationale and target specific risks—such "
            "as having a pharmacist coach on hypoglycemia prevention. "
            "However, deploying a model is only day one. In Module 6, we implemented an MLOps monitoring engine utilizing the "
            "Population Stability Index and Kolmogorov-Smirnov statistics. To demonstrate drift detection honestly, we simulated "
            "two production batches: Month 1, representing stable operations with PSI below 0.01; and Month 2, simulating a realistic "
            "winter respiratory surge and elderly demographic shift. As shown in our monitoring chart, the system immediately flagged "
            "high drift on inpatient stays (PSI 0.385) and age (PSI 0.298), crossing our 0.25 safety threshold and automatically triggering "
            "a retraining alert. This guarantees model reliability over time."
        ),
        understand_text=(
            "TreeSHAP provides bedside factor attribution in 12ms. MLOps drift monitoring tracks PSI and KS statistics; "
            "simulated Month 2 successfully triggered a retraining alert on inpatient utilization (PSI=0.385) and age (PSI=0.298)."
        ),
        action_cue="Point to the TreeSHAP points on the left, then gesture to the PSI drift chart on the right."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 8: Deployment, Testing, and Governance (7:45–8:45)
    # ═════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, COLOR_BG)
    add_header(s8, 8, "Production Engineering, Automated Testing & Governance", "Deployment & Governance", "7:45 – 8:45 (60s)")

    # 3 Column Architecture & Governance Cards
    c_w8 = Inches(3.7)
    c_g8 = Inches(0.3)
    c_t8 = Inches(1.4)
    c_h8 = Inches(5.6)

    # Col 1: Automated Testing Suite
    add_card(s8, Inches(0.8), c_t8, c_w8, c_h8)
    tb = s8.shapes.add_textbox(Inches(0.95), c_t8 + Inches(0.15), c_w8 - Inches(0.3), c_h8 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "AUTOMATED TEST SUITE (100% PASS)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    p1 = tf.add_paragraph()
    p1.text = "17 / 17 pytest Tests"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_RISK_LOW
    p1.space_after = Pt(4)

    test_pts = [
        "Preprocessing Tests: ICD-9 mapping (250->Diabetes, 428->Circulatory, unknown->Other).",
        "Artifact Loading: Validates preprocessor, XGBoost, and feature names exist and load clean.",
        "Input Validation: Rejects negative LOS, handles missing values via median/mode, enforces boundaries.",
        "Demonstration Presets: Proves Scenario 1 (<0.45), Scenario 2 (>0.45), and Scenario 3 (~0.48).",
        "FastAPI Integration: Verifies GET /health returns 200 and POST /predict accepts valid payloads.",
        "Stage 8 System Harness: 5/5 whole-chain tests pass (normal, missing, invalid, unseen, extreme outlier)."
    ]
    for pt in test_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(2.5)

    # Col 2: Deployment & Architecture
    add_card(s8, Inches(0.8) + c_w8 + c_g8, c_t8, c_w8, c_h8)
    tb = s8.shapes.add_textbox(Inches(0.95) + c_w8 + c_g8, c_t8 + Inches(0.15), c_w8 - Inches(0.3), c_h8 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "DEPLOYMENT ARCHITECTURE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    p1 = tf.add_paragraph()
    p1.text = "Microservice & Container"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    deploy_pts = [
        "Streamlit Dashboard: Real-time decision support UI served on port 8501.",
        "FastAPI Microservice: High-throughput programmatic REST API on port 8000 with Pydantic validation schemas.",
        "Docker Containerization: Python 3.11-slim base image, multi-stage build, .dockerignore hygiene, container HEALTHCHECK included.",
        "Experiment Tracking: CSV/JSON run logging in evaluation/ capturing hyperparameters, ROC-AUC, and timestamps."
    ]
    for pt in deploy_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Col 3: Clinical Governance & Ethics
    add_card(s8, Inches(0.8) + (c_w8 + c_g8)*2, c_t8, c_w8, c_h8)
    tb = s8.shapes.add_textbox(Inches(0.95) + (c_w8 + c_g8)*2, c_t8 + Inches(0.15), c_w8 - Inches(0.3), c_h8 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "RESPONSIBLE AI & GOVERNANCE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p1 = tf.add_paragraph()
    p1.text = "9 Governance Documents"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    gov_pts = [
        "HIPAA Safe Harbor: UCI dataset fully de-identified; zero PHI or patient identifiers collected or retained.",
        "Human-in-the-Loop: System strictly provides advisory risk scores; clinicians retain sole authority to modify care.",
        "Demographic Fairness Audit: Verified 0.45 cutoff does not produce disparate false negative rates across gender and racial groups.",
        "Comprehensive Governance Suite: Model card, architecture spec, monitoring plan, drift audit, maintenance SLOs."
    ]
    for pt in gov_pts:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    attach_speaker_notes(
        s8,
        timing="7:45 – 8:45 (60 seconds)",
        say_script=(
            "Production readiness demands engineering rigor. We implemented a comprehensive verification suite: "
            "seventeen automated pytest tests covering data pipelines, artifact loading, boundary validation, presets, "
            "and FastAPI endpoints—passing with 100% reliability. In addition, our Stage 8 robustness harness validated "
            "five whole-chain edge cases: missing value imputation, negative length-of-stay rejection, unseen category handling, "
            "and extreme clinical outliers. "
            "For deployment, we packaged the system into a Docker container running Python 3.11-slim, exposing our Streamlit "
            "dashboard on port 8501 and an optional FastAPI microservice on port 8000. "
            "Crucially, we instituted rigorous clinical governance: the underlying dataset adheres strictly to HIPAA Safe Harbor "
            "de-identification. No protected health information is stored or transmitted. The system enforces human-in-the-loop "
            "oversight—it has zero autonomous diagnostic authority. And we documented the entire lifecycle across nine comprehensive "
            "governance documents, including a standardized Model Card and Support & Maintenance Plan."
        ),
        understand_text=(
            "GlucoShield is production-engineered with 17/17 passing pytest tests, 5 Stage 8 edge-case checks, Docker packaging, "
            "FastAPI REST endpoints, HIPAA compliance, and a complete 9-document clinical governance suite."
        ),
        action_cue="Emphasize 17/17 pytest tests passing and the 9 governance documents."
    )

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 9: Retrospective, Future Work, and Conclusion (8:45–9:30)
    # ═════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, COLOR_BG)
    add_header(s9, 9, "Project Retrospective, Future Roadmap & Conclusion", "Retrospective & Roadmap", "8:45 – 9:30 (45s)")

    # 3 Column Layout: What Worked Well | Limitations | Future Work
    c_w9 = Inches(3.7)
    c_g9 = Inches(0.3)
    c_t9 = Inches(1.4)
    c_h9 = Inches(4.3)

    # Card 1: Key Learnings
    add_card(s9, Inches(0.8), c_t9, c_w9, c_h9)
    tb = s9.shapes.add_textbox(Inches(0.95), c_t9 + Inches(0.15), c_w9 - Inches(0.3), c_h9 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "WHAT WORKED WELL"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    p1 = tf.add_paragraph()
    p1.text = "Key Engineering Learnings"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    learnings = [
        "Causal Data Hygiene: Removing deceased patients eliminated artificial leakage that would distort readmission probabilities.",
        "Clinical Threshold Sweeping: Shifting from 0.50 to 0.45 cutoff proved that threshold tuning is far more impactful than chasing incremental AUC.",
        "Fast Explainability: TreeSHAP delivered 12ms attribution, solving the clinician black-box objection without lag."
    ]
    for it in learnings:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Card 2: Technical Limitations
    add_card(s9, Inches(0.8) + c_w9 + c_g9, c_t9, c_w9, c_h9)
    tb = s9.shapes.add_textbox(Inches(0.95) + c_w9 + c_g9, c_t9 + Inches(0.15), c_w9 - Inches(0.3), c_h9 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KNOWN LIMITATIONS"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_RISK_BORDER

    p1 = tf.add_paragraph()
    p1.text = "Dataset & Clinical Bounds"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    limits = [
        "Claims Data Constraints: Dataset lacks bedside vital signs, nursing progress notes, and outpatient medication adherence.",
        "Absence of SDoH: No data on Social Determinants of Health (housing instability, food access, transportation barrier).",
        "Historical Coding: Utilizes legacy ICD-9 categories rather than modern granular ICD-10-CM codes."
    ]
    for it in limits:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Card 3: Future Roadmap
    add_card(s9, Inches(0.8) + (c_w9 + c_g9)*2, c_t9, c_w9, c_h9)
    tb = s9.shapes.add_textbox(Inches(0.95) + (c_w9 + c_g9)*2, c_t9 + Inches(0.15), c_w9 - Inches(0.3), c_h9 - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "FUTURE ROADMAP"
    p.font.name = "Segoe UI"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE

    p1 = tf.add_paragraph()
    p1.text = "Next-Gen Enhancements"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_MAIN
    p1.space_after = Pt(4)

    roadmap = [
        "Prospective Multi-Center Validation: Partner with active health systems to validate on contemporary EHR data.",
        "HL7 / FHIR Integration: Connect directly into hospital EHR workflows (Epic, Cerner) via standard FHIR APIs.",
        "SDoH & ICD-10 Modernization: Incorporate Z-codes for social risk and upgrade diagnostic taxonomy to ICD-10-CM."
    ]
    for it in roadmap:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_after = Pt(3)

    # Bottom Closing Thank You Banner
    bot_card = add_card(s9, Inches(0.8), Inches(5.85), Inches(11.733), Inches(1.3), COLOR_SURFACE, COLOR_PRIMARY_BLUE)
    btb = s9.shapes.add_textbox(Inches(1.0), Inches(5.92), Inches(11.333), Inches(1.15))
    btf = btb.text_frame
    btf.word_wrap = True

    bp0 = btf.paragraphs[0]
    bp0.text = "GlucoShield — Supporting Better-Informed Discharge Planning Through Explainable AI"
    bp0.font.name = "Segoe UI"
    bp0.font.size = Pt(13)
    bp0.font.bold = True
    bp0.font.color.rgb = COLOR_TEXT_MAIN

    bp1 = btf.add_paragraph()
    bp1.text = (
        "Thank you to our FUSE AI-201 faculty, mentors, and fellow cohorts.\n"
        "Presented by Bililign Yibgeta Amare on behalf of Group 04 | YEEAP Capstone\n"
        "We welcome your evaluation, feedback, and technical questions."
    )
    bp1.font.name = "Segoe UI"
    bp1.font.size = Pt(9.5)
    bp1.font.color.rgb = COLOR_TEAL

    attach_speaker_notes(
        s9,
        timing="8:45 – 9:30 (45 seconds)",
        say_script=(
            "Reflecting on our capstone journey, our primary engineering lesson was that data hygiene and threshold "
            "calibration matter far more than chasing marginal hyperparameter gains. Removing deceased patients eliminated "
            "fatal causal leakage, while tuning our decision cutoff to 0.45 unlocked practical clinical sensitivity. "
            "We are completely candid about our limitations: administrative claims data lacks bedside vital signs, nursing notes, "
            "and Social Determinants of Health like housing and food security. In our future roadmap, we plan to validate GlucoShield "
            "prospectively across modern EHR systems via HL7 and FHIR standards, upgrade to ICD-10, and incorporate social risk indices. "
            "In conclusion: GlucoShield demonstrates how explainable machine learning can support discharge planning teams to reduce "
            "readmissions and safeguard patient health. "
            "On behalf of Group 04, thank you to our instructors, mentors, and assessors. We now welcome your evaluation and questions."
        ),
        understand_text=(
            "Honest reflection of learnings (causal hygiene, threshold tuning) and limitations (lack of SDoH and vital signs). "
            "Strong closing statement on clinical decision support with gratitude to faculty and readiness for Q&A."
        ),
        action_cue="Conclude speaking at 9:30 mark; hold slide 9 on screen for evaluator Q&A."
    )

    prs.save(PATH_PPTX)
    print(f"PowerPoint successfully created: {PATH_PPTX} (9 slides)")

# ─────────────────────────────────────────────────────────────────────────────
# BUILD THE COMPLETE DOCX SPEAKING SCRIPT
# ─────────────────────────────────────────────────────────────────────────────
def build_docx_script():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = DocxInches(1.0)
        section.bottom_margin = DocxInches(1.0)
        section.left_margin = DocxInches(1.0)
        section.right_margin = DocxInches(1.0)

    # Document Header Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("GLUCOSHIELD CLINICAL DECISION SUPPORT SYSTEM")
    r.font.name = "Segoe UI"
    r.font.size = DocxPt(18)
    r.font.bold = True
    r.font.color.rgb = DocxRGBColor(30, 58, 138)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub.add_run("FUSE AI-201 Module 6 Capstone — Complete 10-Minute Presentation Script & Cues")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = DocxPt(11)
    r_sub.font.color.rgb = DocxRGBColor(71, 85, 105)

    doc.add_paragraph().paragraph_format.space_after = DocxPt(6)

    # Metadata Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course & Project", "FUSE AI-201: AI Model Development & MLOps | Module 6 Capstone"),
        ("Project Title", "GlucoShield — Diabetes Hospital Readmission Risk Predictor"),
        ("Project Group", "Group 04 | Youth Empowerment and Employment in AI Program (YEEAP)"),
        ("Lead Presenter", "Bililign Yibgeta Amare (Team Lead)"),
        ("Target Duration", "9 Minutes 30 Seconds (Max 10:00) | Live Streamlit Demo Included"),
        ("Evaluation Audience", "Academic Capstone Reviewers, AI Mentors, and Healthcare ML Evaluators")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        cell0, cell1 = row.cells[0], row.cells[1]
        cell0.width = DocxInches(2.0)
        cell1.width = DocxInches(4.5)
        
        p0 = cell0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.bold = True
        r0.font.size = DocxPt(9.5)
        r0.font.name = "Segoe UI"

        p1 = cell1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = DocxPt(9.5)
        r1.font.name = "Segoe UI"

    doc.add_paragraph().paragraph_format.space_after = DocxPt(12)

    # Deck Structure Table
    h2 = doc.add_paragraph()
    r = h2.add_run("1. Master Presentation Deck Structure & Timing Allocation")
    r.font.name = "Segoe UI"
    r.font.size = DocxPt(13)
    r.font.bold = True
    r.font.color.rgb = DocxRGBColor(30, 58, 138)

    deck_table = doc.add_table(rows=10, cols=4)
    deck_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Slide #", "Section Title", "Timing", "Core Visual / Presenter Action"]
    for col_idx, h in enumerate(headers):
        cell = deck_table.cell(0, col_idx)
        cell.text = h
        for p in cell.paragraphs:
            p.runs[0].font.bold = True
            p.runs[0].font.size = DocxPt(9.5)
            p.runs[0].font.name = "Segoe UI"

    slides_info = [
        ("Slide 1", "Title & Project Introduction", "0:00 – 0:30 (30s)", "Executive title card, team metadata, system highlights"),
        ("Slide 2", "Problem & Industry Motivation", "0:30 – 1:15 (45s)", "Clinical burden, HRRP penalties, Problem-to-Solution flow"),
        ("Slide 3", "Dataset & Causal Preprocessing", "1:15 – 2:15 (60s)", "4-stage pipeline: 101k raw -> 69k clean -> 9 ICD-9 groups"),
        ("Slide 4", "Model Benchmarking & Selection", "2:15 – 3:15 (60s)", "Multi-model table (5 families) + Holdout ROC curves"),
        ("Slide 5", "Evaluation & Threshold Calibration", "3:15 – 4:15 (60s)", "5 KPI cards (65.71% recall) + Confusion matrix (826 TP)"),
        ("Slide 6", "Live Prototype Demonstration", "4:15 – 6:45 (150s)", "Switch to Streamlit app: Scenario 1 (27%), Scenario 2 (72%), Scenario 3 (48%)"),
        ("Slide 7", "TreeSHAP XAI & MLOps Drift", "6:45 – 7:45 (60s)", "TreeSHAP bedside attribution + PSI drift chart (PSI=0.385)"),
        ("Slide 8", "Testing, Deployment & Governance", "7:45 – 8:45 (60s)", "17/17 pytest + 5/5 Stage 8 checks + Docker/FastAPI architecture"),
        ("Slide 9", "Retrospective, Roadmap & Wrap-Up", "8:45 – 9:30 (45s)", "Learnings, limitations, future FHIR roadmap, final thank you")
    ]
    for row_idx, s in enumerate(slides_info, start=1):
        for col_idx, text in enumerate(s):
            cell = deck_table.cell(row_idx, col_idx)
            cell.text = text
            for p in cell.paragraphs:
                p.runs[0].font.size = DocxPt(9)
                p.runs[0].font.name = "Segoe UI"

    doc.add_page_break()

    # Detailed Slide-by-Slide Script
    h_script = doc.add_paragraph()
    r = h_script.add_run("2. Complete Verbatim Speaking Script & Cues")
    r.font.name = "Segoe UI"
    r.font.size = DocxPt(14)
    r.font.bold = True
    r.font.color.rgb = DocxRGBColor(30, 58, 138)

    detailed_scripts = [
        (
            "Slide 1: Title & Project Introduction",
            "0:00 – 0:30 (30 seconds)",
            "Introduce GlucoShield, Group 04, presenter, and presentation roadmap.",
            "Display Slide 1 full screen; maintain confident executive tone.",
            (
                "Good morning, esteemed mentors, evaluators, and colleagues. My name is Bililign Yibgeta Amare, "
                "and on behalf of Group 04 in the Youth Empowerment and Employment in AI Program, I am proud "
                "to present our FUSE AI-201 Capstone project: GlucoShield — an AI-powered Clinical Decision Support "
                "System for predicting 30-day hospital readmission risk among diabetic inpatients. "
                "Our team engineered an end-to-end, tested, containerized, and explainable decision support prototype. "
                "Over the next nine minutes, I will guide you through our clinical problem, causal preprocessing pipeline, "
                "model benchmarking, threshold calibration, a live demonstration of our working prototype, TreeSHAP "
                "explainability, and our MLOps drift monitoring system. Let us examine the clinical problem."
            )
        ),
        (
            "Slide 2: Clinical Problem & Industry Motivation",
            "0:30 – 1:15 (45 seconds)",
            "Explain diabetes burden, HRRP financial penalties, LACE limitations, and the GlucoShield workflow.",
            "Advance to Slide 2; highlight the 3 burden cards and the bottom flow diagram.",
            (
                "Diabetes affects more than five hundred million individuals worldwide. When diabetic patients are hospitalized, "
                "managing their acute recovery is notoriously complex—it demands stabilizing glycemic swings, adjusting multi-drug "
                "regimens, and treating chronic cardiovascular or renal comorbidities. Under the CMS Hospital Readmissions Reduction "
                "Program, hospitals face penalties of up to 3% of their total Medicare reimbursements for excessive 30-day readmissions, "
                "costing the healthcare system over seventeen billion dollars annually. "
                "Currently, discharge planning teams rely on clinical intuition or static heuristics like the LACE index. "
                "These tools suffer from three fundamental limitations: they are linear, they completely ignore medication changes "
                "and lab glycemic indicators, and they are calculated right at discharge—far too late to mobilize post-discharge care. "
                "GlucoShield bridges this gap: analyzing inpatient encounter history with machine learning to generate an explainable "
                "risk score that drives personalized transition care before the patient leaves the hospital."
            )
        ),
        (
            "Slide 3: Dataset Hygiene & Causal Engineering Pipeline",
            "1:15 – 2:15 (60 seconds)",
            "Explain causal leakage audit (removing expired/hospice records), patient deduplication, 9 ICD-9 groups, and 80/20 holdout split.",
            "Advance to Slide 3; gesture across the 4 pipeline stages from left to right.",
            (
                "To build a clinically valid model, data hygiene must be uncompromising. We utilized the gold-standard UCI Diabetes "
                "130-US Hospitals dataset, containing 101,766 inpatient encounters across a ten-year period from 1999 to 2008. "
                "First, we conducted a causal cohort audit: we identified and removed 2,423 patients who expired in the hospital or "
                "transited to hospice. Including deceased patients introduces severe causal leakage, because readmission is logically "
                "impossible. Next, to prevent patient-level test leakage, we deduplicated repeat encounters, retaining strictly each "
                "unique patient's first indexed admission, yielding a clean cohort of 69,990 encounters. "
                "Third, raw ICD-9 diagnosis codes spanned over eight hundred discrete numbers. One-hot encoding them all would cause a "
                "catastrophic explosion of sparse noise. We mapped them into nine clinically sound organ-system categories—such as "
                "Circulatory, Respiratory, and Diabetes with comorbidities—and engineered composite clinical features including "
                "procedure intensity, medications per day, and prior hospital utilization. "
                "Finally, our clean cohort exhibited acute class imbalance: only 8.98% readmitted within 30 days. We split the dataset "
                "strictly 80/20, locking away 13,998 patients for untouched holdout evaluation."
            )
        ),
        (
            "Slide 4: Model Benchmarking & Selection",
            "2:15 – 3:15 (60 seconds)",
            "Explain benchmarking of 5 model families, class imbalance defense, Random Forest overfitting, and why XGBoost was selected.",
            "Advance to Slide 4; point to the comparison table and the ROC curve on the right.",
            (
                "With only 8.98% positive readmissions, an unweighted model falls into the majority-class trap—it predicts zero for everyone "
                "and claims 91% accuracy while catching zero patients at risk. We established a reproducible experiment tracking pipeline "
                "and evaluated five model architectures on our untouched holdout test set of 13,998 patients. "
                "Our majority-class baseline scored 0.50 ROC-AUC. Regularized Logistic Regression established a solid linear lower bound at "
                "0.647 ROC-AUC. Random Forest achieved 0.805 on the training set but dropped to 0.646 on holdout test data, demonstrating "
                "severe tree-memorization of hospital administrative noise. LightGBM and XGBoost both achieved 0.647 ROC-AUC. "
                "We selected XGBoost as our primary operational engine because it provided the highest clinical sensitivity (65.71% at our "
                "calibrated cutoff), controlled generalization error through strict L1 and L2 regularization penalties, and native "
                "compatibility with high-speed TreeSHAP local explainability."
            )
        ),
        (
            "Slide 5: Evaluation & Threshold Calibration",
            "3:15 – 4:15 (60 seconds)",
            "Explain holdout metrics (0.6465 AUC, 65.71% recall), confusion matrix (826 TP), clinical rationale for 0.45 cutoff, and error audit.",
            "Advance to Slide 5; walk through the 5 top cards, point to 826 TP, and explain False Negative audit.",
            (
                "In clinical screening, errors carry asymmetric stakes. A False Negative—missing an at-risk diabetic patient—can lead to "
                "severe relapse, diabetic ketoacidosis, or death. Conversely, a False Positive—scheduling an extra telephone check-in for "
                "a patient who might have managed fine—is a safe, benign clinical action. "
                "At the standard default threshold of 0.50, our XGBoost model achieved 51.9% recall, missing nearly half of all readmissions. "
                "By systematically evaluating threshold sweeps, we calibrated our operational decision boundary to 0.45. "
                "Operating at 0.45 boosted our clinical sensitivity to 65.71%, successfully intercepting 826 out of 1,257 true readmissions "
                "in our holdout test set. We accept a precision of 12.48% because the prevalence of 30-day readmission is naturally low at 8.98%. "
                "We also conducted an error audit on the 431 False Negatives: these patients had virtually zero prior admissions (averaging 0.04) "
                "and shorter hospitalizations. They appeared outwardly healthy upon discharge, pointing to post-discharge social determinants "
                "like medication unaffordability or lack of home caregivers. This reinforces why AI must assist, not replace, clinical case managers."
            )
        ),
        (
            "Slide 6: Live Clinical Prototype Demonstration",
            "4:15 – 6:45 (2 minutes 30 seconds)",
            "Demonstrate working Streamlit app: Scenario 1 (Low 27%), Scenario 2 (High 72%), Scenario 3 (Borderline 48%), and explain dual boundary.",
            "Alt-Tab to Streamlit app at http://localhost:8501. Execute live scenarios. Alt-Tab back to slides.",
            (
                "[PRESENTER ACTIONS: Switch screen to browser running Streamlit dashboard at http://localhost:8501]\n\n"
                "Let us now examine our working clinical prototype running live in Streamlit. "
                "Notice first our clean clinical layout and prominent educational prototype notice: the application clearly states it is an "
                "academic decision support aid and not an autonomous diagnostic device. "
                "To demonstrate real hospital workflows, we pre-loaded three clinical scenarios in the sidebar. "
                "First, Scenario 1: our Low-Risk, Negative case. A 45-year-old male on his first hospital stay with normal HbA1c. "
                "Clicking 'Assess Readmission Risk' validates inputs and transforms the record. Our XGBoost model outputs a 27.1% readmission risk. "
                "Because this is below 0.45, the dashboard renders a green LOW RISK badge and populates a routine discharge checklist: standard "
                "diabetes nutrition education and standard 14 to 30 day primary care follow-up. "
                "Next, Scenario 2: our High-Risk, Positive case. A 75-year-old female with congestive heart failure comorbidity, 3 prior admissions, "
                "and insulin up-titrated during a 6-day stay. Clicking assess yields a 72.7% readmission risk—triggering a red HIGH RISK alert. "
                "The system automatically activates an intensive transition bundle: assigning a home health nurse within 48 hours, mandatory "
                "pharmacist medication reconciliation, and an expedited 7-day clinic follow-up. "
                "Finally, Scenario 3: our Borderline case. A 65-year-old male with ischemic heart disease whose probability lands at 48.3%. "
                "Notice our dual-boundary logic: because 48.3% exceeds the 0.45 cutoff, the operational prediction is POSITIVE, but the display "
                "shows BORDERLINE MODERATE RISK (40 to 50%), alerting the physician to review medications before finalizing discharge. "
                "[PRESENTER ACTIONS: Return to PowerPoint presentation]"
            )
        ),
        (
            "Slide 7: Explainable AI & MLOps Drift Monitoring",
            "6:45 – 7:45 (60 seconds)",
            "Explain TreeSHAP bedside attribution (12ms), PSI drift monitoring, simulated cohorts (Month 1 stable vs Month 2 surge), and retraining trigger.",
            "Advance to Slide 7; point to TreeSHAP drivers on the left, then gesture to the PSI drift chart on the right.",
            (
                "Healthcare professionals will never adopt a black box. In the right panel of our dashboard, we integrated TreeSHAP to "
                "provide sub-fifteen-millisecond local explainability. For our high-risk patient, TreeSHAP mathematically decomposes the log-odds, "
                "showing that prior inpatient admissions and insulin dosage titrations were the primary drivers pushing risk upward. "
                "This allows attending physicians to validate the clinical rationale and target specific risks—such as having a pharmacist "
                "coach on hypoglycemia prevention. "
                "However, deploying a model is only day one. In Module 6, we implemented an MLOps monitoring engine utilizing the "
                "Population Stability Index and Kolmogorov-Smirnov statistics. To demonstrate drift detection honestly, we simulated "
                "two production batches: Month 1, representing stable operations with PSI below 0.01; and Month 2, simulating a realistic "
                "winter respiratory surge and elderly demographic shift. As shown in our monitoring chart, the system immediately flagged "
                "high drift on inpatient stays (PSI 0.385) and age (PSI 0.298), crossing our 0.25 safety threshold and automatically triggering "
                "a retraining alert. This guarantees model reliability over time."
            )
        ),
        (
            "Slide 8: Production Engineering, Testing & Governance",
            "7:45 – 8:45 (60 seconds)",
            "Explain 17/17 pytest tests, 5 Stage 8 edge-case checks, Docker container, FastAPI microservice, and HIPAA governance.",
            "Advance to Slide 8; emphasize 17/17 tests passing, Docker packaging, and the 9-document governance suite.",
            (
                "Production readiness demands engineering rigor. We implemented a comprehensive verification suite: seventeen automated "
                "pytest tests covering data pipelines, artifact loading, boundary validation, presets, and FastAPI endpoints—passing with "
                "100% reliability. In addition, our Stage 8 robustness harness validated five whole-chain edge cases: missing value imputation, "
                "negative length-of-stay rejection, unseen category handling, and extreme clinical outliers. "
                "For deployment, we packaged the system into a Docker container running Python 3.11-slim, exposing our Streamlit dashboard on "
                "port 8501 and an optional FastAPI microservice on port 8000. "
                "Crucially, we instituted rigorous clinical governance: the underlying dataset adheres strictly to HIPAA Safe Harbor "
                "de-identification. No protected health information is stored or transmitted. The system enforces human-in-the-loop oversight—it "
                "has zero autonomous diagnostic authority. And we documented the entire lifecycle across nine comprehensive governance "
                "documents, including a standardized Model Card and Support & Maintenance Plan."
            )
        ),
        (
            "Slide 9: Retrospective, Future Roadmap & Conclusion",
            "8:45 – 9:30 (45 seconds)",
            "Summarize key learnings (causal hygiene, threshold tuning), acknowledge limitations (lack of SDoH), outline FHIR roadmap, and conclude.",
            "Advance to Slide 9; deliver confident concluding statement; leave slide on screen for Q&A.",
            (
                "Reflecting on our capstone journey, our primary engineering lesson was that data hygiene and threshold calibration matter "
                "far more than chasing marginal hyperparameter gains. Removing deceased patients eliminated fatal causal leakage, while tuning "
                "our decision cutoff to 0.45 unlocked practical clinical sensitivity. "
                "We are completely candid about our limitations: administrative claims data lacks bedside vital signs, nursing notes, and Social "
                "Determinants of Health like housing and food security. In our future roadmap, we plan to validate GlucoShield prospectively "
                "across modern EHR systems via HL7 and FHIR standards, upgrade to ICD-10, and incorporate social risk indices. "
                "In conclusion: GlucoShield demonstrates how explainable machine learning can support discharge planning teams to reduce "
                "readmissions and safeguard patient health. "
                "On behalf of Group 04, thank you to our instructors, mentors, and assessors. We now welcome your evaluation and questions."
            )
        )
    ]

    for title, timing, takeaway, cue, script in detailed_scripts:
        p_sec = doc.add_paragraph()
        p_sec.paragraph_format.space_before = DocxPt(14)
        p_sec.paragraph_format.space_after = DocxPt(2)
        r = p_sec.add_run(f"■ {title}")
        r.font.name = "Segoe UI"
        r.font.size = DocxPt(12)
        r.font.bold = True
        r.font.color.rgb = DocxRGBColor(30, 58, 138)

        # Timing and Cue block
        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_after = DocxPt(4)
        r_time = p_info.add_run(f"Timing: {timing}  |  Presenter Cue: {cue}\n")
        r_time.font.name = "Segoe UI"
        r_time.font.size = DocxPt(9.5)
        r_time.font.bold = True
        r_time.font.color.rgb = DocxRGBColor(15, 118, 110)

        r_take = p_info.add_run(f"Key Takeaway: {takeaway}")
        r_take.font.name = "Segoe UI"
        r_take.font.size = DocxPt(9)
        r_take.font.italic = True
        r_take.font.color.rgb = DocxRGBColor(100, 116, 139)

        # Script Blockquote
        p_say = doc.add_paragraph()
        p_say.paragraph_format.left_indent = DocxInches(0.4)
        p_say.paragraph_format.right_indent = DocxInches(0.2)
        p_say.paragraph_format.space_after = DocxPt(10)
        r_say = p_say.add_run(f'"{script}"')
        r_say.font.name = "Georgia"
        r_say.font.size = DocxPt(10.5)
        r_say.font.color.rgb = DocxRGBColor(15, 23, 42)

    # Q&A Defense Strategy Section
    doc.add_page_break()
    h_qa = doc.add_paragraph()
    r = h_qa.add_run("3. Evaluator Q&A Defense Strategy & Technical Cheat Sheet")
    r.font.name = "Segoe UI"
    r.font.size = DocxPt(14)
    r.font.bold = True
    r.font.color.rgb = DocxRGBColor(30, 58, 138)

    qa_list = [
        (
            "Q1: Why is your test ROC-AUC only 0.6465? Isn't that low compared to typical ML benchmarks?",
            "Defense Answer: In administrative claims data for 30-day diabetes readmission, published literature benchmarks consistently range between 0.60 and 0.70 (e.g., Strack et al., 2014; Rubin, 2016). Claims data lacks bedside vitals, nursing progress notes, and outpatient social factors. Random Forest achieved 0.805 on the training set but collapsed to 0.646 on holdout test data, proving that higher training scores in this domain represent overfitting to hospital noise. Our 0.6465 is an honest, un-overfitted holdout result that outperforms standard clinical heuristics."
        ),
        (
            "Q2: Your precision at threshold 0.45 is only 12.48%. Does that produce too many false alarms?",
            "Defense Answer: In hospital discharge planning, False Negatives carry catastrophic risk (patient returns critically ill), while False Positives are safe and beneficial (an extra nurse telephone call or medication check-in). Furthermore, because the positive prevalence of 30-day readmissions is only 8.98%, Bayes' theorem dictates precision is mathematically bounded. By prioritizing sensitivity at 65.71%, we intercept two-thirds of all readmissions. The extra follow-up calls cost approximately $15 each, whereas an avoided readmission saves over $14,000."
        ),
        (
            "Q3: Why did you remove expired and hospice patients from the dataset?",
            "Defense Answer: Including patients who died in the hospital or were discharged to hospice care introduces fatal causal leakage. A deceased patient has a 0.0% physical possibility of readmission. If left in the dataset, the model would learn patterns that predict mortality rather than readmission risk, corrupting the predictive validity for surviving discharged patients. Removing them was an essential causal hygiene step."
        ),
        (
            "Q4: How do you guarantee patient privacy under HIPAA?",
            "Defense Answer: The UCI 130-US Hospitals dataset was completely de-identified under the HIPAA Safe Harbor method before public release. In our application, all patient inputs are processed strictly in ephemeral memory during the active session. No medical record numbers, names, or encounter data are ever written to disk, databases, or external APIs. In our Docker configuration, the API runs locally with no external telemetry."
        ),
        (
            "Q5: How does your MLOps drift detector protect against model decay?",
            "Defense Answer: We implemented Population Stability Index (PSI) and Kolmogorov-Smirnov test tracking. When incoming batches exceed our calibrated safety threshold of PSI 0.25 on primary predictors (such as prior inpatient visits or patient age), the monitoring pipeline triggers an automated retraining alert. This warns clinical engineering before performance degradation can impact patient care."
        )
    ]

    for q, a in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = DocxPt(8)
        p_q.paragraph_format.space_after = DocxPt(2)
        r_q = p_q.add_run(q)
        r_q.font.name = "Segoe UI"
        r_q.font.size = DocxPt(10.5)
        r_q.font.bold = True
        r_q.font.color.rgb = DocxRGBColor(185, 28, 28)

        p_a = doc.add_paragraph()
        p_a.paragraph_format.left_indent = DocxInches(0.2)
        p_a.paragraph_format.space_after = DocxPt(8)
        r_a = p_a.add_run(a)
        r_a.font.name = "Segoe UI"
        r_a.font.size = DocxPt(10)
        r_a.font.color.rgb = DocxRGBColor(30, 41, 59)

    doc.save(PATH_DOCX)
    print(f"Word Document script successfully created: {PATH_DOCX}")

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE HIGH-RESOLUTION PREVIEW IMAGES FOR EVERY SLIDE
# ─────────────────────────────────────────────────────────────────────────────
def generate_slide_previews():
    print("Generating slide preview PNGs...")
    
    slide_metadata = [
        ("Slide 1", "GlucoShield: AI-Powered Diabetes Readmission Risk Prediction", "Title & Introduction", "0:00 - 0:30", [
            ("PRESENTER", "Bililign Yibgeta Amare (Team Lead)"),
            ("AFFILIATION", "FUSE AI-201 Capstone | Group 04 | YEEAP"),
            ("DATASET", "101,766 US Inpatient Records (1999-2008)"),
            ("PRIMARY MODEL", "Calibrated XGBoost (Cutoff = 0.45)")
        ]),
        ("Slide 2", "Clinical Challenge & Problem Motivation", "Problem Statement", "0:30 - 1:15", [
            ("CLINICAL BURDEN", "537M+ diabetic adults; 2-3x higher 30-day readmissions"),
            ("FINANCIAL PENALTY", "CMS HRRP penalties up to 3%; $17B+ annual avoidable cost"),
            ("HEURISTIC LIMITS", "LACE index is linear, static, and ignores medication shifts"),
            ("SOLUTION WORKFLOW", "History -> XGBoost Risk -> TreeSHAP Explanation -> Targeted Care")
        ]),
        ("Slide 3", "Dataset Hygiene & Causal Engineering Pipeline", "Data Preparation", "1:15 - 2:15", [
            ("RAW COHORT", "101,766 records across 130 US hospitals (1999-2008)"),
            ("CAUSAL AUDIT", "2,423 expired/hospice records removed (zero causal leakage)"),
            ("DEDUPLICATION", "69,990 clean unique patient encounters retained"),
            ("FEATURE GROUPING", "800+ ICD-9 codes mapped to 9 clinically validated groups")
        ]),
        ("Slide 4", "Model Benchmarking & Architectural Selection", "Model Selection", "2:15 - 3:15", [
            ("BASELINE", "Majority Class: 0.500 ROC-AUC | 0.0% Recall"),
            ("LOGISTIC REG.", "L2 Regularized: 0.647 ROC-AUC | 53.1% Recall"),
            ("RANDOM FOREST", "Train AUC 0.805 -> Test AUC 0.646 (Severe Overfitting)"),
            ("XGBOOST (SELECTED)", "0.647 ROC-AUC | 65.71% Recall @ 0.45 Cutoff | Zero Overfit")
        ]),
        ("Slide 5", "Evaluation Metrics & Threshold Calibration", "Model Evaluation", "3:15 - 4:15", [
            ("ROC-AUC / PR-AUC", "0.6465 ROC-AUC | 0.158 PR-AUC on holdout test set (n=13,998)"),
            ("SENSITIVITY / RECALL", "65.71% sensitivity at 0.45 cutoff (826 True Readmissions caught)"),
            ("CONFUSION MATRIX", "TP: 826 | FN: 431 | TN: 6,949 | FP: 5,792"),
            ("ERROR AUDIT", "Missed cases had 0.04 prior visits; reflects outpatient social barriers")
        ]),
        ("Slide 6", "Live Clinical Prototype Demonstration", "Prototype Demo", "4:15 - 6:45", [
            ("SCENARIO 1 (LOW)", "Prob: 27.1% | LOW RISK | NEGATIVE (< 0.45) | Routine Care"),
            ("SCENARIO 2 (HIGH)", "Prob: 72.7% | HIGH RISK | POSITIVE (>= 0.45) | 48h Home Nurse"),
            ("SCENARIO 3 (BORDER)", "Prob: 48.3% | BORDERLINE | POSITIVE (>= 0.45) | Med Reconciliation"),
            ("PRESENTER ACTION", "Switch to Streamlit app at http://localhost:8501 for live tour")
        ]),
        ("Slide 7", "TreeSHAP Explainability & MLOps Drift Monitoring", "XAI & MLOps", "6:45 - 7:45", [
            ("TreeSHAP (12ms)", "Local attribution decomposes patient log-odds into clinical factors"),
            ("KEY RISK DRIVERS", "Prior inpatient stays (+), HbA1c >8 (+), insulin titration Up (+)"),
            ("DRIFT MONITORING", "Population Stability Index (PSI) & Kolmogorov-Smirnov tests"),
            ("SIMULATED SURGE", "Month 2 Drift Detected: inpatient PSI=0.385, age PSI=0.298 (Retrain)")
        ]),
        ("Slide 8", "Production Engineering, Automated Testing & Governance", "Deployment & Governance", "7:45 - 8:45", [
            ("AUTOMATED TESTS", "17/17 pytest tests PASS (preprocessing, models, bounds, API)"),
            ("STAGE 8 HARNESS", "5/5 whole-chain robustness checks PASS (missing, outliers, invalid)"),
            ("DEPLOYMENT", "Streamlit (port 8501) + FastAPI (port 8000) in Docker (Python 3.11)"),
            ("AI GOVERNANCE", "HIPAA Safe Harbor compliant; zero PHI stored; human-in-the-loop")
        ]),
        ("Slide 9", "Project Retrospective, Future Roadmap & Conclusion", "Retrospective & Roadmap", "8:45 - 9:30", [
            ("KEY LEARNINGS", "Causal data hygiene and threshold sweeping beat raw hyperparameter tuning"),
            ("LIMITATIONS", "Administrative data lacks bedside vitals, nursing notes, and SDoH"),
            ("FUTURE ROADMAP", "Prospective EHR validation (HL7/FHIR), ICD-10-CM, and social risk"),
            "CLOSING REMARK: GlucoShield - Supporting Better-Informed Discharge Planning"
        ])
    ]

    preview_paths = []

    for idx, (s_num, s_title, cat, timing, details) in enumerate(slide_metadata, start=1):
        fig, ax = plt.subplots(figsize=(13.333, 7.5), dpi=100)
        fig.patch.set_facecolor('#0B1220')
        ax.set_facecolor('#0B1220')
        ax.axis('off')

        # Top Accent Line
        ax.plot([0.06, 0.94], [0.95, 0.95], color='#2563EB', linewidth=3)

        # Category and Timing
        ax.text(0.06, 0.91, f"GLUCOSHIELD CDSS  |  {cat.upper()}  |  SLIDE {idx} OF 9", 
                color='#14B8A6', fontsize=11, fontweight='bold', fontfamily='sans-serif')
        ax.text(0.94, 0.91, f"TIMING: {timing}", 
                color='#94A3B8', fontsize=11, fontweight='bold', fontfamily='sans-serif', ha='right')

        # Slide Title
        ax.text(0.06, 0.83, s_title, 
                color='#F8FAFC', fontsize=20, fontweight='bold', fontfamily='sans-serif')

        # Body Cards (2x2 grid)
        coords = [
            (0.06, 0.44, 0.42, 0.32),
            (0.52, 0.44, 0.42, 0.32),
            (0.06, 0.08, 0.42, 0.32),
            (0.52, 0.08, 0.42, 0.32)
        ]

        if isinstance(details, list):
            for c_idx, item in enumerate(details):
                cx, cy, cw, ch = coords[c_idx]
                rect = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0.015",
                                              facecolor='#1E293B', edgecolor='#334155', linewidth=1.5)
                ax.add_patch(rect)
                
                # Card top strip
                strip_colors = ['#2563EB', '#14B8A6', '#D97706', '#60A5FA']
                ax.plot([cx, cx + cw], [cy + ch, cy + ch], color=strip_colors[c_idx], linewidth=3.5)

                if isinstance(item, tuple):
                    hdr, bdy = item
                    ax.text(cx + 0.02, cy + ch - 0.05, hdr, color='#94A3B8', fontsize=10, fontweight='bold', fontfamily='sans-serif')
                    ax.text(cx + 0.02, cy + ch - 0.12, bdy, color='#F8FAFC', fontsize=11, fontfamily='sans-serif', wrap=True)
                else:
                    ax.text(cx + 0.02, cy + ch - 0.10, str(item), color='#F8FAFC', fontsize=11, fontfamily='sans-serif', wrap=True)

        out_img = os.path.join(DIR_PREVIEWS, f"slide_{idx:02d}_preview.png")
        plt.tight_layout()
        plt.savefig(out_img, facecolor='#0B1220', edgecolor='none')
        plt.close()
        preview_paths.append(out_img)

    # Generate composite 3x3 Overview Image
    print("Generating composite presentation overview...")
    fig, axes = plt.subplots(3, 3, figsize=(18, 10.125), dpi=100)
    fig.patch.set_facecolor('#0B1220')
    axes = axes.flatten()

    for idx, p_path in enumerate(preview_paths):
        img = Image.open(p_path)
        axes[idx].imshow(img)
        axes[idx].axis('off')
        axes[idx].set_title(f"Slide {idx+1}", color='#60A5FA', fontsize=11, fontweight='bold', pad=4)

    overview_path = os.path.join(DIR_PREVIEWS, "presentation_overview.png")
    plt.tight_layout()
    plt.savefig(overview_path, facecolor='#0B1220', edgecolor='none')
    plt.close()
    print(f"Composite overview created: {overview_path}")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE PRESENTATION README
# ─────────────────────────────────────────────────────────────────────────────
def write_presentation_readme():
    content = """# GlucoShield CDSS — Capstone Presentation Guide

**FUSE AI-201 Capstone | Module 6: Final Presentation Deliverable**  
**Project:** GlucoShield — Diabetes Hospital Readmission Risk Predictor  
**Team:** Group 04 | **Cohort:** Youth Empowerment and Employment in AI Program (YEEAP)  
**Presenter:** Bililign Yibgeta Amare (Team Lead)  
**Target Duration:** 9 Minutes 30 Seconds (Max 10:00)

---

## 1. Deliverables in This Directory

| File | Purpose |
| :--- | :--- |
| `GlucoShield_Capstone_Presentation.pptx` | **Master 9-slide PowerPoint presentation** in 16:9 widescreen format with embedded speaker notes on every slide. |
| `GlucoShield_Presentation_Script.docx` | **Complete verbatim speaking script**, slide-by-slide cues, timing allocation, live demonstration checklist, and evaluator Q&A defense cheat sheet. |
| `preview/slide_01_preview.png` ... `slide_09_preview.png` | **High-resolution image previews** of all nine slides for instant visual review without requiring Microsoft Office. |
| `preview/presentation_overview.png` | **Composite 3x3 contact sheet** displaying the full presentation narrative at a glance. |
| `README.md` | This technical guide and execution manual. |

---

## 2. Master Slide Timing & Cue Sheet

| Slide | Title | Target Time | Cumulative | Visual / Action |
| :---: | :--- | :---: | :---: | :--- |
| **1** | Title & Project Introduction | 0:30 | 0:30 | Executive cover card, Group 04 roster, system quick facts |
| **2** | Clinical Challenge & Motivation | 0:45 | 1:15 | Clinical burden, HRRP penalties, Problem-to-Solution flow |
| **3** | Dataset Hygiene & Preprocessing | 1:00 | 2:15 | 4-stage pipeline: 101k raw -> 69k clean -> 9 ICD-9 groups |
| **4** | Model Benchmarking & Selection | 1:00 | 3:15 | 5-model comparison table + Holdout ROC curves |
| **5** | Evaluation & Threshold Calibration | 1:00 | 4:15 | 5 KPI cards (65.71% recall) + Confusion Matrix (826 TP) |
| **6** | Live Prototype Demonstration | 2:30 | 6:45 | **Alt-Tab to Streamlit (`http://localhost:8501`)**: Scenarios 1, 2, 3 |
| **7** | TreeSHAP XAI & MLOps Drift | 1:00 | 7:45 | TreeSHAP bedside attribution + PSI drift chart (PSI=0.385) |
| **8** | Testing, Deployment & Governance | 1:00 | 8:45 | 17/17 pytest + 5/5 Stage 8 checks + Docker/FastAPI architecture |
| **9** | Retrospective, Roadmap & Wrap-Up | 0:45 | 9:30 | Learnings, limitations, future FHIR roadmap, thank you |

**Total Presentation Time:** Exactly 9 minutes 30 seconds (leaving 30 seconds buffer under the 10:00 cap).

---

## 3. Pre-Presentation Setup Checklist

### Step 1: Start the Streamlit Application
Open a terminal and start the clinical dashboard:
```powershell
cd D:\\Projects\\diabets_prediction
python -m streamlit run app.py --server.port 8501
```
Verify the app is active at `http://localhost:8501`.

### Step 2: Have the Automated Test Suite Ready
In a second terminal, verify that all 17 tests pass:
```powershell
python -m pytest tests/ -v
```
Keep this terminal minimized in case evaluators ask to see live automated test execution.

### Step 3: Open PowerPoint in Slide Show Mode
1. Open `GlucoShield_Capstone_Presentation.pptx`.
2. Press `F5` to begin the slide show (or `Alt + F5` for Presenter View with speaker notes).
3. Use the spacebar or right arrow key to advance.

### Step 4: Execute the Live Demo on Slide 6
1. When Slide 6 appears on screen, say your transition cue: *"Let us now examine our working clinical prototype running live in Streamlit."*
2. Press `Alt + Tab` to switch to your browser displaying `http://localhost:8501`.
3. Walk through:
   - **Scenario 1 (Low Risk):** Select from dropdown -> Click *Assess Readmission Risk* -> Show **27.1% score**, green badge, routine discharge checklist.
   - **Scenario 2 (High Risk):** Select from dropdown -> Click *Assess Readmission Risk* -> Show **72.7% score**, red badge, intensive 5-point transition bundle, and the TreeSHAP local attribution table.
   - **Scenario 3 (Borderline):** Select from dropdown -> Show **48.3% score**, explaining why it is POSITIVE (>= 0.45) but marked BORDERLINE (40–50%).
4. Press `Alt + Tab` to return to PowerPoint and advance to Slide 7.

---

## 4. Fallback Contingency Plan

If internet, browser, or server connection drops during the presentation:
- **Slide 6 contains complete scenario cards** with exact probabilities (27.1%, 72.7%, 48.3%), risk tiers, and discharge protocols.
- You can seamlessly present the three scenarios directly from Slide 6 without interrupting your presentation flow.
- Evaluation plots (`plots/roc_curve.png`, `plots/confusion_matrix.png`, `plots/monitoring_drift.png`) are pre-rendered and embedded in the deck.

---

## 5. Verified Metric Reference

All metrics in the presentation and script are verified against the repository source of truth:
- **Test ROC-AUC:** 0.6465 (Holdout test set, n=13,998)
- **PR-AUC:** 0.158
- **Recall @ 0.45 threshold:** 65.71% (Sensitivity)
- **Specificity @ 0.45:** 54.54%
- **Precision @ 0.45:** 12.48%
- **Confusion Matrix at 0.45:** TP: 826 | FN: 431 | TN: 6,949 | FP: 5,792
- **Simulated Drift PSI:** `number_inpatient` = 0.385 | `age` = 0.298 | `diag_1_group` = 0.260 (Threshold = 0.25)
- **Test Verification:** 17/17 pytest tests PASS | 5/5 Stage 8 system checks PASS
"""
    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Presentation README created: {PATH_README}")

# ── Main Execution ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Executing Capstone Presentation Artifact Generation...")
    build_powerpoint()
    build_docx_script()
    generate_slide_previews()
    write_presentation_readme()
    print("\nALL PRESENTATION ARTIFACTS GENERATED SUCCESSFULLY.")
