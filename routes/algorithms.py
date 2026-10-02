"""
Algorithms API Routes for CoreAlgorithm PROBLEM95.
Provides sorting execution with metrics & steps, algorithm comparison (Greedy vs Backtracking),
and interactive algorithm visualization trace generators.
"""

from flask import Blueprint, request, jsonify
from services.question_service import get_all_questions_for_generation
from services.paper_generator import run_comparison
from algorithms.sorting import (
    bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, run_all_sorting_benchmarks
)
from algorithms.greedy import generate_paper_greedy
from algorithms.backtracking import generate_paper_backtracking

algorithms_bp = Blueprint('algorithms', __name__, url_prefix='/api/algorithms')

@algorithms_bp.route('/sort', methods=['POST'])
def execute_sorting():
    data = request.get_json() or {}
    algo_name = data.get('algorithm', 'bubble').lower()
    sort_key = data.get('key', 'marks')
    ascending = data.get('ascending', True)
    record_steps = data.get('record_steps', True)
    custom_items = data.get('items')

    if custom_items:
        items = custom_items
    else:
        items = get_all_questions_for_generation()

    if not items:
        return jsonify({'success': False, 'error': 'No items to sort.'}), 400

    if algo_name == 'all':
        benchmarks = run_all_sorting_benchmarks(items, key=sort_key, ascending=ascending)
        return jsonify({'success': True, 'benchmarks': benchmarks})

    sort_functions = {
        'bubble': bubble_sort,
        'selection': selection_sort,
        'insertion': insertion_sort,
        'merge': merge_sort,
        'quick': quick_sort
    }

    sort_func = sort_functions.get(algo_name, bubble_sort)
    result = sort_func(items, key=sort_key, ascending=ascending, record_steps=record_steps)

    # Return top 20 sorted items for UI display to avoid massive payloads
    display_items = result['sorted_items'][:25]
    del result['sorted_items']
    result['display_items'] = display_items

    return jsonify({'success': True, **result})

@algorithms_bp.route('/compare', methods=['POST'])
def compare_generation_algorithms():
    config = request.get_json() or {
        'paper_name': 'Algorithm Benchmark Examination',
        'subject': 'Design and Analysis of Algorithms',
        'total_marks': 100,
        'question_count': 10,
        'difficulty_ratio': {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20},
        'unit_ratio': {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20},
        'required_topics': ['Divide and Conquer', 'Greedy Algorithms', 'Dynamic Programming', 'Backtracking', 'NP-Completeness'],
        'avoid_used': False,
        'max_per_topic': 3
    }

    result = run_comparison(config)
    return jsonify(result)

@algorithms_bp.route('/visualize', methods=['POST'])
def get_visualization_trace():
    data = request.get_json() or {}
    algo_type = data.get('type', 'greedy').lower()
    config = data.get('config') or {
        'total_marks': 50,
        'question_count': 5,
        'difficulty_ratio': {'Easy': 0.40, 'Medium': 0.40, 'Hard': 0.20},
        'unit_ratio': {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20},
        'required_topics': [],
        'avoid_used': False,
        'max_per_topic': 2
    }

    pool = get_all_questions_for_generation()
    if not pool:
        return jsonify({'success': False, 'error': 'No questions available in question bank.'}), 400

    if algo_type == 'greedy':
        res = generate_paper_greedy(pool, config)
        return jsonify({
            'success': True,
            'type': 'greedy',
            'logs': res.get('generation_logs', []),
            'selected_questions': res.get('selected_questions', []),
            'statistics': res.get('statistics', {}),
            'objective_score': res.get('objective_score', {})
        })
    elif algo_type == 'backtracking':
        res = generate_paper_backtracking(pool, config)
        return jsonify({
            'success': True,
            'type': 'backtracking',
            'search_tree': res.get('search_tree', []),
            'logs': res.get('generation_logs', []),
            'selected_questions': res.get('selected_questions', []),
            'statistics': res.get('statistics', {}),
            'objective_score': res.get('objective_score', {})
        })
    elif algo_type == 'sorting':
        sort_algo = data.get('algorithm', 'bubble')
        sort_key = data.get('key', 'marks')
        # Use first 15 questions for clean step visualizer
        sample_pool = pool[:15]
        sort_functions = {
            'bubble': bubble_sort,
            'selection': selection_sort,
            'insertion': insertion_sort,
            'merge': merge_sort,
            'quick': quick_sort
        }
        fn = sort_functions.get(sort_algo, bubble_sort)
        res = fn(sample_pool, key=sort_key, ascending=True, record_steps=True)
        return jsonify({
            'success': True,
            'type': 'sorting',
            'algorithm': res['algorithm'],
            'steps': res.get('steps', []),
            'initial_array': [x.get(sort_key, 0) for x in sample_pool],
            'questions': sample_pool,
            'metrics': {
                'comparisons': res['comparisons'],
                'swaps': res['swaps'],
                'execution_time_ms': res['execution_time_ms'],
                'time_complexity': res['time_complexity'],
                'space_complexity': res['space_complexity']
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Unknown visualization type'}), 400
