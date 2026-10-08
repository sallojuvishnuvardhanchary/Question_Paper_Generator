"""
Professional Examination PDF Generator using ReportLab.
Produces print-ready, university-grade examination question papers and answer keys on A4 paper.
"""

import os
import json
from typing import Dict, List, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from config import Config

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that performs two-pass page numbering ('Page X of Y')."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#475569"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 0.6 * inch, 0.4 * inch, page_text)
        self.drawString(0.6 * inch, 0.4 * inch, "Confidential — Examination Document")
        self.restoreState()

def generate_exam_pdf(
    paper_data: Dict[str, Any],
    institution_data: Optional[Dict[str, Any]] = None,
    output_filename: Optional[str] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    Generates a formal, printable academic question paper PDF.
    Returns the absolute path to the generated PDF file.
    Supports client logos, custom institutional headers, section instructions,
    and continuous question numbering.
    """
    folder = output_dir or Config.GENERATED_PAPERS_FOLDER
    os.makedirs(folder, exist_ok=True)
    paper_id = paper_data.get('id', 'temp')
    filename = output_filename or f"Question_Paper_{paper_id}.pdf"
    file_path = os.path.join(folder, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    # Custom formal styles
    inst_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.black,
        spaceAfter=2
    )

    addr_style = ParagraphStyle(
        'InstAddr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceAfter=2
    )

    dept_style = ParagraphStyle(
        'DeptTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )

    exam_style = ParagraphStyle(
        'ExamTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.black,
        spaceAfter=6
    )

    part_header_style = ParagraphStyle(
        'PartHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=4
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=0, # Left
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=2
    )

    q_text_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.black
    )

    or_style = ParagraphStyle(
        'OrSeparator',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceBefore=4,
        spaceAfter=4
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black
    )

    elements = []

    # 1. INSTITUTION & EXAM HEADER
    inst = institution_data or {}
    inst_name = (inst.get('institution_name') or 'ABC INSTITUTE OF TECHNOLOGY').upper()
    inst_addr = (inst.get('institution_address') or 'AUTONOMOUS EXAMINATIONS BRANCH, HYDERABAD').upper()
    branch_name = inst.get('branch') or inst.get('department') or 'COMPUTER SCIENCE AND ENGINEERING'
    exam_name = (inst.get('exam_name') or paper_data.get('paper_name') or 'B.TECH III YEAR II SEMESTER REGULAR EXAMINATIONS').upper()
    subject = paper_data.get('subject') or inst.get('subject') or 'Design and Analysis of Algorithms'
    subj_code = inst.get('subject_code', 'CS601PC')
    course_code = inst.get('course_code', 'R20-CSE')
    semester = inst.get('semester', 'III Year II Semester')
    academic_year = inst.get('academic_year', '2026-2027')
    exam_date = inst.get('exam_date') or inst.get('date', '15-11-2026')
    duration = inst.get('duration', '3 Hours')
    max_marks = paper_data.get('total_marks', 100)
    instructions = inst.get('instructions', '1. Answer all questions in Part A.\n2. In Part B, answer either (a) or (b) from each question.\n3. Assume suitable missing data if necessary.')

    # Check for logo image
    logo_path = inst.get('logo_path') or paper_data.get('logo_path')
    logo_element = None
    if logo_path:
        actual_logo_path = logo_path
        if not os.path.isabs(actual_logo_path):
            actual_logo_path = os.path.join(Config.BASE_DIR, actual_logo_path)
        if os.path.exists(actual_logo_path):
            try:
                logo_element = Image(actual_logo_path, width=1.1 * inch, height=0.9 * inch, kind='proportional')
            except Exception as img_err:
                print(f"Note: Could not load logo image {actual_logo_path}: {img_err}")
                logo_element = None

    if logo_element:
        # 2-column header: Logo on Left, Academic Text on Right
        text_flowables = [
            Paragraph(inst_name, inst_style),
            Paragraph(inst_addr, addr_style),
            Paragraph(f"DEPARTMENT OF {branch_name.upper()}", dept_style),
            Paragraph(exam_name, exam_style)
        ]
        header_table = Table([[logo_element, text_flowables]], colWidths=[1.3 * inch, 5.9 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
    else:
        elements.append(Paragraph(inst_name, inst_style))
        if inst_addr:
            elements.append(Paragraph(inst_addr, addr_style))
        elements.append(Paragraph(f"DEPARTMENT OF {branch_name.upper()}", dept_style))
        elements.append(Paragraph(exam_name, exam_style))

    # Info Grid Table
    info_data = [
        [
            Paragraph(f"<b>Branch / Dept:</b> {branch_name}", meta_label_style),
            Paragraph(f"<b>Course Code:</b> {course_code}", meta_val_style),
            Paragraph(f"<b>Subject Code:</b> {subj_code}", meta_label_style)
        ],
        [
            Paragraph(f"<b>Subject:</b> {subject}", meta_label_style),
            Paragraph(f"<b>Date of Exam:</b> {exam_date}", meta_val_style),
            Paragraph(f"<b>Max Marks:</b> {max_marks} Marks", meta_label_style)
        ],
        [
            Paragraph(f"<b>Semester / Year:</b> {semester}", meta_label_style),
            Paragraph(f"<b>Academic Year:</b> {academic_year}", meta_val_style),
            Paragraph(f"<b>Time / Duration:</b> {duration}", meta_label_style)
        ]
    ]

    info_table = Table(info_data, colWidths=[3.0 * inch, 2.3 * inch, 1.9 * inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6))

    # Instructions box
    inst_lines = [f"• {line.strip()}" for line in instructions.split('\n') if line.strip()]
    inst_paras = [Paragraph(f"<b>General Instructions:</b>", meta_label_style)] + [
        Paragraph(line, ParagraphStyle('InstItem', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor("#334155")))
        for line in inst_lines
    ]
    inst_table = Table([[inst_paras]], colWidths=[7.2 * inch])
    inst_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#64748b")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(inst_table)
    elements.append(Spacer(1, 8))

    # 2. QUESTIONS (GROUPED BY PART & SECTION)
    questions = paper_data.get('questions', paper_data.get('selected_questions', []))
    
    # Organize by part
    parts_map = {}
    for q in questions:
        p_name = q.get('part_name') or 'PART A'
        s_name = q.get('section_name') or ''
        parts_map.setdefault(p_name, {}).setdefault(s_name, []).append(q)

    # Render each part
    for part_idx, (p_name, sections) in enumerate(parts_map.items()):
        # Calculate part total
        p_marks = sum(q.get('marks', 0) for sec in sections.values() for q in sec if not q.get('is_choice'))
        
        elements.append(Paragraph(f"<b>{p_name.upper()}</b>", part_header_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=8))

        for s_name, sec_questions in sections.items():
            first_q = sec_questions[0] if sec_questions else {}
            q_disp = len([q for q in sec_questions if not q.get('is_choice')])
            q_attempt = int(first_q.get('questions_to_answer') or q_disp)
            m_per_q = int(first_q.get('marks', 2))
            sec_marks = int(first_q.get('section_marks') or (q_attempt * m_per_q))
            sec_instr = first_q.get('section_instructions')
            if not sec_instr:
                if q_attempt < q_disp:
                    sec_instr = f"Answer any {q_attempt} question{'s' if q_attempt > 1 else ''} out of {q_disp}."
                else:
                    sec_instr = f"Answer all {q_disp} questions."

            sec_title_text = f"<b>{s_name.upper()}</b>" if s_name else "<b>SECTION</b>"
            elements.append(Paragraph(sec_title_text, section_header_style))

            # Section Instruction Badge
            sec_badge_text = (
                f"<b>Instructions:</b> {sec_instr} &nbsp;&nbsp;&nbsp;&nbsp; "
                f"<b>[ {q_disp} Questions &times; {m_per_q}M &nbsp;|&nbsp; "
                f"Attempt any {q_attempt} &nbsp;|&nbsp; Max Marks: {sec_marks} ]</b>"
            )
            elements.append(Paragraph(
                sec_badge_text,
                ParagraphStyle('SecBadge', parent=styles['Normal'], fontSize=8.5, leading=11.5, textColor=colors.HexColor("#1e293b"), spaceAfter=5)
            ))

            # Group choices if present
            # If questions share a choice_group, display them as Q (a) OR Q (b)
            rendered_choice_groups = set()
            
            for q in sec_questions:
                c_group = q.get('choice_group')
                if c_group:
                    if c_group in rendered_choice_groups:
                        continue
                    rendered_choice_groups.add(c_group)
                    
                    # Find all alternatives in this choice group
                    alternatives = [alt for alt in sec_questions if alt.get('choice_group') == c_group]
                    
                    q_num = q.get('question_number', '1')
                    
                    # Render Choice (a)
                    alt_a = alternatives[0]
                    alt_b = alternatives[1] if len(alternatives) > 1 else None
                    
                    q_row_a = [
                        Paragraph(f"<b>{q_num}. (a)</b>", ParagraphStyle('QNum', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13)),
                        Paragraph(alt_a.get('question_text', ''), q_text_style),
                        Paragraph(f"<b>[{alt_a.get('marks', 10)} Marks]</b>", ParagraphStyle('QMarks', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=2))
                    ]
                    t_a = Table([q_row_a], colWidths=[0.6 * inch, 5.6 * inch, 1.0 * inch])
                    t_a.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ]))
                    
                    # Render OR separator
                    or_table = Table([[Paragraph("<b>[ OR ]</b>", or_style)]], colWidths=[7.2 * inch])
                    
                    # Render Choice (b)
                    if alt_b:
                        q_row_b = [
                            Paragraph(f"<b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(b)</b>", ParagraphStyle('QNum', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13)),
                            Paragraph(alt_b.get('question_text', ''), q_text_style),
                            Paragraph(f"<b>[{alt_b.get('marks', 10)} Marks]</b>", ParagraphStyle('QMarks', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=2))
                        ]
                        t_b = Table([q_row_b], colWidths=[0.6 * inch, 5.6 * inch, 1.0 * inch])
                        t_b.setStyle(TableStyle([
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        elements.append(KeepTogether([t_a, or_table, t_b, Spacer(1, 8)]))
                    else:
                        elements.append(t_a)
                else:
                    # Single standalone question
                    q_num = q.get('question_number', '1')
                    q_row = [
                        Paragraph(f"<b>{q_num}.</b>", ParagraphStyle('QNum', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13)),
                        Paragraph(q.get('question_text', ''), q_text_style),
                        Paragraph(f"<b>[{q.get('marks', 2)} Marks]</b>", ParagraphStyle('QMarks', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=2))
                    ]

                    # If question has MCQ options, append options cleanly below stem
                    opts = []
                    if q.get('options_json'):
                        try:
                            opts = json.loads(q.get('options_json'))
                        except Exception:
                            opts = []

                    flowables = []
                    t_q = Table([q_row], colWidths=[0.4 * inch, 5.8 * inch, 1.0 * inch])
                    t_q.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('TOPPADDING', (0,0), (-1,-1), 3),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ]))
                    flowables.append(t_q)

                    if opts and len(opts) >= 4:
                        opt_table_data = [
                            [
                                Paragraph(f"<b>A)</b> {opts[0]}", ParagraphStyle('Opt', parent=styles['Normal'], fontSize=8.5, leading=11)),
                                Paragraph(f"<b>B)</b> {opts[1]}", ParagraphStyle('Opt', parent=styles['Normal'], fontSize=8.5, leading=11))
                            ],
                            [
                                Paragraph(f"<b>C)</b> {opts[2]}", ParagraphStyle('Opt', parent=styles['Normal'], fontSize=8.5, leading=11)),
                                Paragraph(f"<b>D)</b> {opts[3]}", ParagraphStyle('Opt', parent=styles['Normal'], fontSize=8.5, leading=11))
                            ]
                        ]
                        t_opts = Table(opt_table_data, colWidths=[3.2 * inch, 3.2 * inch])
                        t_opts.setStyle(TableStyle([
                            ('LEFTPADDING', (0,0), (-1,-1), 24),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        flowables.append(t_opts)

                    flowables.append(Spacer(1, 6))
                    elements.append(KeepTogether(flowables))

        elements.append(Spacer(1, 10))

    # Build the document
    doc.build(elements, canvasmaker=NumberedCanvas)
    return file_path

def generate_answer_key_pdf(
    paper_data: Dict[str, Any],
    institution_data: Optional[Dict[str, Any]] = None,
    output_filename: Optional[str] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    Generates a separate Answer Key PDF document containing correct solutions/options.
    Returns path to generated file.
    """
    folder = output_dir or Config.GENERATED_PAPERS_FOLDER
    os.makedirs(folder, exist_ok=True)
    paper_id = paper_data.get('id', 'temp')
    filename = output_filename or f"Answer_Key_{paper_id}.pdf"
    file_path = os.path.join(folder, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph(f"<b>OFFICIAL ANSWER KEY & EVALUATION SCHEME</b>", ParagraphStyle('KeyHead', alignment=1, fontSize=13, fontName='Helvetica-Bold', spaceAfter=4)),
        Paragraph(f"Subject: {paper_data.get('subject', 'Examination')} | Paper: {paper_data.get('paper_name', '')}", ParagraphStyle('KeySub', alignment=1, fontSize=10, textColor=colors.HexColor("#334155"), spaceAfter=14)),
        HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=12)
    ]

    questions = paper_data.get('questions', paper_data.get('selected_questions', []))

    rows = [["Q#", "Topic / Unit", "Type / Marks", "Correct Answer / Solution Key"]]
    for idx, q in enumerate(questions, start=1):
        q_num = q.get('question_number', str(idx))
        ans = q.get('correct_answer') or f"Detailed analytical solution based on {q.get('topic')} curriculum specifications."
        rows.append([
            f"Q{q_num}",
            f"{q.get('topic')} (Unit {q.get('unit')})",
            f"{q.get('question_type')} ({q.get('marks')}M)",
            Paragraph(ans, ParagraphStyle('AnsText', fontSize=8.5, leading=11))
        ])

    table = Table(rows, colWidths=[0.6*inch, 2.0*inch, 1.4*inch, 3.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(table)

    doc.build(elements, canvasmaker=NumberedCanvas)
    return file_path
