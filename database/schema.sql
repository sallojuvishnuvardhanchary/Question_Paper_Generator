-- Schema for Syllabus-Driven Exam Question Paper Generator (CoreAlgorithm PROBLEM95)

PRAGMA foreign_keys = ON;

-- 1. Syllabi Repository
CREATE TABLE IF NOT EXISTS syllabi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'Subject Syllabus',
    parsed_text TEXT NOT NULL,
    structured_data TEXT NOT NULL, -- JSON containing extracted units, titles, topics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Question Bank (Historical / Cache / Pre-seeded)
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'Design and Analysis of Algorithms',
    unit INTEGER NOT NULL CHECK (unit BETWEEN 1 AND 10),
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    marks INTEGER NOT NULL CHECK (marks > 0),
    question_type TEXT NOT NULL CHECK (question_type IN ('MCQ', 'Short Answer', 'Long Answer', 'Descriptive', 'Programming', 'Theory', 'Bits')),
    options_json TEXT DEFAULT '',
    correct_answer TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    used_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Dynamic Generated Questions Pool (Generated directly from uploaded syllabus)
CREATE TABLE IF NOT EXISTS generated_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER,
    question_text TEXT NOT NULL,
    unit INTEGER NOT NULL,
    topic TEXT NOT NULL,
    subtopic TEXT DEFAULT '',
    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    marks INTEGER NOT NULL CHECK (marks > 0),
    question_type TEXT NOT NULL,
    options_json TEXT DEFAULT '', -- JSON array of options for MCQs
    correct_answer TEXT DEFAULT '',
    generation_source TEXT DEFAULT 'local', -- 'ai_provider' or 'local_academic_engine'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi (id) ON DELETE CASCADE
);

-- 4. Paper Configurations
CREATE TABLE IF NOT EXISTS paper_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_name TEXT,
    paper_type TEXT NOT NULL DEFAULT 'theory_bits', -- 'theory_bits', 'theory', 'mcq'
    total_marks INTEGER NOT NULL,
    structure_json TEXT NOT NULL, -- Parts, Sections, Questions per section, Marks, Choices
    difficulty_config TEXT,
    unit_config TEXT,
    topic_config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Generated Papers History
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER,
    paper_name TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'Examination',
    paper_type TEXT NOT NULL DEFAULT 'theory_bits',
    total_marks INTEGER NOT NULL,
    question_count INTEGER NOT NULL,
    algorithm_used TEXT NOT NULL,
    objective_score REAL NOT NULL,
    execution_time_ms REAL NOT NULL DEFAULT 0.0,
    pdf_path TEXT DEFAULT '',
    answer_key_pdf_path TEXT DEFAULT '',
    answer_key_json TEXT DEFAULT '',
    institution_data_json TEXT DEFAULT '',
    logo_path TEXT DEFAULT '',
    header_config_json TEXT DEFAULT '',
    metrics_json TEXT,
    constraints_json TEXT,
    status TEXT NOT NULL DEFAULT 'Valid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi (id) ON DELETE SET NULL
);

-- 6. Paper Questions with Part & Section Structure
CREATE TABLE IF NOT EXISTS paper_questions (
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
);

-- 7. Generation Decision & Execution Logs
CREATE TABLE IF NOT EXISTS generation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,
    algorithm TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    question_id INTEGER,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_syllabi_subject ON syllabi(subject);
CREATE INDEX IF NOT EXISTS idx_gen_questions_syllabus ON generated_questions(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_gen_questions_topic ON generated_questions(topic);
CREATE INDEX IF NOT EXISTS idx_questions_unit ON questions(unit);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_marks ON questions(marks);
CREATE INDEX IF NOT EXISTS idx_paper_questions_paper ON paper_questions(paper_id);
CREATE INDEX IF NOT EXISTS idx_gen_logs_paper ON generation_logs(paper_id);
