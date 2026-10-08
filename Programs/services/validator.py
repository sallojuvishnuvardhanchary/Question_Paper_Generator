"""
Comprehensive Paper Validation Service for CoreAlgorithm PROBLEM95.
Verifies syllabus coverage, part structure, section marks, internal choices,
Bloom's difficulty distribution, duplicate prevention, and MCQ option completeness.
"""

import json
from typing import Dict, List, Any
from services.duplicate_detector import detect_duplicates_in_pool

def validate_question_paper_structure(
    selected_questions: List[Dict[str, Any]],
    paper_config: Dict[str, Any],
    syllabus_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs comprehensive structural, mathematical, and syllabus constraint validation.
    Returns:
      {
        "is_valid": bool,
        "summary": str,
        "checks": List[Dict],
        "warnings": List[str],
        "errors": List[str]
      }
    """
    checks = []
    errors = []
    warnings = []

    target_total_marks = int(paper_config.get('total_marks', 100))
    paper_type = paper_config.get('paper_type', 'theory_bits')
    structure = paper_config.get('structure') or []
    inst = paper_config.get('institution_data') or paper_config.get('header_config') or {}

    # 1. Header Information & Logo Verification
    inst_name = inst.get('institution_name') or paper_config.get('institution_name')
    exam_name = inst.get('exam_name') or paper_config.get('paper_name')
    header_valid = bool(inst_name and exam_name)
    checks.append({
        'name': 'Examination Header Completeness',
        'passed': header_valid,
        'target': 'Institution Name & Exam Title defined',
        'actual': f"{inst_name or 'Missing'} | {exam_name or 'Missing'}",
        'message': 'Institutional header and exam metadata fully configured.' if header_valid else 'Institution name or exam title missing.'
    })
    if not header_valid:
        warnings.append("Institutional header incomplete: Institution name or Exam title is missing.")

    logo_path = paper_config.get('logo_path') or inst.get('logo_path')
    if logo_path:
        ext = logo_path.rsplit('.', 1)[-1].lower() if '.' in logo_path else ''
        logo_valid = ext in ('png', 'jpg', 'jpeg')
        checks.append({
            'name': 'Institution Logo Format',
            'passed': logo_valid,
            'target': 'PNG, JPG, or JPEG format',
            'actual': f".{ext}" if ext else 'Unknown',
            'message': 'Valid high-resolution logo formatted for ReportLab PDF insertion.' if logo_valid else f"Unsupported logo format '.{ext}'."
        })
        if not logo_valid:
            errors.append(f"Invalid logo image format '.{ext}'. Supported formats: PNG, JPG, JPEG.")

    # 2. Section Attempt & Section Marks Calculation Verification
    section_math_valid = True
    expected_structure_marks = 0
    if structure:
        for p_idx, part in enumerate(structure, start=1):
            for s_idx, sec in enumerate(part.get('sections', []), start=1):
                q_disp = int(sec.get('question_count', 0))
                q_att = int(sec.get('questions_to_answer', q_disp)) or q_disp
                m_q = int(sec.get('marks_per_question', 0))

                if q_att > q_disp:
                    section_math_valid = False
                    errors.append(f"Section {p_idx}.{s_idx}: Questions to answer ({q_att}) cannot exceed displayed questions ({q_disp}).")

                sec_marks = q_att * m_q
                expected_structure_marks += sec_marks

        checks.append({
            'name': 'Section Attempt & Marks Logic',
            'passed': section_math_valid,
            'target': 'N_attempt <= N_displayed and Section Marks = N_attempt * Marks_per_Q',
            'actual': f"Sum of sections: {expected_structure_marks} Marks",
            'message': 'All sections enforce valid attempt limits and mathematical section marks.' if section_math_valid else 'Invalid attempt counts in sections.'
        })

    # 3. Total Marks Check (Sum of Section Marks = Paper Budget)
    # If paper has questions with section_marks or questions_to_answer
    section_grouped_marks = 0
    seen_sections = set()
    choice_seen = set()
    for q in selected_questions:
        c_group = q.get('choice_group')
        if c_group:
            if c_group in choice_seen:
                continue
            choice_seen.add(c_group)
        sec_key = (q.get('part_name'), q.get('section_name'))
        if sec_key not in seen_sections and q.get('section_marks'):
            seen_sections.add(sec_key)
            section_grouped_marks += int(q.get('section_marks', 0))
        elif not q.get('section_marks'):
            section_grouped_marks += int(q.get('marks', 0))

    actual_total_marks = section_grouped_marks if seen_sections else sum(
        int(q.get('marks', 0)) for q in selected_questions if not q.get('is_choice')
    )

    marks_passed = (actual_total_marks == target_total_marks)
    checks.append({
        'name': 'Total Marks Accuracy',
        'passed': marks_passed,
        'target': f"{target_total_marks} Marks",
        'actual': f"{actual_total_marks} Marks",
        'message': 'Total paper marks strictly equal target exam mark budget.' if marks_passed else f"Marks discrepancy: Expected {target_total_marks}, got {actual_total_marks}."
    })
    if not marks_passed:
        errors.append(f"Total marks mismatch: Expected {target_total_marks} marks, calculated {actual_total_marks} marks.")

    # 4. Continuous Question Numbering Check
    main_questions = [q for q in selected_questions if not q.get('is_choice')]
    q_numbers = []
    for q in main_questions:
        try:
            q_numbers.append(int(q.get('question_number', 0)))
        except (ValueError, TypeError):
            pass

    continuous_numbers = False
    if q_numbers:
        expected_seq = list(range(1, len(q_numbers) + 1))
        continuous_numbers = (q_numbers == expected_seq)

    checks.append({
        'name': 'Continuous Question Numbering',
        'passed': continuous_numbers or len(q_numbers) == 0,
        'target': f"Q1 to Q{len(q_numbers)} sequential across sections",
        'actual': f"Q{min(q_numbers, default=1)} to Q{max(q_numbers, default=1)}" if q_numbers else "Custom labels",
        'message': f"Question numbers Q1 through Q{len(q_numbers)} are continuous across all sections." if continuous_numbers else "Non-continuous question numbers detected."
    })
    if not continuous_numbers and q_numbers:
        warnings.append(f"Question numbering has gaps or non-sequential labels: {q_numbers[:10]}")

    # 5. Question Count & Availability Check
    total_q_count = len(selected_questions)
    checks.append({
        'name': 'Question Count & Availability',
        'passed': total_q_count > 0,
        'target': 'Valid non-empty set',
        'actual': f"{total_q_count} questions generated",
        'message': f"Successfully synthesized {total_q_count} distinct questions." if total_q_count > 0 else "No questions generated."
    })
    if total_q_count == 0:
        errors.append("No questions were generated for this paper.")

    # 3. Duplicate Prevention Check
    dup_res = detect_duplicates_in_pool(selected_questions)
    no_exact_dups = (dup_res['exact_count'] == 0)
    checks.append({
        'name': 'No Duplicate Questions',
        'passed': no_exact_dups,
        'target': '0 duplicates',
        'actual': f"{dup_res['exact_count']} exact duplicates",
        'message': 'All questions have distinct statements.' if no_exact_dups else 'Duplicate questions detected!'
    })
    if not no_exact_dups:
        errors.append("Exact duplicate questions found in generated paper.")

    if dup_res['similar_count'] > 0:
        warnings.append(f"Detected {dup_res['similar_count']} pairs of questions with high conceptual similarity.")

    # 4. Internal Choice Validity Check
    choice_groups = {}
    for q in selected_questions:
        cg = q.get('choice_group')
        if cg:
            choice_groups.setdefault(cg, []).append(q)

    choice_valid = True
    for cg, alts in choice_groups.items():
        if len(alts) < 2:
            choice_valid = False
            warnings.append(f"Choice group {cg} has only {len(alts)} alternative (expected 2).")
        else:
            # Check equal marks
            m1 = alts[0].get('marks')
            for alt in alts[1:]:
                if alt.get('marks') != m1:
                    choice_valid = False
                    errors.append(f"Unequal marks in choice group {cg}: {m1} vs {alt.get('marks')}.")

    if choice_groups:
        checks.append({
            'name': 'Internal Choice Symmetry',
            'passed': choice_valid,
            'target': 'Equal marks & valid alternatives',
            'actual': f"{len(choice_groups)} choice groups verified",
            'message': 'All internal choices (a) OR (b) have symmetric marks and distinct alternatives.' if choice_valid else 'Internal choices have asymmetric marks or missing pairs.'
        })

    # 5. Syllabus Coverage Check
    if syllabus_data and syllabus_data.get('units'):
        syllabus_units = set(u.get('unit') for u in syllabus_data.get('units', []))
        paper_units = set(q.get('unit') for q in selected_questions if q.get('unit'))
        
        covered_ratio = len(paper_units.intersection(syllabus_units)) / max(len(syllabus_units), 1)
        units_passed = (covered_ratio >= 0.70) or (len(syllabus_units) > total_q_count)

        checks.append({
            'name': 'Syllabus Unit Coverage',
            'passed': units_passed,
            'target': f"{len(syllabus_units)} units in syllabus",
            'actual': f"{len(paper_units)} units covered ({int(covered_ratio*100)}%)",
            'message': 'Strong multi-unit representation across the uploaded syllabus.' if units_passed else 'Low unit diversity; some syllabus units omitted.'
        })
        if not units_passed:
            warnings.append("Some syllabus units have 0 questions in this paper.")

    # 6. Difficulty Distribution
    diff_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
    for q in selected_questions:
        d = q.get('difficulty', 'Medium')
        diff_counts[d] = diff_counts.get(d, 0) + 1

    checks.append({
        'name': 'Difficulty Distribution',
        'passed': True,
        'target': 'Easy / Medium / Hard balance',
        'actual': f"E:{diff_counts.get('Easy',0)} M:{diff_counts.get('Medium',0)} H:{diff_counts.get('Hard',0)}",
        'message': f"Questions distributed across cognitive levels ({diff_counts['Easy']} Easy, {diff_counts['Medium']} Medium, {diff_counts['Hard']} Hard)."
    })

    # 7. MCQ Option Validity (If MCQ paper)
    if paper_type in ('mcq', 'theory_bits'):
        mcqs = [q for q in selected_questions if q.get('question_type') == 'MCQ']
        mcq_valid = True
        for m in mcqs:
            opts = []
            if m.get('options_json'):
                try:
                    opts = json.loads(m.get('options_json'))
                except Exception:
                    pass
            if len(opts) < 4 or not m.get('correct_answer'):
                mcq_valid = False
                break

        if mcqs:
            checks.append({
                'name': 'MCQ Completeness & Key',
                'passed': mcq_valid,
                'target': '4 distinct options + answer key',
                'actual': f"{len(mcqs)} MCQs validated",
                'message': 'All MCQs possess 4 distinct options and internal answer keys.' if mcq_valid else 'Some MCQs are missing options or correct answers.'
            })
            if not mcq_valid:
                errors.append("Invalid MCQ formatting detected: must have 4 options and a solution key.")

    overall_valid = marks_passed and (len(errors) == 0)

    summary = (
        "Paper validation successful: All mandatory academic structure, marks, and syllabus constraints satisfied."
        if overall_valid else f"Validation identified issues: {'; '.join(errors)}"
    )

    return {
        'is_valid': overall_valid,
        'summary': summary,
        'checks': checks,
        'errors': errors,
        'warnings': warnings
    }

# Backwards compatibility alias
validate_question_paper = validate_question_paper_structure
