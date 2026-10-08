import pytest
from algorithms.greedy import generate_paper_greedy
from algorithms.backtracking import generate_paper_backtracking
from algorithms.sorting import bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort
from algorithms.scoring import calculate_objective_score

@pytest.fixture
def sample_pool():
    return [
        {'id': 1, 'question_text': 'Q1', 'unit': 1, 'topic': 'Sorting', 'difficulty': 'Easy', 'marks': 5, 'used_count': 0, 'question_type': 'Theory'},
        {'id': 2, 'question_text': 'Q2', 'unit': 1, 'topic': 'Divide and Conquer', 'difficulty': 'Medium', 'marks': 10, 'used_count': 0, 'question_type': 'Descriptive'},
        {'id': 3, 'question_text': 'Q3', 'unit': 2, 'topic': 'Greedy Algorithms', 'difficulty': 'Easy', 'marks': 5, 'used_count': 0, 'question_type': 'Short Answer'},
        {'id': 4, 'question_text': 'Q4', 'unit': 2, 'topic': 'Graphs', 'difficulty': 'Hard', 'marks': 10, 'used_count': 0, 'question_type': 'Programming'},
        {'id': 5, 'question_text': 'Q5', 'unit': 3, 'topic': 'Dynamic Programming', 'difficulty': 'Medium', 'marks': 10, 'used_count': 0, 'question_type': 'Descriptive'},
        {'id': 6, 'question_text': 'Q6', 'unit': 3, 'topic': 'Dynamic Programming', 'difficulty': 'Easy', 'marks': 5, 'used_count': 1, 'question_type': 'Theory'},
        {'id': 7, 'question_text': 'Q7', 'unit': 4, 'topic': 'Backtracking', 'difficulty': 'Medium', 'marks': 10, 'used_count': 0, 'question_type': 'Descriptive'},
        {'id': 8, 'question_text': 'Q8', 'unit': 4, 'topic': 'Branch and Bound', 'difficulty': 'Hard', 'marks': 15, 'used_count': 0, 'question_type': 'Long Answer'},
        {'id': 9, 'question_text': 'Q9', 'unit': 5, 'topic': 'NP-Completeness', 'difficulty': 'Easy', 'marks': 5, 'used_count': 0, 'question_type': 'MCQ'},
        {'id': 10, 'question_text': 'Q10', 'unit': 5, 'topic': 'Approximation Algorithms', 'difficulty': 'Hard', 'marks': 10, 'used_count': 0, 'question_type': 'Theory'}
    ]

def test_greedy_generation(sample_pool):
    config = {
        'total_marks': 40,
        'question_count': 5,
        'difficulty_ratio': {'Easy': 0.40, 'Medium': 0.40, 'Hard': 0.20},
        'unit_ratio': {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20},
        'required_topics': [],
        'avoid_used': False,
        'max_per_topic': 2
    }
    result = generate_paper_greedy(sample_pool, config)
    assert len(result['selected_questions']) == 5
    assert len(result['generation_logs']) == 5
    assert result['statistics']['questions_selected'] == 5
    # Unique question ids
    q_ids = [q['id'] for q in result['selected_questions']]
    assert len(q_ids) == len(set(q_ids))
    # Objective score exists and is between 0 and 100
    assert 0 <= result['objective_score']['total_score'] <= 100

def test_backtracking_generation(sample_pool):
    config = {
        'total_marks': 35,
        'question_count': 4,
        'difficulty_ratio': {'Easy': 0.25, 'Medium': 0.50, 'Hard': 0.25},
        'unit_ratio': {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25, 5: 0.0},
        'required_topics': [],
        'avoid_used': False,
        'max_per_topic': 2
    }
    result = generate_paper_backtracking(sample_pool, config)
    assert result['success'] is True
    assert len(result['selected_questions']) == 4
    assert sum(q['marks'] for q in result['selected_questions']) == 35
    assert len(result['search_tree']) > 0
    assert result['statistics']['states_explored'] > 0

