"""
Unit & Integration Tests for Question Generation Service
CoreAlgorithm PROBLEM95 - Syllabus-Driven Exam Question Paper Generator
"""

import json
import pytest
from services.question_generator import generate_candidate_questions

@pytest.fixture
def mock_syllabus():
    return {
        'subject': 'Operating Systems',
        'units': [
            {
                'unit': 1,
                'title': 'Process Management',
                'topics': ['Process Scheduling', 'Inter-process Communication', 'Threads']
            },
            {
                'unit': 2,
                'title': 'Concurrency & Synchronization',
                'topics': ['Semaphores', 'Monitors', 'Deadlocks']
            },
            {
                'unit': 3,
                'title': 'Memory Management',
                'topics': ['Virtual Memory', 'Paging', 'Page Replacement Algorithms']
            }
        ]
    }

def test_generate_theory_bits_questions(mock_syllabus):
    res = generate_candidate_questions(mock_syllabus, paper_type='theory_bits')
    assert res['success'] is True
    questions = res['questions']
    assert len(questions) > 10

    # Verify presence of both Bits (2M) and Theory (5M/10M/16M)
    marks_set = set(q['marks'] for q in questions)
    assert 2 in marks_set
    assert any(m >= 5 for m in marks_set)

    # Verify Bloom's difficulty tiers
    difficulties = set(q['difficulty'] for q in questions)
    assert 'Easy' in difficulties
    assert 'Medium' in difficulties
    assert 'Hard' in difficulties

    # Verify unit assignment
    units_in_pool = set(q['unit'] for q in questions)
    assert units_in_pool == {1, 2, 3}

def test_generate_mcq_questions(mock_syllabus):
    res = generate_candidate_questions(mock_syllabus, paper_type='mcq')
    assert res['success'] is True
    questions = res['questions']
    assert len(questions) >= 15

    for q in questions:
        assert q['question_type'] == 'MCQ'
        assert q['marks'] == 1
        assert q.get('options_json') is not None
        opts = json.loads(q['options_json'])
        # Exactly 4 distinct options
        assert len(opts) == 4
        assert len(set(opts)) == 4
        # Options formatted with A), B), C), D)
        assert opts[0].startswith('(A)')
        assert opts[1].startswith('(B)')
        assert opts[2].startswith('(C)')
        assert opts[3].startswith('(D)')
        # Valid correct answer key
        assert q.get('correct_answer') in ('(A)', '(B)', '(C)', '(D)')

def test_generate_theory_only_questions(mock_syllabus):
    res = generate_candidate_questions(mock_syllabus, paper_type='theory')
    assert res['success'] is True
    questions = res['questions']
    for q in questions:
        assert q['marks'] >= 5
        assert q['question_type'] in ('Theory', 'Descriptive', 'Long Answer')
