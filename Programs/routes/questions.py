"""
Questions API Routes for CoreAlgorithm PROBLEM95.
Provides complete CRUD endpoints, filtering, searching, and metadata.
"""

from flask import Blueprint, request, jsonify
from services.question_service import (
    get_questions, get_question_by_id, create_question,
    update_question, delete_question, get_topics_and_units
)

questions_bp = Blueprint('questions', __name__, url_prefix='/api/questions')

@questions_bp.route('', methods=['GET'])
def list_questions():
    search = request.args.get('search')
    unit = request.args.get('unit')
    difficulty = request.args.get('difficulty')
    marks = request.args.get('marks')
    topic = request.args.get('topic')
    question_type = request.args.get('question_type')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    data = get_questions(
        search=search,
        unit=unit,
        difficulty=difficulty,
        marks=marks,
        topic=topic,
        question_type=question_type,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )
    return jsonify({'success': True, **data})

@questions_bp.route('/<int:qid>', methods=['GET'])
def get_single_question(qid):
    q = get_question_by_id(qid)
    if not q:
        return jsonify({'success': False, 'error': f'Question ID {qid} not found'}), 404
    return jsonify({'success': True, 'question': q})

@questions_bp.route('', methods=['POST'])
def add_question():
    data = request.get_json() or {}
    # Validation
    required_fields = ['question_text', 'unit', 'topic', 'difficulty', 'marks', 'question_type']
    missing = [f for f in required_fields if f not in data or str(data[f]).strip() == '']
    if missing:
        return jsonify({'success': False, 'error': f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        unit = int(data['unit'])
        if unit < 1 or unit > 5:
            return jsonify({'success': False, 'error': 'Unit must be between 1 and 5'}), 400
        
        marks = int(data['marks'])
        if marks <= 0:
            return jsonify({'success': False, 'error': 'Marks must be greater than 0'}), 400

        if data['difficulty'] not in ('Easy', 'Medium', 'Hard'):
            return jsonify({'success': False, 'error': 'Difficulty must be Easy, Medium, or Hard'}), 400

        created = create_question(data)
        return jsonify({'success': True, 'message': 'Question created successfully', 'question': created}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid numeric value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@questions_bp.route('/<int:qid>', methods=['PUT'])
def edit_question(qid):
    existing = get_question_by_id(qid)
    if not existing:
        return jsonify({'success': False, 'error': f'Question ID {qid} not found'}), 404

    data = request.get_json() or {}
    required_fields = ['question_text', 'unit', 'topic', 'difficulty', 'marks', 'question_type']
    missing = [f for f in required_fields if f not in data or str(data[f]).strip() == '']
    if missing:
        return jsonify({'success': False, 'error': f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        unit = int(data['unit'])
        if unit < 1 or unit > 5:
            return jsonify({'success': False, 'error': 'Unit must be between 1 and 5'}), 400
        
        marks = int(data['marks'])
        if marks <= 0:
            return jsonify({'success': False, 'error': 'Marks must be greater than 0'}), 400

        updated = update_question(qid, data)
        return jsonify({'success': True, 'message': 'Question updated successfully', 'question': updated})
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid numeric value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@questions_bp.route('/<int:qid>', methods=['DELETE'])
def remove_question(qid):
    deleted = delete_question(qid)
    if not deleted:
        return jsonify({'success': False, 'error': f'Question ID {qid} not found or could not be deleted'}), 404
    return jsonify({'success': True, 'message': f'Question {qid} deleted successfully'})

@questions_bp.route('/meta', methods=['GET'])
def get_metadata():
    meta = get_topics_and_units()
    return jsonify({'success': True, **meta})

@questions_bp.route('/generate', methods=['POST'])
def generate_questions_from_syllabus_endpoint():
    data = request.get_json() or {}
    syllabus_id = data.get('syllabus_id')
    syllabus_data = data.get('syllabus_data')
    paper_type = data.get('paper_type', 'theory_bits')
    custom_topics = data.get('custom_topics')

    from database.database import get_db_connection
    import json

    # If syllabus_id provided, fetch structured data
    if syllabus_id and not syllabus_data:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM syllabi WHERE id = ?", (syllabus_id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({'success': False, 'error': f"Syllabus #{syllabus_id} not found."}), 404
        try:
            syllabus_data = json.loads(row['structured_data'])
        except Exception:
            syllabus_data = {'subject': row['subject'], 'units': []}

    if not syllabus_data or not syllabus_data.get('units'):
        return jsonify({'success': False, 'error': 'Invalid or empty syllabus data. Please upload a syllabus first.'}), 400

    from services.question_generator import generate_candidate_questions

    try:
        res = generate_candidate_questions(syllabus_data, paper_type=paper_type, custom_topics=custom_topics)
        
        # Save generated questions into generated_questions table if syllabus_id exists
        if syllabus_id and res.get('questions'):
            conn = get_db_connection()
            cur = conn.cursor()
            # Clear previous generated pool for this syllabus if requested
            if data.get('replace_existing', True):
                cur.execute("DELETE FROM generated_questions WHERE syllabus_id = ?", (syllabus_id,))

            for q in res['questions']:
                cur.execute("""
                    INSERT INTO generated_questions 
                    (syllabus_id, question_text, unit, topic, subtopic, difficulty, marks, question_type, options_json, correct_answer, generation_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    syllabus_id,
                    q['question_text'],
                    q['unit'],
                    q['topic'],
                    q.get('subtopic', ''),
                    q['difficulty'],
                    q['marks'],
                    q['question_type'],
                    q.get('options_json', ''),
                    q.get('correct_answer', ''),
                    q.get('generation_source', 'local')
                ))
            conn.commit()
            conn.close()

        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'error': f"Question generation failed: {str(e)}"}), 500
