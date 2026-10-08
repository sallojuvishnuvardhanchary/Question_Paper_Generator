"""
Generate Professional 7-Slide Hackathon Pitch Deck for ExamGen AI.
CoreAlgorithm PROBLEM95 - Syllabus-Driven Exam Question Paper Generator
Outputs: ExamGen_AI_Hackathon_Presentation.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Color Palette (Dark Professional Technology / AI Theme)
COLOR_BG = RGBColor(10, 15, 29)          # Obsidian Slate #0A0F1D
COLOR_CARD = RGBColor(19, 28, 49)        # Dark Navy Card #131C31
COLOR_CARD_BORDER = RGBColor(35, 50, 83) # Card Border #233253
COLOR_CARD_ACCENT = RGBColor(26, 38, 66) # Lighter Card #1A2642

COLOR_PRIMARY = RGBColor(59, 130, 246)   # Electric Blue #3B82F6
COLOR_CYAN = RGBColor(6, 182, 212)       # Vibrant Cyan #06B6D4
COLOR_CYAN_LIGHT = RGBColor(56, 189, 248)# Sky Light #38BDF8
COLOR_EMERALD = RGBColor(16, 185, 129)   # Emerald Green #10B981
COLOR_AMBER = RGBColor(245, 158, 11)     # Amber Gold #F59E0B
COLOR_ROSE = RGBColor(239, 68, 68)       # Crimson Rose #EF4444

COLOR_TEXT_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT_SLATE = RGBColor(148, 163, 184) # #94A3B8
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B


def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG


def add_header(slide, category_text, title_text, lead_text=None):
    """Adds consistent header to a slide."""
    # Category Tracker Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.2), Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = COLOR_CARD_ACCENT
    pill.line.color.rgb = COLOR_CYAN
    pill.line.width = Pt(1)
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0
    p_p = tf_p.paragraphs[0]
    p_p.text = f"  {category_text.upper()}  "
    p_p.alignment = PP_ALIGN.CENTER
    p_p.font.name = "Segoe UI"
    p_p.font.size = Pt(10)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_CYAN_LIGHT

    # Main Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.6))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TEXT_WHITE

    # Subtitle / Lead line
    if lead_text:
        lead_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.4))
        tf_l = lead_box.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
        p_l = tf_l.paragraphs[0]
        p_l.text = lead_text
        p_l.font.name = "Segoe UI"
        p_l.font.size = Pt(12)
        p_l.font.color.rgb = COLOR_CYAN_LIGHT


def create_card(slide, left, top, width, height, border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD):
    """Creates a stylized tech card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


# ==============================================================================
# SLIDE 1: PROJECT INTRODUCTION
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1)

# Top Badges
badge1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(2.3), Inches(0.35))
badge1.fill.solid()
badge1.fill.fore_color.rgb = COLOR_CARD_ACCENT
badge1.line.color.rgb = COLOR_PRIMARY
badge1.line.width = Pt(1.2)
tf_b1 = badge1.text_frame
tf_b1.margin_left = tf_b1.margin_top = tf_b1.margin_right = tf_b1.margin_bottom = 0
p_b1 = tf_b1.paragraphs[0]
p_b1.text = "⚡ HACKATHON PITCH DECK"
p_b1.alignment = PP_ALIGN.CENTER
p_b1.font.name = "Segoe UI"
p_b1.font.size = Pt(10.5)
p_b1.font.bold = True
p_b1.font.color.rgb = COLOR_PRIMARY

badge2 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.25), Inches(0.6), Inches(3.5), Inches(0.35))
badge2.fill.solid()
badge2.fill.fore_color.rgb = COLOR_CARD_ACCENT
badge2.line.color.rgb = COLOR_CYAN
badge2.line.width = Pt(1.2)
tf_b2 = badge2.text_frame
tf_b2.margin_left = tf_b2.margin_top = tf_b2.margin_right = tf_b2.margin_bottom = 0
p_b2 = tf_b2.paragraphs[0]
p_b2.text = "CoreAlgorithm PROBLEM95 • DAA"
p_b2.alignment = PP_ALIGN.CENTER
p_b2.font.name = "Segoe UI"
p_b2.font.size = Pt(10.5)
p_b2.font.bold = True
p_b2.font.color.rgb = COLOR_CYAN_LIGHT

