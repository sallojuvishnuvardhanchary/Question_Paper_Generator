"""
Exam Question Paper Generator Web Application
Problem ID: CoreAlgorithm PROBLEM95
Domain: Design and Analysis of Algorithms (DAA)
Main Application Server (Flask)
"""

import os
from flask import Flask, render_template, send_from_directory, jsonify
from config import Config
from database.database import init_db, is_db_seeded
from database.seed import seed_database
from routes.questions import questions_bp
from routes.papers import papers_bp
from routes.algorithms import algorithms_bp
from routes.analytics import analytics_bp
from routes.syllabus import syllabus_bp
from routes.pdf import pdf_bp

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Initialize DB & Seed if empty
    with app.app_context():
        if not is_db_seeded():
            print("Database not detected or empty. Initializing and seeding...")
            init_db(force=False)
            seed_database()
        else:
            print("Database verified with existing questions.")

    # Register Blueprints
    app.register_blueprint(questions_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(syllabus_bp)
    app.register_blueprint(pdf_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/uploads/logos/<path:filename>')
    def uploaded_logo(filename):
        return send_from_directory(Config.LOGO_UPLOAD_FOLDER, filename)

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'online', 'problem': 'CoreAlgorithm PROBLEM95', 'version': '1.0.0'})

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found', 'status': 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'status': 500}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"   Exam Question Paper Generator (CoreAlgorithm PROBLEM95) ")
    print(f"   Listening on: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
