"""
Analytics API Routes for CoreAlgorithm PROBLEM95.
Provides dashboard statistics, distribution metrics, usage frequency,
and system maintenance endpoints.
"""

from flask import Blueprint, jsonify
from database.database import get_db_connection
from database.seed import seed_database
from services.question_service import get_question_stats

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')

@analytics_bp.route('/analytics', methods=['GET'])
def get_analytics():
    # Fetch base question stats
    stats = get_question_stats()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Paper generation metrics
    total_papers = cursor.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    avg_score_row = cursor.execute("SELECT AVG(objective_score) FROM papers").fetchone()
    avg_score = round(avg_score_row[0], 2) if avg_score_row and avg_score_row[0] is not None else 0.0

    # Algorithm usage counts
    algo_counts = {}
    for r in cursor.execute("SELECT algorithm_used, COUNT(*) FROM papers GROUP BY algorithm_used").fetchall():
        algo_counts[r[0]] = r[1]

    # Recent papers
    recent_papers = [dict(r) for r in cursor.execute("""
        SELECT id, paper_name, total_marks, question_count, algorithm_used, objective_score, status, created_at 
        FROM papers 
        ORDER BY created_at DESC 
        LIMIT 6
    """).fetchall()]

    # Score distribution of generated papers (e.g. 70-80, 80-90, 90-100)
    score_buckets = {'< 70': 0, '70 - 79': 0, '80 - 89': 0, '90 - 100': 0}
    for r in cursor.execute("SELECT objective_score FROM papers").fetchall():
        sc = r[0]
        if sc < 70:
            score_buckets['< 70'] += 1
        elif sc < 80:
            score_buckets['70 - 79'] += 1
        elif sc < 90:
            score_buckets['80 - 89'] += 1
        else:
            score_buckets['90 - 100'] += 1

    conn.close()

    return jsonify({
        'success': True,
        'question_stats': stats,
        'paper_stats': {
            'total_papers': total_papers,
            'average_objective_score': avg_score,
            'algorithm_distribution': algo_counts,
            'recent_papers': recent_papers,
            'score_buckets': score_buckets
        }
    })

@analytics_bp.route('/system/reset-seed', methods=['POST'])
def reset_database():
    try:
        from database.database import init_db
        init_db(force=True)
        seed_database()
        return jsonify({'success': True, 'message': 'Database successfully reset and re-seeded with 80 DAA questions.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to reset database: {str(e)}'}), 500