# Main Big Project Title
t_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(1.1))
tf = t_box.text_frame
tf.word_wrap = True
p1 = tf.paragraphs[0]
p1.text = "EXAMGEN AI"
p1.font.name = "Segoe UI"
p1.font.size = Pt(50)
p1.font.bold = True
p1.font.color.rgb = COLOR_TEXT_WHITE

sub_box = slide1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(0.55))
tf_sub = sub_box.text_frame
tf_sub.word_wrap = True
p_sub = tf_sub.paragraphs[0]
p_sub.text = "Syllabus-Driven Intelligent Question Paper Generator"
p_sub.font.name = "Segoe UI"
p_sub.font.size = Pt(20)
p_sub.font.bold = True
p_sub.font.color.rgb = COLOR_CYAN_LIGHT

tag_box = slide1.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(0.45))
tf_tag = tag_box.text_frame
p_tag = tf_tag.paragraphs[0]
p_tag.text = '“Transform a syllabus into a structured, optimized and professionally formatted examination paper.”'
p_tag.font.name = "Segoe UI"
p_tag.font.size = Pt(13)
p_tag.font.italic = True
p_tag.font.color.rgb = COLOR_TEXT_SLATE

# Hero Transformation Visual (3 Connected Cards)
hero_top = Inches(3.45)
hero_h = Inches(1.8)

# Card 1: Syllabus Copy
c1 = create_card(slide1, Inches(0.8), hero_top, Inches(3.3), hero_h, COLOR_CYAN)
tf1 = c1.text_frame
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = Inches(0.2)
p = tf1.paragraphs[0]
p.text = "📄 UPLOAD SYLLABUS COPY"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

p = tf1.add_paragraph()
p.text = "• Ingests raw PDF, DOCX, or TXT\n• NLP extraction of Units & Topics\n• Automatic Roman/Arabic numeral parsing\n• No static question bank dependency"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Arrow 1
arr1 = slide1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.25), hero_top + Inches(0.65), Inches(0.7), Inches(0.45))
arr1.fill.solid()
arr1.fill.fore_color.rgb = COLOR_PRIMARY
arr1.line.fill.background()

# Card 2: ExamGen AI Engine
c2 = create_card(slide1, Inches(5.1), hero_top, Inches(3.4), hero_h, COLOR_PRIMARY)
tf2 = c2.text_frame
tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = Inches(0.2)
p = tf2.paragraphs[0]
p.text = "⚙️ EXAMGEN AI CORE"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY

p = tf2.add_paragraph()
p.text = "• Dynamic Structure & Section Builder\n• Greedy Multi-Criteria Optimization\n• Backtracking + Branch & Bound Pruning\n• Bloom's Taxonomy Cognitive Balance"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Arrow 2
arr2 = slide1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.65), hero_top + Inches(0.65), Inches(0.7), Inches(0.45))
arr2.fill.solid()
arr2.fill.fore_color.rgb = COLOR_EMERALD
arr2.line.fill.background()

# Card 3: Autonomous Question Paper
c3 = create_card(slide1, Inches(9.5), hero_top, Inches(3.0), hero_h, COLOR_EMERALD)
tf3 = c3.text_frame
tf3.margin_left = tf3.margin_top = tf3.margin_right = tf3.margin_bottom = Inches(0.2)
p = tf3.paragraphs[0]
p.text = "🎓 QUESTION PAPER & KEY"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf3.add_paragraph()
p.text = "• Publication-Grade ReportLab A4 PDF\n• Institutional Branding & College Logo\n• Continuous Numbering & (a)/(b) Choice\n• Verified Solution Key & Rationale"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Bottom Info Strip (Domain & Team)
meta_card = create_card(slide1, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.3), COLOR_CARD_BORDER, COLOR_CARD_ACCENT)
tf_m = meta_card.text_frame
tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = Inches(0.2)

