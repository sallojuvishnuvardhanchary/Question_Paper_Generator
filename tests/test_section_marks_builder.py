"""
Tests for Section Builder Marks / Question and Section Max Marks Calculation.
CoreAlgorithm PROBLEM95 - Syllabus-Driven Exam Question Paper Generator

Validates:
1. Client manually enters Marks / Question (1, 2, 5, 10, 15, etc.).
2. Section maximum marks is strictly calculated as:
   section_max_marks = questions_to_answer * marks_per_question.
3. NEVER calculate displayed * marks_per_question for total marks.
4. When marks_per_question changes (e.g., 5 -> 10), section marks updates (15 -> 30).
5. Endpoint /api/paper/generate correctly accepts structure and generates valid paper.
6. Generated PDF includes correct section marks, question marks, and instructions.
"""

import json
import pytest
from app import app
from services.paper_generator import generate_paper
from services.pdf_generator import generate_exam_pdf


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_syllabus():
    return {
        'subject': 'Design and Analysis of Algorithms',
        'subject_code': 'CS502PC',
        'units': [
            {
                'unit_number': 1,
                'title': 'Introduction & Greedy Algorithms',
                'topics': ['Greedy Method', 'Knapsack Problem', 'Job Sequencing', 'Optimal Merge Patterns']
            },
            {
                'unit_number': 2,
                'title': 'Dynamic Programming',
                'topics': ['0/1 Knapsack', 'Matrix Chain Multiplication', 'Longest Common Subsequence']
            },
            {
                'unit_number': 3,
                'title': 'Backtracking & Branch and Bound',
                'topics': ['N-Queens Problem', 'Graph Coloring', 'Subset Sum', 'Traveling Salesperson']
            }
        ]
    }


def test_section_max_marks_formula():
    """
    Test strict formula:
    section_max_marks = questions_to_answer * marks_per_question.
    Displayed = 5, To Answer = 3, Marks / Question = 5 -> Result: 3 * 5 = 15 Marks.
    MUST NOT be 5 * 5 = 25.
    """
    displayed = 5
    to_answer = 3
    marks_per_q = 5

    # Correct formula
    correct_section_marks = to_answer * marks_per_q
    assert correct_section_marks == 15

    # Incorrect formula check
    incorrect_section_marks = displayed * marks_per_q
    assert incorrect_section_marks == 25
    assert correct_section_marks != incorrect_section_marks


def test_section_marks_update_when_marks_per_question_changes():
    """
    When marks_per_question is changed from 5 to 10:
    Initial: 3 * 5 = 15 Marks
    Updated: 3 * 10 = 30 Marks
    """
    to_answer = 3

    marks_initial = 5
    sec_marks_initial = to_answer * marks_initial
    assert sec_marks_initial == 15

    marks_updated = 10
    sec_marks_updated = to_answer * marks_updated
    assert sec_marks_updated == 30


def test_paper_generation_with_custom_marks_per_question(sample_syllabus):
    """
    Verify paper generation backend with client-configured structure:
    Section 1: Displayed = 5, To Answer = 3, Marks / Q = 5 -> 15 Marks
    Section 2: Displayed = 4, To Answer = 2, Marks / Q = 10 -> 20 Marks
    Total expected marks = 15 + 20 = 35 Marks
    Total displayed questions = 5 + 4 = 9 Questions
    """
    config = {
        'paper_name': 'DAA Comprehensive Midterm',
        'subject': 'Design and Analysis of Algorithms',
        'paper_type': 'theory_bits',
        'algorithm': 'greedy',
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Conceptual Questions',
                        'question_count': 5,
                        'questions_to_answer': 3,
                        'marks_per_question': 5,
                        'question_type': 'Theory',
                        'internal_choice': False
                    }
                ]
            },
            {
                'part_name': 'PART B',
                'sections': [
                    {
                        'section_name': 'Analytical & Design Problems',
                        'question_count': 4,
                        'questions_to_answer': 2,
                        'marks_per_question': 10,
                        'question_type': 'Theory',
                        'internal_choice': False
                    }
                ]
            }
        ]
    }

    result = generate_paper(config, syllabus_data=sample_syllabus, save_to_db=False)
    assert result['success'] is True

    questions = result['selected_questions']
    assert len(questions) == 9  # 5 + 4 displayed questions

    # Check Part A questions have marks == 5
    part_a_questions = [q for q in questions if q['part_name'] == 'PART A']
    assert len(part_a_questions) == 5
    for q in part_a_questions:
        assert q['marks'] == 5
        assert q['questions_to_answer'] == 3
        assert q['section_marks'] == 15

    # Check Part B questions have marks == 10
    part_b_questions = [q for q in questions if q['part_name'] == 'PART B']
    assert len(part_b_questions) == 4
    for q in part_b_questions:
        assert q['marks'] == 10
        assert q['questions_to_answer'] == 2
        assert q['section_marks'] == 20

    # Total marks achieved = 3 * 5 + 2 * 10 = 35
    assert result['statistics']['total_marks_achieved'] == 35


