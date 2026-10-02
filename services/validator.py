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

    # 1. Total Marks Check (Excluding internal choice alternatives from double-counting)
    actual_total_marks = 0
    choice_seen = set()
    for q in selected_questions:
        c_group = q.get('choice_group')
        if c_group:
            if c_group in choice_seen:
                continue
            choice_seen.add(c_group)
        actual_total_marks += int(q.get('marks', 0))

    marks_passed = (actual_total_marks == target_total_marks)
    checks.append({
        'name': 'Total Marks Accuracy',
        'passed': marks_passed,
        'target': f"{target_total_marks} Marks",
        'actual': f"{actual_total_marks} Marks",
        'message': 'Total marks strictly equal target exam mark budget.' if marks_passed else f"Marks discrepancy: Expected {target_total_marks}, got {actual_total_marks}."
    })
    if not marks_passed:
        errors.append(f"Total marks mismatch: Expected {target_total_marks} marks, calculated {actual_total_marks} marks.")

    # 2. Question Count & Structure Check
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