p_m1 = tf_m.paragraphs[0]
p_m1.text = "PROJECT DOMAIN: AI / EdTech / Design & Analysis of Algorithms (DAA) / Automated Academic Assessment"
p_m1.font.name = "Segoe UI"
p_m1.font.size = Pt(11)
p_m1.font.bold = True
p_m1.font.color.rgb = COLOR_TEXT_WHITE

p_m2 = tf_m.add_paragraph()
p_m2.text = "CORE ALGORITHMS: Multi-Attribute Greedy Heuristic • Backtracking with Branch-and-Bound • Comparative Sorters"
p_m2.font.name = "Segoe UI"
p_m2.font.size = Pt(10.5)
p_m2.font.color.rgb = COLOR_CYAN_LIGHT

p_m3 = tf_m.add_paragraph()
p_m3.text = "TEAM MEMBERS: Member 1  |  Member 2  |  Member 3  |  Member 4  •  Hackathon Team"
p_m3.font.name = "Segoe UI"
p_m3.font.size = Pt(10)
p_m3.font.color.rgb = COLOR_TEXT_SLATE


# ==============================================================================
# SLIDE 2: THE CHALLENGE
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2)
add_header(
    slide2,
    "Problem Statement & Academic Friction",
    "THE CHALLENGE",
    "“Creating a balanced examination paper manually is time-consuming and involves multiple complex constraints.”"
)

# Left Column: The Traditional Manual Workflow
w_card = create_card(slide2, Inches(0.8), Inches(1.85), Inches(5.6), Inches(5.0))
tf_w = w_card.text_frame
tf_w.margin_left = tf_w.margin_top = tf_w.margin_right = tf_w.margin_bottom = Inches(0.25)

p = tf_w.paragraphs[0]
p.text = "TRADITIONAL MANUAL WORKFLOW"
p.font.name = "Segoe UI"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf_w.add_paragraph()
p.text = "Syllabus Copy\n  ↓\nRead Curriculum Topics\n  ↓\nManually Select / Draft Questions\n  ↓\nAttempt to Balance Cognitive Difficulty\n  ↓\nManually Calculate Marks & Options Arithmetic\n  ↓\nAudit Unit & Topic Coverage Spread\n  ↓\nFormat Word Document & Align Spacing\n  ↓\nExport Final PDF Document"
p.font.name = "Segoe UI"
p.font.size = Pt(11)
p.font.color.rgb = COLOR_TEXT_SLATE

# Bottom Alert Box in Left Column
alert_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.05), Inches(5.8), Inches(5.1), Inches(0.85))
alert_box.fill.solid()
alert_box.fill.fore_color.rgb = RGBColor(38, 20, 30)
alert_box.line.color.rgb = COLOR_ROSE
alert_box.line.width = Pt(1)
tf_a = alert_box.text_frame
tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = Inches(0.1)
p_a = tf_a.paragraphs[0]
p_a.text = "MANUAL PROCESS LIMITATION:"
p_a.font.name = "Segoe UI"
p_a.font.size = Pt(10)
p_a.font.bold = True
p_a.font.color.rgb = COLOR_ROSE
p_a2 = tf_a.add_paragraph()
p_a2.text = "High Effort → Multiple Subjective Decisions → High Configuration Risk"
p_a2.font.name = "Segoe UI"
p_a2.font.size = Pt(9.5)
p_a2.font.color.rgb = COLOR_TEXT_WHITE

# Right Column: 4 Pain Points (Stacked Cards)
right_left = Inches(6.65)
card_w = Inches(5.85)

