"""
Papers API Routes for CoreAlgorithm PROBLEM95.
Provides paper generation, historical listing, single paper retrieval, and deletion.
"""

from flask import Blueprint, request, jsonify
from services.paper_generator import generate_paper, get_papers, get_paper_by_id, delete_paper

papers_bp = Blueprint('papers', __name__, url_prefix='/api')

@papers_bp.route('/generate', methods=['POST'])
@papers_bp.route('/paper/generate', methods=['POST'])
def generate_question_paper_endpoint():
    config = request.get_json() or {}

    # If dynamic structure is provided, derive marks and count if not explicitly set
    if config.get('structure'):
        calc_marks = 0
        calc_count = 0
        for p in config['structure']:
            sections = p.get('sections', [])
            if not sections:
                q_c = int(p.get('question_count', 0))
                m_q = int(p.get('marks_per_question', 0))
                calc_count += q_c
                calc_marks += q_c * m_q
            else:
                for s in sections:
                    q_c = int(s.get('question_count', 0))
                    m_q = int(s.get('marks_per_question', 0))
                    calc_count += q_c
                    calc_marks += q_c * m_q
        if not config.get('total_marks') or int(config.get('total_marks', 0)) <= 0:
            config['total_marks'] = calc_marks
        if not config.get('question_count') or int(config.get('question_count', 0)) <= 0:
            config['question_count'] = calc_count

    # Validation
    total_marks = config.get('total_marks')
    question_count = config.get('question_count')

    if not total_marks or int(total_marks) <= 0:
        return jsonify({'success': False, 'error': 'Invalid total marks. Must be greater than 0.'}), 400

    if not question_count or int(question_count) <= 0:
        return jsonify({'success': False, 'error': 'Invalid question count. Must be greater than 0.'}), 400

    total_marks = int(total_marks)
    question_count = int(question_count)

    # Sanity bounds (allow flexible bounds for MCQ/Bits)
    if total_marks < question_count:
        return jsonify({
            'success': False,
            'error': f'Total marks ({total_marks}) is too low for {question_count} questions. Minimum 1 mark per question required.'
        }), 400

    # Ensure difficulty ratios sum to ~1.0
    diff_ratio = config.get('difficulty_ratio', {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20})
    diff_sum = sum(diff_ratio.values())
    if abs(diff_sum - 1.0) > 0.05 and diff_sum > 0:
        config['difficulty_ratio'] = {k: v / diff_sum for k, v in diff_ratio.items()}

    # Ensure unit ratios sum to ~1.0
    unit_ratio = config.get('unit_ratio', {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20})
    normalized_units = {}
    for k, v in unit_ratio.items():
        try:
            normalized_units[int(k)] = float(v)
        except (ValueError, TypeError):
            pass
    unit_sum = sum(normalized_units.values())
    if abs(unit_sum - 1.0) > 0.05 and unit_sum > 0:
        config['unit_ratio'] = {k: v / unit_sum for k, v in normalized_units.items()}
    elif normalized_units:
        config['unit_ratio'] = normalized_units

    save_flag = config.get('save', True)
    syllabus_data = config.get('syllabus_data')

    try:
        result = generate_paper(config, syllabus_data=syllabus_data, save_to_db=save_flag)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Generation error: {str(e)}'}), 500

@papers_bp.route('/paper/validate', methods=['POST'])
@papers_bp.route('/validate', methods=['POST'])
def validate_paper_endpoint():
    data = request.get_json() or {}
    questions = data.get('questions', [])
    config = data.get('config', {})
    syllabus_data = data.get('syllabus_data')

    from services.validator import validate_question_paper_structure
    val_res = validate_question_paper_structure(questions, config, syllabus_data)
    return jsonify({'success': True, 'validation': val_res})

@papers_bp.route('/papers', methods=['GET'])
def list_generated_papers():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    data = get_papers(page=page, per_page=per_page)
    return jsonify({'success': True, **data})

@papers_bp.route('/papers/<int:pid>', methods=['GET'])
def get_paper_details(pid):
    paper = get_paper_by_id(pid)
    if not paper:
        return jsonify({'success': False, 'error': f'Paper ID {pid} not found'}), 404
    return jsonify({'success': True, 'paper': paper})

@papers_bp.route('/papers/<int:pid>', methods=['DELETE'])
def remove_paper(pid):
    deleted = delete_paper(pid)
    if not deleted:
        return jsonify({'success': False, 'error': f'Paper ID {pid} not found'}), 404
    return jsonify({'success': True, 'message': f'Paper {pid} deleted successfully'})