def test_sorting_algorithms():
    items = [
        {'id': 1, 'marks': 15, 'difficulty': 'Hard', 'unit': 3},
        {'id': 2, 'marks': 5, 'difficulty': 'Easy', 'unit': 1},
        {'id': 3, 'marks': 10, 'difficulty': 'Medium', 'unit': 2},
        {'id': 4, 'marks': 2, 'difficulty': 'Easy', 'unit': 5},
        {'id': 5, 'marks': 10, 'difficulty': 'Medium', 'unit': 4}
    ]

    for sort_func in [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]:
        res = sort_func(items, key='marks', ascending=True)
        sorted_marks = [q['marks'] for q in res['sorted_items']]
        assert sorted_marks == [2, 5, 10, 10, 15]
        assert res['comparisons'] > 0
        assert res['execution_time_ms'] >= 0.0

def test_sorting_edge_cases():
    # 1. Empty list
    for sort_func in [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]:
        res = sort_func([], key='marks')
        assert res['sorted_items'] == []
        assert res['comparisons'] == 0

    # 2. Single element
    single = [{'id': 1, 'marks': 10}]
    for sort_func in [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]:
        res = sort_func(single, key='marks')
        assert len(res['sorted_items']) == 1

    # 3. All duplicates
    dups = [{'id': i, 'marks': 5} for i in range(5)]
    for sort_func in [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]:
        res = sort_func(dups, key='marks')
        assert len(res['sorted_items']) == 5
        assert all(q['marks'] == 5 for q in res['sorted_items'])

def test_backtracking_impossible_constraints():
    pool = [
        {'id': 1, 'question_text': 'Q1', 'unit': 1, 'topic': 'A', 'difficulty': 'Easy', 'marks': 2, 'used_count': 0},
        {'id': 2, 'question_text': 'Q2', 'unit': 1, 'topic': 'B', 'difficulty': 'Easy', 'marks': 2, 'used_count': 0}
    ]
    # Request 5 questions when only 2 exist
    config = {
        'total_marks': 50,
        'question_count': 5,
        'difficulty_ratio': {'Easy': 1.0, 'Medium': 0.0, 'Hard': 0.0},
        'unit_ratio': {1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
        'required_topics': [],
        'avoid_used': False,
        'max_per_topic': 2
    }
    result = generate_paper_backtracking(pool, config)
    assert result['success'] is False
    assert result['statistics']['questions_selected'] < 5

def test_greedy_required_topics_preference(sample_pool):
    config = {
        'total_marks': 35,
        'question_count': 4,
        'difficulty_ratio': {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20},
        'unit_ratio': {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25, 5: 0.0},
        'required_topics': ['Greedy Algorithms', 'Dynamic Programming'],
        'avoid_used': False,
        'max_per_topic': 2
    }
    result = generate_paper_greedy(sample_pool, config)
    topics = [q['topic'] for q in result['selected_questions']]
    assert 'Greedy Algorithms' in topics or 'Dynamic Programming' in topics

def test_objective_scoring():
    questions = [
        {'id': 1, 'difficulty': 'Easy', 'unit': 1, 'topic': 'Sorting', 'marks': 10, 'used_count': 0, 'question_type': 'Theory'},
        {'id': 2, 'difficulty': 'Medium', 'unit': 2, 'topic': 'Greedy Algorithms', 'marks': 10, 'used_count': 0, 'question_type': 'Descriptive'},
        {'id': 3, 'difficulty': 'Hard', 'unit': 3, 'topic': 'Dynamic Programming', 'marks': 10, 'used_count': 0, 'question_type': 'Programming'}
    ]
    config = {
        'total_marks': 30,
        'question_count': 3,
        'difficulty_ratio': {'Easy': 0.33, 'Medium': 0.33, 'Hard': 0.34},
        'unit_ratio': {1: 0.33, 2: 0.33, 3: 0.34, 4: 0.0, 5: 0.0},
        'required_topics': ['Sorting', 'Greedy Algorithms']
    }
    score_res = calculate_objective_score(questions, config)
    assert score_res['total_score'] >= 85.0
    assert 'difficulty' in score_res['breakdown']
    assert 'unit' in score_res['breakdown']
    assert 'topic' in score_res['breakdown']
    assert 'marks_fit' in score_res['breakdown']
    assert 'novelty' in score_res['breakdown']