challenges = [
    ("1. Cognitive Difficulty Imbalance", "Questions tend to skew heavily toward easy rote recall rather than balanced Bloom's Taxonomy tiers (Easy, Medium, Hard).", COLOR_AMBER),
    ("2. Uneven Coverage & Repetition Risk", "High probability of over-sampling specific units while leaving other topics completely unassessed; risk of repeating identical concepts.", COLOR_ROSE),
    ("3. Multi-Tier Arithmetic Constraints", "Severe difficulty coordinating Questions Displayed (N_disp) vs Questions to Answer (N_attempt) across sections with internal choices.", COLOR_CYAN),
    ("4. Layout & Typesetting Overhead", "Manual formatting in Word processors results in broken margins, mismatched marks totals, and missing or desynchronized answer keys.", COLOR_PRIMARY)
]

for idx, (title, desc, color) in enumerate(challenges):
    top_pos = Inches(1.85) + idx * Inches(1.25)
    c = create_card(slide2, right_left, top_pos, card_w, Inches(1.15), color)
    tf_c = c.text_frame
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = Inches(0.18)
    p = tf_c.paragraphs[0]
    p.text = title
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = color
    p = tf_c.add_paragraph()
    p.text = desc
    p.font.name = "Segoe UI"
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_SLATE


# ==============================================================================
# SLIDE 3: OUR INNOVATION
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3)
add_header(
    slide3,
    "Algorithmic Paradigm Shift",
    "OUR INNOVATION",
    "“ExamGen AI treats question-paper generation as a constrained algorithmic optimization problem.”"
)

# 4 Major Innovation Cards (2x2 Grid)
grid_w = Inches(5.7)
grid_h = Inches(1.95)
top_row = Inches(1.85)
bot_row = Inches(3.95)
col1_l = Inches(0.8)
col2_l = Inches(6.8)

# Innovation 1
i1 = create_card(slide3, col1_l, top_row, grid_w, grid_h, COLOR_CYAN)
tf = i1.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.2)
p = tf.paragraphs[0]
p.text = "1. SYLLABUS-DRIVEN PIPELINE"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT
p = tf.add_paragraph()
p.text = "• Directly ingests PDF, DOCX, or TXT syllabus copies\n• Regex & NLP unit/topic segmentation (Roman & Arabic numerals)\n• Generates contextual candidate questions aligned to curriculum\n• Completely replaces static, hard-coded question banks"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Innovation 2
i2 = create_card(slide3, col2_l, top_row, grid_w, grid_h, COLOR_PRIMARY)
tf = i2.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.2)
p = tf.paragraphs[0]
p.text = "2. DYNAMIC PAPER STRUCTURE BUILDER"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p = tf.add_paragraph()
p.text = "• Client defines custom Parts, Sections, and Question Types\n• Client manually enters Marks/Question (1, 2, 5, 10, 16M)\n• Strict section math: Section Marks = N_attempt × Marks/Q\n• Symmetric (a)/(b) internal choice toggles with continuous numbering"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Innovation 3
i3 = create_card(slide3, col1_l, bot_row, grid_w, grid_h, COLOR_EMERALD)
tf = i3.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.2)
p = tf.paragraphs[0]
p.text = "3. DAA-BASED OPTIMIZATION ENGINE"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD
p = tf.add_paragraph()
p.text = "• Multi-Attribute Greedy Heuristic for ultra-fast candidate scoring\n• Backtracking + Branch & Bound Pruning for guaranteed constraints\n• Real-time visualizer trace: candidate scores & state-space pruning\n• Comparative sorting algorithms (Quick, Merge, Heap, Insertion)"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Innovation 4
i4 = create_card(slide3, col2_l, bot_row, grid_w, grid_h, COLOR_AMBER)
tf = i4.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.2)
p = tf.paragraphs[0]
p.text = "4. AUTOMATED PDF GENERATION"
p.font.name = "Segoe UI"
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER
p = tf.add_paragraph()
p.text = "• Server-side ReportLab 4.x vector rendering on standard A4\n• Dynamic institutional header & custom college logo integration\n• Automatic two-pass 'Page X of Y' NumberedCanvas\n• Synchronized official Answer Key & Solution Matrix PDF"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.color.rgb = COLOR_TEXT_SLATE

