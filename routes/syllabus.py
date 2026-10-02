"""
Syllabus Management API Routes for CoreAlgorithm PROBLEM95.
Provides file upload (PDF, DOCX, TXT), text extraction, structure extraction,
syllabus review, editing, and history retrieval.
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from config import Config
from database.database import get_db_connection
from services.syllabus_parser import parse_uploaded_syllabus
from services.syllabus_structure import extract_syllabus_structure

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/api/syllabus')

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@syllabus_bp.route('/upload', methods=['POST'])
def upload_syllabus():
    if 'file' not in request.files:
        # Check if raw text was sent instead of a file
        data = request.get_json(silent=True)
        if data and data.get('raw_text'):
            raw_text = data.get('raw_text').strip()
            subject_name = data.get('subject', 'Uploaded Syllabus')
            structure = extract_syllabus_structure(raw_text, default_subject=subject_name)
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO syllabi (filename, subject, parsed_text, structured_data)
                VALUES (?, ?, ?, ?)
            """, ('manual_entry.txt', structure['subject'], raw_text, json.dumps(structure)))
            s_id = cur.lastrowid
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'syllabus_id': s_id,
                'filename': 'manual_entry.txt',
                'subject': structure['subject'],
                'parsed_text': raw_text,
                'structured_data': structure
            })
        return jsonify({'success': False, 'error': 'No file or syllabus text provided.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f"Unsupported format. Allowed formats are: {', '.join(Config.ALLOWED_EXTENSIONS).upper()}"
        }), 400

    filename = secure_filename(file.filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(temp_path)

    try:
        # 1. Parse text from document (PDF / DOCX / TXT)
        parsed_text = parse_uploaded_syllabus(temp_path, filename)
        
        # 2. Extract structured Units and Topics
        structured_data = extract_syllabus_structure(parsed_text)

        # 3. Store in SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO syllabi (filename, subject, parsed_text, structured_data)
            VALUES (?, ?, ?, ?)
        """, (
            filename,
            structured_data['subject'],
            parsed_text,
            json.dumps(structured_data)
        ))
        syllabus_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'syllabus_id': syllabus_id,
            'filename': filename,
            'subject': structured_data['subject'],
            'parsed_text': parsed_text,
            'structured_data': structured_data,
            'message': f"Syllabus '{filename}' uploaded and parsed successfully!"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f"Failed to parse syllabus: {str(e)}"}), 400
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@syllabus_bp.route('', methods=['GET'])
def list_syllabi():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, filename, subject, created_at FROM syllabi ORDER BY created_at DESC").fetchall()
    
    # Also get counts of generated papers per syllabus
    syllabi = []
    for r in rows:
        s_dict = dict(r)
        paper_count = conn.execute("SELECT COUNT(*) FROM papers WHERE syllabus_id = ?", (s_dict['id'],)).fetchone()[0]
        s_dict['papers_generated'] = paper_count
        syllabi.append(s_dict)

    conn.close()
    return jsonify({'success': True, 'syllabi': syllabi})

@syllabus_bp.route('/<int:sid>', methods=['GET'])
def get_syllabus(sid):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM syllabi WHERE id = ?", (sid,)).fetchone()
    conn.close()

    if not row:
        return jsonify({'success': False, 'error': f"Syllabus ID {sid} not found."}), 404

    s_dict = dict(row)
    if s_dict.get('structured_data'):
        try:
            s_dict['structured_data'] = json.loads(s_dict['structured_data'])
        except Exception:
            s_dict['structured_data'] = {}

    return jsonify({'success': True, 'syllabus': s_dict})

@syllabus_bp.route('/<int:sid>', methods=['PUT'])
def update_syllabus(sid):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM syllabi WHERE id = ?", (sid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'error': f"Syllabus ID {sid} not found."}), 404

    data = request.get_json() or {}
    new_text = data.get('parsed_text')
    new_struct = data.get('structured_data')
    new_subject = data.get('subject')

    struct_str = json.dumps(new_struct) if isinstance(new_struct, dict) else row['structured_data']
    text_to_save = new_text if new_text else row['parsed_text']
    subject_to_save = new_subject if new_subject else row['subject']

    conn.execute("""
        UPDATE syllabi 
        SET subject = ?, parsed_text = ?, structured_data = ?
        WHERE id = ?
    """, (subject_to_save, text_to_save, struct_str, sid))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Syllabus updated successfully.'})

@syllabus_bp.route('/<int:sid>', methods=['DELETE'])
def delete_syllabus(sid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM syllabi WHERE id = ?", (sid,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        return jsonify({'success': False, 'error': f"Syllabus ID {sid} not found."}), 404
    return jsonify({'success': True, 'message': f"Syllabus #{sid} deleted successfully."})