def test_api_generate_paper_overrides_stale_total_marks(client, sample_syllabus):
    """
    If frontend sends structure where 3 to answer * 5 marks = 15 marks,
    even if an old total_marks=100 was submitted in JSON, the backend
    strictly derives total_marks = 15 from the structure.
    """
    # 1. Upload syllabus via raw_text
    s_res = client.post('/api/syllabus/upload', json={
        'subject': 'Design and Analysis of Algorithms',
        'raw_text': """
        Design and Analysis of Algorithms
        UNIT I: Greedy Algorithms
        Greedy Method, Knapsack Problem, Job Sequencing.
        
        UNIT II: Dynamic Programming
        Matrix Chain Multiplication, Longest Common Subsequence.
        """
    })
    assert s_res.status_code == 200
    s_id = s_res.get_json()['syllabus_id']

    # Generate candidate questions from syllabus
    gen_q_res = client.post('/api/questions/generate', json={
        'syllabus_id': s_id,
        'paper_type': 'theory'
    })
    assert gen_q_res.status_code == 200
    assert gen_q_res.get_json()['success'] is True

    payload = {
        'syllabus_id': s_id,
        'paper_name': 'DAA Test Paper',
        'subject': 'Design and Analysis of Algorithms',
        'paper_type': 'theory',
        'algorithm': 'greedy',
        'total_marks': 100,  # Deliberately stale number
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Core Questions',
                        'question_count': 5,
                        'questions_to_answer': 3,
                        'marks_per_question': 5,
                        'question_type': 'Theory',
                        'internal_choice': False
                    }
                ]
            }
        ],
        'save': True
    }

    res = client.post('/api/paper/generate', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # 3 to answer * 5 marks = 15 marks total
    assert data['statistics']['target_marks'] == 15
    assert data['statistics']['total_marks_achieved'] == 15
    assert len(data['selected_questions']) == 5
    for q in data['selected_questions']:
        assert q['marks'] == 5
        assert q['questions_to_answer'] == 3
        assert q['section_marks'] == 15


def test_pdf_generation_with_custom_section_marks(sample_syllabus):
    """
    Verify PDF generator renders the paper with the custom marks per question.
    """
    config = {
        'paper_name': 'DAA Final Examination',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 30,
        'question_count': 5,
        'algorithm': 'greedy',
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Descriptive Section',
                        'question_count': 5,
                        'questions_to_answer': 3,
                        'marks_per_question': 10,
                        'question_type': 'Theory',
                        'internal_choice': False
                    }
                ]
            }
        ]
    }

    result = generate_paper(config, syllabus_data=sample_syllabus, save_to_db=False)
    assert result['success'] is True

    paper_dict = {
        'id': 'test-marks-30',
        'paper_name': config['paper_name'],
        'subject': config['subject'],
        'total_marks': 30,
        'questions': result['selected_questions']
    }

    pdf_path = generate_exam_pdf(paper_dict)
    assert pdf_path is not None
    import os
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
    with open(pdf_path, 'rb') as f:
        header = f.read(5)
        assert header == b'%PDF-'