# Bottom Pipeline Highlight Strip
pipe_card = create_card(slide3, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.85), COLOR_CARD_BORDER, COLOR_CARD_ACCENT)
tf_p = pipe_card.text_frame
tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = Inches(0.12)
p = tf_p.paragraphs[0]
p.text = "THE CORE ARCHITECTURAL PIPELINE:"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

p = tf_p.add_paragraph()
p.text = "Candidate Question Pool  →  Constraint Analysis  →  DAA Optimization (Greedy / Backtracking)  →  Validated Paper  →  Printable PDF"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT_WHITE


# ==============================================================================
# SLIDE 4: HOW IT WORKS
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
set_slide_background(slide4)
add_header(
    slide4,
    "End-to-End Execution Pipeline",
    "HOW IT WORKS",
    "“A structured 7-stage synthesis pipeline ensuring pedagogical balance, mathematical rigor, and instant publication.”"
)

# 7-Step Workflow Chain (Horizontal Cards)
steps = [
    ("1. UPLOAD", "Syllabus PDF / DOCX / TXT copy ingested", COLOR_CYAN),
    ("2. EXTRACT", "NLP segments units & topic keywords", COLOR_CYAN_LIGHT),
    ("3. CONFIGURE", "Parts, sections, N_disp, N_attempt, Marks", COLOR_PRIMARY),
    ("4. GENERATE", "Bloom's taxonomy candidate pool", COLOR_PRIMARY),
    ("5. OPTIMIZE", "Greedy or Backtracking + B&B search", COLOR_EMERALD),
    ("6. VALIDATE", "Audit marks, units & difficulty quotas", COLOR_AMBER),
    ("7. OUTPUT", "Publication ReportLab PDF + Answer Key", COLOR_TEXT_WHITE)
]

step_w = Inches(1.58)
step_gap = Inches(0.11)
step_top = Inches(1.9)
step_h = Inches(3.2)

for i, (title, desc, color) in enumerate(steps):
    x_pos = Inches(0.8) + i * (step_w + step_gap)
    card = create_card(slide4, x_pos, step_top, step_w, step_h, color)
    tf = card.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.12)
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = color
    
    p_step = tf.add_paragraph()
    p_step.text = f"STAGE {i+1}"
    p_step.font.name = "Segoe UI"
    p_step.font.size = Pt(9)
    p_step.font.bold = True
    p_step.font.color.rgb = COLOR_TEXT_MUTED
    
    p_desc = tf.add_paragraph()
    p_desc.text = f"\n{desc}"
    p_desc.font.name = "Segoe UI"
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = COLOR_TEXT_SLATE

# Bottom User Journey Card
journey_card = create_card(slide4, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.6), COLOR_PRIMARY, COLOR_CARD_ACCENT)
tf_j = journey_card.text_frame
tf_j.margin_left = tf_j.margin_top = tf_j.margin_right = tf_j.margin_bottom = Inches(0.18)

p = tf_j.paragraphs[0]
p.text = "USER JOURNEY & INTERACTION FLOW:"
p.font.name = "Segoe UI"
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

p = tf_j.add_paragraph()
p.text = "Client Faculty  →  Uploads Course Syllabus  →  Configures Paper Blueprint & Quotas  →  Triggers DAA Optimization  →  Inspects Live Trace & Preview  →  Downloads Official PDF"
p.font.name = "Segoe UI"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT_WHITE

p = tf_j.add_paragraph()
p.text = "• Zero manual typesetting • Immediate visual confirmation of constraint fulfillment • Complete administrative audit trail"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE


# ==============================================================================
# SLIDE 5: TECHNOLOGY & ALGORITHM
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
set_slide_background(slide5)
add_header(
    slide5,
    "Computer Science & Engineering Foundations",
    "TECHNOLOGY & ALGORITHMS",
    "“Built on verified full-stack architecture, rigorous DAA algorithmic implementations, and mathematical bounds.”"
)

# Left Column: Production Tech Stack
tech_card = create_card(slide5, Inches(0.8), Inches(1.85), Inches(5.5), Inches(5.0))
tf_tech = tech_card.text_frame
tf_tech.margin_left = tf_tech.margin_top = tf_tech.margin_right = tf_tech.margin_bottom = Inches(0.25)

