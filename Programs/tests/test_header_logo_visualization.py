"""
Tests for Real-time DAA Algorithm Visualization, Section Attempt Marks Calculation,
Client-Customized Exam Header, and Logo Upload.
CoreAlgorithm PROBLEM95.
"""

import io
import os
import pytest
from PIL import Image as PILImage
from app import create_app
from services.paper_generator import generate_paper
from services.pdf_generator import generate_exam_pdf
from services.validator import validate_question_paper_structure

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_syllabus():
    return {
        'subject': 'Design and Analysis of Algorithms',
        'units': [
            {
                'unit': 1,
                'title': 'Foundations & Asymptotic Analysis',
                'topics': ['Asymptotic Notations', 'Recurrence Relations', 'Master Theorem']
            },
            {
                'unit': 2,
                'title': 'Divide and Conquer & Greedy Techniques',
                'topics': ['Merge Sort', 'Knapsack Problem', 'Huffman Codes']
            },
            {
                'unit': 3,
                'title': 'Dynamic Programming & Graph Algorithms',
                'topics': ['Matrix Chain Multiplication', 'Shortest Paths', 'Bellman Ford']
            }
        ]
    }

def _create_valid_png_bytes():
    img = PILImage.new('RGB', (80, 80), color=(30, 64, 175))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()

def test_logo_upload_api(client):
    # 1. Valid PNG upload
    png_bytes = _create_valid_png_bytes()
    data = {
        'logo': (io.BytesIO(png_bytes), 'test_college_logo.png')
    }
    res = client.post('/api/logo/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data['success'] is True
    assert 'logo_url' in res_data
    assert 'logo_path' in res_data
    assert os.path.exists(res_data['logo_path'])

    # 2. Invalid extension rejection
    bad_data = {
        'logo': (io.BytesIO(b'dummy executable code'), 'malicious_file.exe')
    }
    bad_res = client.post('/api/logo/upload', data=bad_data, content_type='multipart/form-data')
    assert bad_res.status_code == 400
    bad_json = bad_res.get_json()
    assert bad_json['success'] is False
    assert 'Only PNG, JPG, and JPEG' in bad_json['error']

def test_section_attempt_calculation(sample_syllabus):
    """
    Verifies that Section Marks = N_attempt * Marks_per_q (NOT N_disp * Marks_per_q).
    Example:
    Part A Section 1: 5 displayed, attempt 3, 5M each = 15 Marks.
    Part B Section 1: 4 displayed, attempt 2, 10M each = 20 Marks.
    Total Paper Marks = 15 + 20 = 35 Marks.
    """
    config = {
        'paper_name': 'DAA Midterm Examination',
        'subject': 'Design and Analysis of Algorithms',
        'paper_type': 'theory',
        'algorithm': 'greedy',
        'total_marks': 35,
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Short Theory',
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
                        'section_name': 'Analytical Questions',
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

    # Total displayed questions should be 5 + 4 = 9
    assert len(questions) == 9

    # Total marks achieved should be 35 (15 from Part A + 20 from Part B)
    assert result['statistics']['total_marks_achieved'] == 35

    # Check section attributes on questions
    part_a_q = [q for q in questions if q['part_name'] == 'PART A']
    assert len(part_a_q) == 5
    assert part_a_q[0]['questions_to_answer'] == 3
    assert part_a_q[0]['section_marks'] == 15

    part_b_q = [q for q in questions if q['part_name'] == 'PART B']
    assert len(part_b_q) == 4
    assert part_b_q[0]['questions_to_answer'] == 2
    assert part_b_q[0]['section_marks'] == 20

def test_continuous_question_numbering(sample_syllabus):
    """
    Verifies that question numbers are strictly continuous:
    Part A (Q1 to Q5) -> Part B (Q6 to Q9).
    """
    config = {
        'paper_name': 'Continuous Numbering Test',
        'subject': 'Design and Analysis of Algorithms',
        'paper_type': 'theory',
        'algorithm': 'greedy',
        'total_marks': 35,
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Section 1',
                        'question_count': 5,
                        'questions_to_answer': 3,
                        'marks_per_question': 5,
                        'question_type': 'Theory'
                    }
                ]
            },
            {
                'part_name': 'PART B',
                'sections': [
                    {
                        'section_name': 'Section 2',
                        'question_count': 4,
                        'questions_to_answer': 2,
                        'marks_per_question': 10,
                        'question_type': 'Theory'
                    }
                ]
            }
        ]
    }

    result = generate_paper(config, syllabus_data=sample_syllabus, save_to_db=False)
    questions = result['selected_questions']
    q_nums = [q['question_number'] for q in questions if not q.get('is_choice')]
    assert q_nums == ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def test_realtime_trace_events_generation(sample_syllabus):
    """
    Verifies authentic trace events emitted by Greedy and Backtracking.
    """
    # 1. Greedy trace events
    config_greedy = {
        'paper_name': 'Greedy Trace Test',
        'subject': 'Design and Analysis of Algorithms',
        'paper_type': 'theory',
        'algorithm': 'greedy',
        'total_marks': 20,
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Sec 1',
                        'question_count': 4,
                        'questions_to_answer': 4,
                        'marks_per_question': 5,
                        'question_type': 'Theory'
                    }
                ]
            }
        ]
    }
    g_res = generate_paper(config_greedy, syllabus_data=sample_syllabus, save_to_db=False)
    assert 'trace_events' in g_res
    g_events = g_res['trace_events']
    assert len(g_events) > 0

    event_types = [e['event'] for e in g_events]
    assert 'candidate_pool_loaded' in event_types
    assert 'candidates_scored' in event_types
    assert 'candidates_ranked' in event_types
    assert 'candidate_selected' in event_types
    assert 'optimization_completed' in event_types

    # 2. Backtracking trace events
    config_bt = dict(config_greedy)
    config_bt['algorithm'] = 'backtracking'
    bt_res = generate_paper(config_bt, syllabus_data=sample_syllabus, save_to_db=False)
    assert 'trace_events' in bt_res
    bt_events = bt_res['trace_events']
    assert len(bt_events) > 0

    bt_event_types = [e['event'] for e in bt_events]
    assert 'tree_init' in bt_event_types
    assert 'tree_node' in bt_event_types

    # Check node states
    tree_nodes = [e for e in bt_events if e['event'] == 'tree_node']
    assert len(tree_nodes) > 0
    assert any(n['status'] in ('SELECTED', 'EXPLORE', 'PRUNED') for n in tree_nodes)
    assert all('upper_bound' in n for n in tree_nodes)

