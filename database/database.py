import sqlite3
import os
from config import Config

def get_db_connection():
    """Returns a SQLite connection with timeout and foreign keys configured."""
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force=False):
    """Initializes the database schema. If force=True, recreates tables."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    conn.execute("PRAGMA journal_mode = WAL")
    cursor = conn.cursor()
    
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    if force:
        cursor.execute("DROP TABLE IF EXISTS generation_logs")
        cursor.execute("DROP TABLE IF EXISTS paper_questions")
        cursor.execute("DROP TABLE IF EXISTS papers")
        cursor.execute("DROP TABLE IF EXISTS paper_configurations")
        cursor.execute("DROP TABLE IF EXISTS generated_questions")
        cursor.execute("DROP TABLE IF EXISTS syllabi")
        cursor.execute("DROP TABLE IF EXISTS questions")
        conn.commit()
    
    cursor.executescript(schema_sql)
    conn.commit()

    # Automatic safe migration for existing databases:
    # Add new columns if table already existed from previous version
    try:
        # Check papers table columns
        cols = [c[1] for c in cursor.execute("PRAGMA table_info(papers)").fetchall()]
        if 'syllabus_id' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN syllabus_id INTEGER")
        if 'paper_type' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN paper_type TEXT DEFAULT 'theory_bits'")
        if 'pdf_path' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN pdf_path TEXT DEFAULT ''")
        if 'answer_key_pdf_path' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN answer_key_pdf_path TEXT DEFAULT ''")
        if 'answer_key_json' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN answer_key_json TEXT DEFAULT ''")
        if 'institution_data_json' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN institution_data_json TEXT DEFAULT ''")
        if 'logo_path' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN logo_path TEXT DEFAULT ''")
        if 'header_config_json' not in cols:
            cursor.execute("ALTER TABLE papers ADD COLUMN header_config_json TEXT DEFAULT ''")
        
        # Check questions table columns
        q_cols = [c[1] for c in cursor.execute("PRAGMA table_info(questions)").fetchall()]
        if 'options_json' not in q_cols:
            cursor.execute("ALTER TABLE questions ADD COLUMN options_json TEXT DEFAULT ''")
        if 'correct_answer' not in q_cols:
            cursor.execute("ALTER TABLE questions ADD COLUMN correct_answer TEXT DEFAULT ''")

        # Check paper_questions table foreign keys:
        # If it still references questions(id), migrate it so syllabus-generated questions can be stored
        fk_list = cursor.execute("PRAGMA foreign_key_list(paper_questions)").fetchall()
        has_questions_fk = any(fk[2] == 'questions' for fk in fk_list)
        if has_questions_fk:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paper_questions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id INTEGER NOT NULL,
                    question_id INTEGER,
                    part_name TEXT DEFAULT 'Part A',
                    section_name TEXT DEFAULT '',
                    question_number TEXT DEFAULT '1',
                    choice_group TEXT DEFAULT '',
                    is_choice INTEGER DEFAULT 0,
                    question_text TEXT NOT NULL,
                    marks INTEGER NOT NULL,
                    unit INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    options_json TEXT DEFAULT '',
                    correct_answer TEXT DEFAULT '',
                    selection_order INTEGER NOT NULL,
                    selection_reason TEXT NOT NULL,
                    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                INSERT INTO paper_questions_new (
                    id, paper_id, question_id, part_name, section_name, question_number,
                    choice_group, is_choice, question_text, marks, unit, topic,
                    difficulty, question_type, options_json, correct_answer,
                    selection_order, selection_reason
                )
                SELECT 
                    id, paper_id, question_id, part_name, section_name, question_number,
                    choice_group, is_choice, question_text, marks, unit, topic,
                    difficulty, question_type, options_json, correct_answer,
                    selection_order, selection_reason
                FROM paper_questions
            """)
            cursor.execute("DROP TABLE paper_questions")
            cursor.execute("ALTER TABLE paper_questions_new RENAME TO paper_questions")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_questions_paper ON paper_questions(paper_id)")
            cursor.execute("PRAGMA foreign_keys = ON")

        conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

    conn.close()

def is_db_seeded():
    """Checks if questions table contains rows."""
    if not os.path.exists(Config.DATABASE_PATH):
        return False
    try:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False