p = tf_tech.paragraphs[0]
p.text = "PRODUCTION TECH STACK"
p.font.name = "Segoe UI"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

tech_items = [
    ("Python 3.10+ & Flask 3.0", "Clean REST API routing, modular blueprint architecture, production-ready server execution via Gunicorn."),
    ("SQLite3 with WAL Mode", "Write-Ahead Logging for high concurrency, zero data corruption, and automatic schema migration."),
    ("Document Extraction (pypdf, docx)", "Robust regex & AST document parsing for PDF and Word DOCX curriculum documents."),
    ("ReportLab 4.x PDF Engine", "Server-side Flowable canvas engine for precise vector typography, tables, headers, and pagination."),
    ("Frontend (HTML5, CSS3, ES6+ JS)", "Zero heavy JS frameworks. Ultra-fast native DOM manipulation, dark slate theme, and Chart.js 4.4."),
    ("Pytest Testing Suite", "Comprehensive automated unit and integration tests covering algorithms, APIs, and PDF generation.")
]

for title, desc in tech_items:
    p = tf_tech.add_paragraph()
    p.text = f"• {title}: "
    p.font.name = "Segoe UI"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_WHITE
    p.text += desc
    p.font.bold = False
    p.font.color.rgb = COLOR_TEXT_SLATE

# Right Column: DAA Algorithms (3 Cards)
right_l = Inches(6.55)
right_w = Inches(5.95)

# DAA 1: Greedy
d1 = create_card(slide5, right_l, Inches(1.85), right_w, Inches(1.5), COLOR_PRIMARY)
tf = d1.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "1. GREEDY ALGORITHM  •  Complexity: O(K · N)"
p.font.name = "Segoe UI"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p = tf.add_paragraph()
p.text = "• Multi-Criteria Heuristic Function: Score(q) = Wm·MarksFit + Wd·DiffFit + Wu·UnitDeficit + Wn·Novelty\n• Selects locally optimal question at each section slot to satisfy deficits\n• Fast, deterministic paper synthesis in sub-50ms"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# DAA 2: Backtracking
d2 = create_card(slide5, right_l, Inches(3.45), right_w, Inches(1.6), COLOR_EMERALD)
tf = d2.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "2. BACKTRACKING + BRANCH & BOUND  •  Worst: O(2^N), Pruned: O(N·K)"
p.font.name = "Segoe UI"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD
p = tf.add_paragraph()
p.text = "• Explores state-space search tree with mathematical bounding checks\n• Upper/Lower Marks Feasibility Pruning: C_marks + Remaining_Max < Target\n• Quota Violation Pruning: Prunes branches exceeding maximum unit/diff caps\n• Reverts state upon detecting infeasible paths to guarantee valid solution"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# DAA 3: Sorters
d3 = create_card(slide5, right_l, Inches(5.15), right_w, Inches(1.7), COLOR_AMBER)
tf = d3.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "3. SORTING ALGORITHMS  •  O(N log N) / O(N²)"
p.font.name = "Segoe UI"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER
p = tf.add_paragraph()
p.text = "• Verified Implementations: Quick Sort, Merge Sort, Insertion Sort, Bubble Sort, Selection Sort\n• Candidate prioritization by Marks, Difficulty, Unit, Topic relevance, and Novelty\n• Full trace event streaming for live step-by-step sorting visualization in Algorithm Lab"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE


# ==============================================================================
# SLIDE 6: DEMO & IMPACT
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
set_slide_background(slide6)
add_header(
    slide6,
    "Empirical Verification & Practical Implementation",
    "DEMO & IMPACT",
    "“A fully functional, algorithm-centric academic prototype with 100% verified test coverage and production capabilities.”"
)

# 4 UI Architecture Cards
card_w = Inches(5.7)
card_h = Inches(1.85)
top_pos1 = Inches(1.85)
top_pos2 = Inches(3.85)

