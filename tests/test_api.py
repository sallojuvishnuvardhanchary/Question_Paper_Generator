import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'online'
    assert 'CoreAlgorithm PROBLEM95' in data['problem']

def test_get_questions(client):
    res = client.get('/api/questions?page=1&per_page=5')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['questions']) <= 5
    assert data['total_count'] >= 50

def test_crud_question(client):
    new_q = {
        'question_text': 'Explain Time vs Space Tradeoff in Algorithm Design with examples.',
        'subject': 'Design and Analysis of Algorithms',
        'unit': 1,
        'topic': 'Asymptotic Analysis',
        'difficulty': 'Medium',
        'marks': 10,
        'question_type': 'Descriptive',
        'tags': 'time space tradeoff, analysis',
        'used_count': 0
    }
    # Create
    res = client.post('/api/questions', data=json.dumps(new_q), content_type='application/json')
    assert res.status_code == 201
    created = res.get_json()['question']
    qid = created['id']
    assert qid > 0

    # Read
    res_get = client.get(f'/api/questions/{qid}')
    assert res_get.status_code == 200
    assert res_get.get_json()['question']['question_text'] == new_q['question_text']

    # Update
    update_data = dict(new_q)
    update_data['marks'] = 15
    res_put = client.put(f'/api/questions/{qid}', data=json.dumps(update_data), content_type='application/json')
    assert res_put.status_code == 200
    assert res_put.get_json()['question']['marks'] == 15

    # Delete
    res_del = client.delete(f'/api/questions/{qid}')
    assert res_del.status_code == 200

def test_paper_generation_api(client):
    payload = {
        'paper_name': 'Mid-Term Test DAA',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 50,
        'question_count': 6,
        'algorithm': 'greedy',
        'difficulty_ratio': {'Easy': 0.33, 'Medium': 0.50, 'Hard': 0.17},
        'unit_ratio': {'1': 0.20, '2': 0.20, '3': 0.20, '4': 0.20, '5': 0.20},
        'required_topics': ['Greedy Algorithms', 'Dynamic Programming'],
        'avoid_used': False,
        'max_per_topic': 2,
        'save': False
    }
    res = client.post('/api/generate', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['selected_questions']) == 6
    assert 'validation' in data
    assert 'objective_score' in data

def test_algorithm_compare_api(client):
    payload = {
        'paper_name': 'Algorithm Benchmark',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 50,
        'question_count': 5,
        'difficulty_ratio': {'Easy': 0.40, 'Medium': 0.40, 'Hard': 0.20},
        'unit_ratio': {'1': 0.20, '2': 0.20, '3': 0.20, '4': 0.20, '5': 0.20},
        'required_topics': [],
        'avoid_used': False,
        'max_per_topic': 2
    }
    res = client.post('/api/algorithms/compare', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'greedy' in data
    assert 'backtracking' in data
    assert 'observation' in data

def test_analytics_api(client):
    res = client.get('/api/analytics')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'question_stats' in data
    assert 'paper_stats' in data

def test_api_validation_errors(client):
    # Invalid marks
    bad_payload = {'total_marks': -10, 'question_count': 5}
    res = client.post('/api/generate', data=json.dumps(bad_payload), content_type='application/json')
    assert res.status_code == 400
    assert 'Invalid total marks' in res.get_json()['error']

    # Total marks too low for question count
    low_marks = {'total_marks': 5, 'question_count': 10}
    res2 = client.post('/api/generate', data=json.dumps(low_marks), content_type='application/json')
    assert res2.status_code == 400
    assert 'too low' in res2.get_json()['error']

    # Missing question fields on create
    bad_q = {'question_text': 'Missing other fields'}
    res3 = client.post('/api/questions', data=json.dumps(bad_q), content_type='application/json')
    assert res3.status_code == 400
    assert 'Missing required fields' in res3.get_json()['error']

    # Non-existent question 404
    res4 = client.get('/api/questions/999999')
    assert res4.status_code == 404

def test_syllabus_to_pdf_end_to_end_api(client):
    # 1. Upload syllabus via raw text
    upload_res = client.post('/api/syllabus/upload', data=json.dumps({
        'subject': 'Software Engineering',
        'raw_text': """
        Software Engineering Course
        UNIT I: Agile Methodologies
        Scrum, Sprint Planning, User Stories, Daily Standups.
        
        UNIT II: Design Patterns & Architecture
        MVC, Singleton, Factory Pattern, Microservices.
        """
    }), content_type='application/json')
    assert upload_res.status_code == 200
    s_data = upload_res.get_json()
    assert s_data['success'] is True
    s_id = s_data['syllabus_id']
    assert s_id > 0

    # 2. Generate candidate pool from syllabus
    gen_q_res = client.post('/api/questions/generate', data=json.dumps({
        'syllabus_id': s_id,
        'paper_type': 'theory_bits'
    }), content_type='application/json')
    assert gen_q_res.status_code == 200
    q_data = gen_q_res.get_json()
    assert q_data['success'] is True
    assert len(q_data['questions']) > 0

    # 3. Generate structured examination paper
    paper_payload = {
        'syllabus_id': s_id,
        'paper_name': 'Midterm SE Examination',
        'subject': 'Software Engineering',
        'paper_type': 'theory_bits',
        'algorithm': 'greedy',
        'structure': [
            {
                'part_name': 'PART A',
                'sections': [
                    {
                        'section_name': 'Conceptual Bits',
                        'question_count': 4,
                        'marks_per_question': 2,
                        'question_type': 'Bits',
                        'internal_choice': False
                    }
                ]
            }
        ],
        'total_marks': 8,
        'question_count': 4,
        'save': True
    }
    paper_res = client.post('/api/paper/generate', data=json.dumps(paper_payload), content_type='application/json')
    assert paper_res.status_code == 200
    p_data = paper_res.get_json()
    assert p_data['success'] is True
    paper_id = p_data['paper_id']
    assert paper_id > 0

    # 4. Download Exam Paper PDF
    pdf_res = client.get(f'/api/paper/{paper_id}/download')
    assert pdf_res.status_code == 200
    assert pdf_res.headers['Content-Type'] == 'application/pdf'
    assert len(pdf_res.data) > 500

