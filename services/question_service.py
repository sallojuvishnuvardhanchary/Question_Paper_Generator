"""
Question Service for CoreAlgorithm PROBLEM95.
Provides CRUD operations, database queries, full filtering, search, sorting, and usage tracking.
"""

from typing import Dict, List, Any, Optional
from database.database import get_db_connection

def get_questions(
    search: Optional[str] = None,
    unit: Optional[int] = None,
    difficulty: Optional[str] = None,
    marks: Optional[int] = None,
    topic: Optional[str] = None,
    question_type: Optional[str] = None,
    sort_by: str = 'id',
    sort_order: str = 'asc',
    page: int = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    """Retrieves paginated and filtered questions from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM questions WHERE 1=1"
    params = []

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += " AND (question_text LIKE ? OR tags LIKE ? OR topic LIKE ?)"
        params.extend([term, term, term])

    if unit is not None and str(unit).strip() != '' and str(unit) != 'all':
        query += " AND unit = ?"
        params.append(int(unit))

    if difficulty and difficulty != 'all':
        query += " AND difficulty = ?"
        params.append(difficulty)

    if marks is not None and str(marks).strip() != '' and str(marks) != 'all':
        query += " AND marks = ?"
        params.append(int(marks))

    if topic and topic != 'all':
        query += " AND topic = ?"
        params.append(topic)

    if question_type and question_type != 'all':
        query += " AND question_type = ?"
        params.append(question_type)

    # Count total matching rows
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total_count = cursor.execute(count_query, params).fetchone()[0]

    # Validate sort column
    valid_sort_cols = {'id', 'marks', 'difficulty', 'unit', 'used_count', 'created_at', 'topic', 'question_type'}
    col = sort_by if sort_by in valid_sort_cols else 'id'
    order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'

    # Custom ordering for difficulty if requested
    if col == 'difficulty':
        col_expr = "CASE difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Hard' THEN 3 ELSE 4 END"
        query += f" ORDER BY {col_expr} {order}, id ASC"
    else:
        query += f" ORDER BY {col} {order}, id ASC"

    # Pagination
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    rows = cursor.execute(query, params).fetchall()
    questions = [dict(r) for r in rows]
    conn.close()

    total_pages = max(1, (total_count + per_page - 1) // per_page)

    return {
        'questions': questions,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_question_by_id(qid: int) -> Optional[Dict[str, Any]]:
    """Fetches a single question by primary key."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_question(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new question into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions 
        (question_text, subject, unit, topic, difficulty, marks, question_type, tags, used_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['question_text'].strip(),
        data.get('subject', 'Design and Analysis of Algorithms'),
        int(data['unit']),
        data['topic'].strip(),
        data['difficulty'],
        int(data['marks']),
        data['question_type'],
        data.get('tags', '').strip(),
        int(data.get('used_count', 0))
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_question_by_id(new_id)

def update_question(qid: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing question."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE questions
        SET question_text = ?,
            subject = ?,
            unit = ?,
            topic = ?,
            difficulty = ?,
            marks = ?,
            question_type = ?,
            tags = ?,
            used_count = ?
        WHERE id = ?
    """, (
        data['question_text'].strip(),
        data.get('subject', 'Design and Analysis of Algorithms'),
        int(data['unit']),
        data['topic'].strip(),
        data['difficulty'],
        int(data['marks']),
        data['question_type'],
        data.get('tags', '').strip(),
        int(data.get('used_count', 0)),
        qid
    ))
    conn.commit()
    conn.close()
    return get_question_by_id(qid)

def delete_question(qid: int) -> bool:
    """Deletes a question by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (qid,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_all_questions_for_generation() -> List[Dict[str, Any]]:
    """Retrieves all questions from the database."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM questions ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def increment_used_count(question_ids: List[int]):
    """Increments the used_count column for generated paper questions."""
    if not question_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in question_ids)
    cursor.execute(f"UPDATE questions SET used_count = used_count + 1 WHERE id IN ({placeholders})", question_ids)
    conn.commit()
    conn.close()

def get_topics_and_units() -> Dict[str, Any]:
    """Returns distinct topics, units, and marks available in the question bank."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    topics = [r[0] for r in cursor.execute("SELECT DISTINCT topic FROM questions ORDER BY topic ASC").fetchall()]
    units = [r[0] for r in cursor.execute("SELECT DISTINCT unit FROM questions ORDER BY unit ASC").fetchall()]
    marks = [r[0] for r in cursor.execute("SELECT DISTINCT marks FROM questions ORDER BY marks ASC").fetchall()]
    q_types = [r[0] for r in cursor.execute("SELECT DISTINCT question_type FROM questions ORDER BY question_type ASC").fetchall()]
    
    conn.close()
    return {
        'topics': topics,
        'units': units,
        'marks': marks,
        'question_types': q_types
    }

def get_question_stats() -> Dict[str, Any]:
    """Calculates comprehensive database statistics for dashboards."""
    conn = get_db_connection()
    cursor = conn.cursor()

    total_questions = cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    easy_count = cursor.execute("SELECT COUNT(*) FROM questions WHERE difficulty = 'Easy'").fetchone()[0]
    medium_count = cursor.execute("SELECT COUNT(*) FROM questions WHERE difficulty = 'Medium'").fetchone()[0]
    hard_count = cursor.execute("SELECT COUNT(*) FROM questions WHERE difficulty = 'Hard'").fetchone()[0]

    unit_counts = {}
    for u in range(1, 6):
        c = cursor.execute("SELECT COUNT(*) FROM questions WHERE unit = ?", (u,)).fetchone()[0]
        unit_counts[f"Unit {u}"] = c

    topic_counts = {}
    for row in cursor.execute("SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY COUNT(*) DESC LIMIT 8").fetchall():
        topic_counts[row[0]] = row[1]

    marks_counts = {}
    for row in cursor.execute("SELECT marks, COUNT(*) FROM questions GROUP BY marks ORDER BY marks ASC").fetchall():
        marks_counts[f"{row[0]} Marks"] = row[1]

    total_used_count = cursor.execute("SELECT COUNT(*) FROM questions WHERE used_count > 0").fetchone()[0]
    available_unused = total_questions - total_used_count

    # Most and least used
    most_used = [dict(r) for r in cursor.execute("SELECT * FROM questions ORDER BY used_count DESC, id ASC LIMIT 5").fetchall()]
    least_used = [dict(r) for r in cursor.execute("SELECT * FROM questions WHERE used_count = 0 ORDER BY id ASC LIMIT 5").fetchall()]

    # Paper counts
    total_papers = cursor.execute("SELECT COUNT(*) FROM papers").fetchone()[0]

    conn.close()

    return {
        'total_questions': total_questions,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
        'unit_counts': unit_counts,
        'topic_counts': topic_counts,
        'marks_counts': marks_counts,
        'total_units': 5,
        'total_topics': len(topic_counts),
        'papers_generated': total_papers,
        'questions_used': total_used_count,
        'questions_available': available_unused,
        'most_used': most_used,
        'least_used': least_used
    }