# UI 1: Syllabus Parser
u1 = create_card(slide6, Inches(0.8), top_pos1, card_w, card_h, COLOR_CYAN)
tf = u1.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "🖥️ SYLLABUS MANAGER & TOPIC EXPLORER"
p.font.name = "Segoe UI"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT
p = tf.add_paragraph()
p.text = "• Drag-and-drop syllabus upload interface (PDF/Word/Text)\n• Live curriculum editor displaying extracted Units and Topic tags\n• Real-time candidate question synthesis categorized by Bloom's Taxonomy\n• Instant search and syllabus switching across academic subjects"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# UI 2: Dynamic Structure Builder
u2 = create_card(slide6, Inches(6.8), top_pos1, card_w, card_h, COLOR_PRIMARY)
tf = u2.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "🛠️ DYNAMIC EXAMINATION STRUCTURE BUILDER"
p.font.name = "Segoe UI"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p = tf.add_paragraph()
p.text = "• Configure custom Parts, Sections, and manual Marks/Question\n• Strict Section Math: Section Marks = N_attempt × Marks/Q\n• Continuous question numbering across parts (e.g. Q1-Q10, Q11-Q15)\n• Institutional branding module with live college logo preview & upload"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# UI 3: DAA Algorithm Lab
u3 = create_card(slide6, Inches(0.8), top_pos2, card_w, card_h, COLOR_EMERALD)
tf = u3.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "📊 DAA ALGORITHM VISUALIZER & TRACE LAB"
p.font.name = "Segoe UI"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD
p = tf.add_paragraph()
p.text = "• Real-time DAA execution visualization powered by actual backend trace events\n• Step-by-step playback with speed controls (0.5x, 1x, 2x)\n• Interactive State-Space Search Tree diagram showing Branch-and-Bound pruning\n• Live candidate score decomposition and comparative sorting benchmarks"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# UI 4: ReportLab PDF Engine
u4 = create_card(slide6, Inches(6.8), top_pos2, card_w, card_h, COLOR_AMBER)
tf = u4.text_frame
tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.18)
p = tf.paragraphs[0]
p.text = "📑 PUBLICATION-GRADE REPORTLAB PDF GENERATOR"
p.font.name = "Segoe UI"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER
p = tf.add_paragraph()
p.text = "• Academic A4 printable PDF with embedded institution logo & course metadata\n• Professional internal choice layout: symmetric Q11. (a) OR (b) formatting\n• Two-pass dynamic 'Page X of Y' NumberedCanvas with confidential watermark\n• Synchronized official Answer Key & Solution Matrix PDF document"
p.font.name = "Segoe UI"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_TEXT_SLATE

# Bottom Verified Results Panel
res_card = create_card(slide6, Inches(0.8), Inches(5.85), Inches(11.7), Inches(1.15), COLOR_CARD_BORDER, COLOR_CARD_ACCENT)
tf_r = res_card.text_frame
tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = Inches(0.15)

p = tf_r.paragraphs[0]
p.text = "VERIFIED PROJECT RESULTS & IMPACT METRICS:"
p.font.name = "Segoe UI"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

metrics_text = (
    "✓ 41 Automated Tests Passing (100% Pytest pass rate across algorithms, API, and PDF generator)  |  "
    "✓ 3 Academic Paper Formats  |  "
    "✓ Zero Question Bank Lock-in (100% Syllabus-Driven)  |  "
    "✓ Strict Section Arithmetic Enforced  |  "
    "✓ Complete Paper Generated in <150ms"
)
p_m = tf_r.add_paragraph()
p_m.text = metrics_text
p_m.font.name = "Segoe UI"
p_m.font.size = Pt(10)
p_m.font.bold = True
p_m.font.color.rgb = COLOR_TEXT_WHITE


# ==============================================================================
# SLIDE 7: FUTURE VISION & CONCLUSION
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
set_slide_background(slide7)
add_header(
    slide7,
    "Strategic Roadmap & Summary",
    "FUTURE VISION & CONCLUSION",
    "“Advancing from syllabus-driven synthesis to an autonomous institutional assessment infrastructure.”"
)

