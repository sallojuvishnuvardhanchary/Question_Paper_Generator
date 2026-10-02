"""
PDF Generation & Download API Routes for CoreAlgorithm PROBLEM95.
Provides endpoints for downloading student question papers, answer keys,
and regenerating PDFs with custom institutional metadata.
"""

import os
from flask import Blueprint, request, jsonify, send_file
from config import Config
from services.paper_generator import get_paper_by_id
from services.pdf_generator import generate_exam_pdf, generate_answer_key_pdf

pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/paper')

@pdf_bp.route('/<int:pid>/download', methods=['GET'])
def download_student_paper(pid):
    paper = get_paper_by_id(pid)
    if not paper:
        return jsonify({'success': False, 'error': f"Paper ID {pid} not found."}), 404

    filename = paper.get('pdf_path') or f"Question_Paper_{pid}.pdf"
    file_path = os.path.join(Config.GENERATED_PAPERS_FOLDER, filename)

    # If file doesn't exist on disk, synthesize it on the fly
    if not os.path.exists(file_path):
        inst_data = paper.get('constraints', {}).get('institution_data') or {}
        file_path = generate_exam_pdf(paper, institution_data=inst_data, output_filename=filename)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@pdf_bp.route('/<int:pid>/download-key', methods=['GET'])
def download_answer_key(pid):
    paper = get_paper_by_id(pid)
    if not paper:
        return jsonify({'success': False, 'error': f"Paper ID {pid} not found."}), 404

    filename = paper.get('answer_key_pdf_path') or f"Answer_Key_{pid}.pdf"
    file_path = os.path.join(Config.GENERATED_PAPERS_FOLDER, filename)

    if not os.path.exists(file_path):
        inst_data = paper.get('constraints', {}).get('institution_data') or {}
        file_path = generate_answer_key_pdf(paper, institution_data=inst_data, output_filename=filename)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@pdf_bp.route('/<int:pid>/pdf', methods=['POST'])
def regenerate_pdf(pid):
    paper = get_paper_by_id(pid)
    if not paper:
        return jsonify({'success': False, 'error': f"Paper ID {pid} not found."}), 404

    inst_data = request.get_json() or {}
    filename = f"Question_Paper_{pid}.pdf"
    file_path = generate_exam_pdf(paper, institution_data=inst_data, output_filename=filename)

    return jsonify({
        'success': True,
        'message': 'PDF generated successfully.',
        'pdf_url': f"/api/paper/{pid}/download"
    })
