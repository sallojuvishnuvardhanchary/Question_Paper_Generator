"""
Unit & Integration Tests for ReportLab PDF Generation Service
CoreAlgorithm PROBLEM95 - Syllabus-Driven Exam Question Paper Generator
"""

import os
import tempfile
import pytest
from services.pdf_generator import generate_exam_pdf, generate_answer_key_pdf

@pytest.fixture
def mock_paper():
    return {
        'id': 999,
        'paper_name': 'End Semester Examination',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 100,
        'questions': [
            {
                'id': 101,
                'part_name': 'PART A',
                'section_name': 'Short Answer',
                'question_number': '1',
                'question_text': 'State the Master Theorem for solving divide-and-conquer recurrences.',
                'marks': 2,
                'unit': 1,
                'topic': 'Divide and Conquer',
                'difficulty': 'Easy',
                'question_type': 'Bits',
                'is_choice': 0
            },
            {
                'id': 102,
                'part_name': 'PART A',
                'section_name': 'Short Answer',
                'question_number': '2',
                'question_text': 'Define optimal substructure and overlapping subproblems in Dynamic Programming.',
                'marks': 2,
                'unit': 3,
                'topic': 'Dynamic Programming',
                'difficulty': 'Easy',
                'question_type': 'Bits',
                'is_choice': 0
            },
            {
                'id': 201,
                'part_name': 'PART B',
                'section_name': 'Descriptive Questions',
                'question_number': '3',
                'choice_group': 'P2S1Q1',
                'question_text': 'Describe Dijkstra algorithm for single-source shortest paths and analyze its running time.',
                'marks': 16,
                'unit': 2,
                'topic': 'Greedy Algorithms',
                'difficulty': 'Medium',
                'question_type': 'Theory',
                'is_choice': 0
            },
            {
                'id': 202,
                'part_name': 'PART B',
                'section_name': 'Descriptive Questions',
                'question_number': '3',
                'choice_group': 'P2S1Q1',
                'question_text': 'Explain Kruskal algorithm for finding Minimum Spanning Tree with Disjoint Sets.',
                'marks': 16,
                'unit': 2,
                'topic': 'Greedy Algorithms',
                'difficulty': 'Medium',
                'question_type': 'Theory',
                'is_choice': 1
            },
            {
                'id': 301,
                'part_name': 'PART C',
                'section_name': 'Multiple Choice Questions',
                'question_number': '4',
                'question_text': 'What is the time complexity of Quick Sort in the worst case?',
                'marks': 1,
                'unit': 1,
                'topic': 'Sorting',
                'difficulty': 'Medium',
                'question_type': 'MCQ',
                'options_json': '["(A) O(n log n)", "(B) O(n^2)", "(C) O(n)", "(D) O(log n)"]',
                'correct_answer': '(B)',
                'is_choice': 0
            }
        ]
    }

def test_generate_exam_pdf(mock_paper):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_name = "test_exam_paper.pdf"
        file_path = generate_exam_pdf(mock_paper, output_dir=tmpdir, output_filename=output_name)

        assert os.path.exists(file_path)
        assert os.path.getsize(file_path) > 1000

        # Verify PDF header
        with open(file_path, 'rb') as f:
            header = f.read(5)
            assert header == b'%PDF-'

def test_generate_answer_key_pdf(mock_paper):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_name = "test_answer_key.pdf"
        file_path = generate_answer_key_pdf(mock_paper, output_dir=tmpdir, output_filename=output_name)

        assert os.path.exists(file_path)
        assert os.path.getsize(file_path) > 1000

        with open(file_path, 'rb') as f:
            header = f.read(5)
            assert header == b'%PDF-'