def test_pdf_generation_with_logo_and_custom_header(tmp_path):
    """
    Verifies that ReportLab PDF generation renders with custom institution header and logo.
    """
    # Create test logo file with real PNG encoding
    logo_file = tmp_path / "inst_logo.png"
    img = PILImage.new('RGB', (80, 80), color=(15, 23, 42))
    img.save(str(logo_file), format='PNG')

    paper_record = {
        'id': 999,
        'paper_name': 'B.Tech III Year II Semester Regular Examinations',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 70,
        'questions': [
            {
                'id': 1,
                'part_name': 'PART A',
                'section_name': 'Short Answer',
                'question_number': '1',
                'question_text': 'State Master Theorem for divide-and-conquer recurrences.',
                'marks': 5,
                'questions_to_answer': 2,
                'section_marks': 10,
                'section_instructions': 'Answer any 2 questions out of 3.'
            },
            {
                'id': 2,
                'part_name': 'PART A',
                'section_name': 'Short Answer',
                'question_number': '2',
                'question_text': 'Explain Huffman coding tree construction algorithm.',
                'marks': 5,
                'questions_to_answer': 2,
                'section_marks': 10,
                'section_instructions': 'Answer any 2 questions out of 3.'
            }
        ]
    }

    inst_data = {
        'institution_name': 'ABC INSTITUTE OF TECHNOLOGY',
        'institution_address': 'AUTONOMOUS EXAMINATIONS BRANCH, HYDERABAD',
        'department': 'DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING',
        'branch': 'Computer Science and Engineering',
        'exam_name': 'B.Tech III Year II Semester Regular Examinations',
        'subject_code': 'CS601PC',
        'course_code': 'R20-CSE',
        'semester': 'III Year II Semester',
        'duration': '3 Hours',
        'exam_date': '15-11-2026',
        'instructions': '1. Answer any 2 questions in Part A.',
        'logo_path': str(logo_file)
    }

    pdf_out = tmp_path / "Test_Exam_Paper_999.pdf"
    res_path = generate_exam_pdf(paper_record, institution_data=inst_data, output_filename=pdf_out.name, output_dir=str(tmp_path))
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000

def test_validator_attempt_constraints():
    """
    Verifies that validator flags when N_attempt > N_disp.
    """
    invalid_structure = [
        {
            'part_name': 'PART A',
            'sections': [
                {
                    'section_name': 'Section 1',
                    'question_count': 3,
                    'questions_to_answer': 5, # INVALID: 5 > 3
                    'marks_per_question': 5
                }
            ]
        }
    ]
    val_res = validate_question_paper_structure([], {'total_marks': 15, 'structure': invalid_structure})
    assert val_res['is_valid'] is False
    assert any('cannot exceed displayed questions' in err for err in val_res['errors'])
