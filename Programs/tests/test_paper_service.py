"""
Integration Tests for Paper Service Orchestration & Validation
CoreAlgorithm PROBLEM95 - Syllabus-Driven Exam Question Paper Generator
"""

import pytest
from services.paper_generator import generate_paper, _generate_structured_paper
from services.validator import validate_question_paper_structure

@pytest.fixture
def sample_syllabus_data():
    return {
        'subject': 'Operating Systems',
        'units': [
            {'unit': 1, 'title': 'Processes', 'topics': ['Processes', 'Threads', 'CPU Scheduling']},
            {'unit': 2, 'title': 'Concurrency', 'topics': ['Semaphores', 'Deadlocks', 'Mutex']},
            {'unit': 3, 'title': 'Memory', 'topics': ['Paging', 'Segmentation', 'Virtual Memory']},
            {'unit': 4, 'title': 'File Systems', 'topics': ['File Allocation', 'Directory Structure']},
            {'unit': 5, 'title': 'I/O & Security', 'topics': ['Disk Scheduling', 'Protection']}
        ]
    }

def test_structured_paper_generation(sample_syllabus_data):
    config = {
        'paper_name': 'OS Mid-Term Test',
        'subject': 'Operating Systems',
        'paper_type': 'theory_bits',
        'algorithm': 'greedy',
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Short Answer Bits',
                        'question_count': 5,
                        'marks_per_question': 2,
                        'question_type': 'Bits',
                        'internal_choice': False
                    }
                ]
            },
            {
                'part_name': 'PART B',
                'sections': [
                    {
                        'section_name': 'Descriptive Questions',
                        'question_count': 4,
                        'marks_per_question': 10,
                        'question_type': 'Theory',
                        'internal_choice': True
                    }
                ]
            }
        ],
        'total_marks': 50,
        'question_count': 9
    }

    result = generate_paper(config, syllabus_data=sample_syllabus_data, save_to_db=False)
    assert result['success'] is True
    questions = result['selected_questions']

    # Total questions = 5 in Part A + 4 primary + 4 internal choices in Part B = 13
    assert len(questions) == 13

    # Primary marks total = 5 * 2 + 4 * 10 = 50
    primary_marks = sum(q['marks'] for q in questions if not q.get('is_choice'))
    assert primary_marks == 50

    # Validation should pass
    val = result['validation']
    assert val['is_valid'] is True
    assert len(val['errors']) == 0

def test_validation_detects_marks_mismatch():
    questions = [
        {'id': 1, 'question_text': 'Q1', 'marks': 10, 'is_choice': 0, 'choice_group': ''},
        {'id': 2, 'question_text': 'Q2', 'marks': 15, 'is_choice': 0, 'choice_group': ''}
    ]
    config = {'total_marks': 30, 'paper_type': 'theory'}
    val = validate_question_paper_structure(questions, config)
    assert val['is_valid'] is False
    assert any("Total marks mismatch" in e for e in val['errors'])

def test_validation_detects_choice_asymmetry():
    questions = [
        {'id': 1, 'question_text': 'Q1', 'marks': 10, 'is_choice': 0, 'choice_group': 'G1'},
        {'id': 2, 'question_text': 'Q2', 'marks': 8, 'is_choice': 1, 'choice_group': 'G1'}
    ]
    config = {'total_marks': 10, 'paper_type': 'theory'}
    val = validate_question_paper_structure(questions, config)
    assert val['is_valid'] is False
    assert any("Unequal marks in choice group" in e for e in val['errors'])

def test_paper_generation_with_db_save_and_pdf(sample_syllabus_data):
    config = {
        'paper_name': 'OS Semester Exam DB Test',
        'subject': 'Operating Systems',
        'paper_type': 'theory_bits',
        'algorithm': 'greedy',
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Short Answer',
                        'question_count': 3,
                        'marks_per_question': 2,
                        'question_type': 'Bits',
                        'internal_choice': False
                    }
                ]
            }
        ],
        'total_marks': 6,
        'question_count': 3
    }
    result = generate_paper(config, syllabus_data=sample_syllabus_data, save_to_db=True)
    assert result['success'] is True
    assert result.get('paper_id') is not None
    assert result.get('pdf_url') is not None