# Left Column: Current Achievements
left_card = create_card(slide7, Inches(0.8), Inches(1.85), Inches(5.6), Inches(3.65), COLOR_EMERALD)
tf_ach = left_card.text_frame
tf_ach.margin_left = tf_ach.margin_top = tf_ach.margin_right = tf_ach.margin_bottom = Inches(0.2)

p = tf_ach.paragraphs[0]
p.text = "CURRENT ACHIEVEMENTS (VERIFIED)"
p.font.name = "Segoe UI"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

achievements = [
    "✓ Syllabus-Driven Workflow: End-to-end ingestion of PDF/DOCX/TXT syllabi.",
    "✓ Dynamic Paper Structure: Customizable Parts, Sections, Questions, and Marks.",
    "✓ Real DAA Optimization: Multi-criteria Greedy and Backtracking with B&B.",
    "✓ Pedagogical Quota Balancing: Strict unit spread and Bloom's difficulty quotas.",
    "✓ Real-Time Visualization: Live trace events, scoring logs, and state-space tree.",
    "✓ Publication PDF Engine: Watermarked A4 exam papers and verified solution keys."
]
for a in achievements:
    p = tf_ach.add_paragraph()
    p.text = a
    p.font.name = "Segoe UI"
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_SLATE

# Right Column: Future Roadmap
right_card = create_card(slide7, Inches(6.8), Inches(1.85), Inches(5.7), Inches(3.65), COLOR_PRIMARY)
tf_fut = right_card.text_frame
tf_fut.margin_left = tf_fut.margin_top = tf_fut.margin_right = tf_fut.margin_bottom = Inches(0.2)

p = tf_fut.paragraphs[0]
p.text = "FUTURE ROADMAP & EXPANSIONS"
p.font.name = "Segoe UI"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY

future_items = [
    "→ LLM Fine-Tuning Integration: Specialized mathematical LaTeX and code-generation.",
    "→ Vector Semantic Deduplication: Cosine distance embedding checks against repetition.",
    "→ Multi-Tenant Institutional Cloud: Role-based access for Deans, HODs, and Faculty.",
    "→ LMS & QTI Standards Export: 1-click import into Canvas, Moodle, and Blackboard.",
    "→ Automated Difficulty Calibration: Historical student performance telemetry feedback.",
    "→ Mobile Application: Companion app for syllabus review and instant paper previews."
]
for f in future_items:
    p = tf_fut.add_paragraph()
    p.text = f
    p.font.name = "Segoe UI"
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_SLATE

# Bottom Hero Takeaway Card
takeaway_card = create_card(slide7, Inches(0.8), Inches(5.65), Inches(11.7), Inches(1.4), COLOR_CYAN, COLOR_CARD_ACCENT)
tf_t = takeaway_card.text_frame
tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = Inches(0.2)

p = tf_t.paragraphs[0]
p.text = "FINAL TAKEAWAY"
p.font.name = "Segoe UI"
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_LIGHT

p_quote = tf_t.add_paragraph()
p_quote.text = "“From syllabus to optimized examination paper — automated, configurable, and algorithm-driven.”"
p_quote.font.name = "Segoe UI"
p_quote.font.size = Pt(13.5)
p_quote.font.bold = True
p_quote.font.color.rgb = COLOR_TEXT_WHITE

p_ty = tf_t.add_paragraph()
p_ty.text = "THANK YOU!  •  Questions & Answers  •  CoreAlgorithm PROBLEM95"
p_ty.font.name = "Segoe UI"
p_ty.font.size = Pt(11)
p_ty.font.bold = True
p_ty.font.color.rgb = COLOR_EMERALD

# Save Presentation
output_filename = "ExamGen_AI_Hackathon_Presentation.pptx"
prs.save(output_filename)
print(f"Presentation successfully created and saved as: {output_filename}")
print(f"Total slides generated: {len(prs.slides)}")
