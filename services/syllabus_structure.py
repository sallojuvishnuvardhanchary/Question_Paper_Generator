"""
Syllabus Structure Extractor for CoreAlgorithm PROBLEM95.
Converts raw syllabus text into a structured JSON hierarchy of Subject, Units, Titles, and Topics.
Supports standard academic patterns (Units I-V, Modules 1-5, Chapters) and unstructured syllabi.
"""

import re
from typing import Dict, List, Any

ROMAN_MAP = {
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
    'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10
}

def extract_syllabus_structure(raw_text: str, default_subject: str = '') -> Dict[str, Any]:
    """
    Parses unstructured or structured syllabus text into clean JSON format:
    {
      "subject": "Design and Analysis of Algorithms",
      "units": [
        {
          "unit": 1,
          "title": "Algorithm Analysis & Divide and Conquer",
          "topics": ["Asymptotic Notations", "Recurrence Relations", "Binary Search", ...]
        }, ...
      ]
    }
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Syllabus text is empty.")

    # 1. Detect Subject Name
    subject = default_subject.strip()
    if not subject:
        subject = _detect_subject_name(lines)

    # 2. Extract Units
    units = _extract_units(lines)

    # 3. Fallback if no explicit "Unit / Module / Chapter" markers were identified
    if not units:
        units = _fallback_partition_into_units(lines)

    return {
        'subject': subject or 'Academic Course Examination',
        'units': units
    }

def _detect_subject_name(lines: List[str]) -> str:
    """Detects likely course/subject name from top header lines."""
    subject_patterns = [
        r'(?:course|subject|paper)\s*(?:title|name)?\s*[:\-]\s*(.+)',
        r'syllabus\s+for\s+(.+)',
        r'curriculum\s+for\s+(.+)',
        r'b\.?tech\s+[:\-]?\s*(.+)'
    ]

    for line in lines[:8]:
        for pat in subject_patterns:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                found = m.group(1).strip()
                # Clean trailing semester/code
                found = re.sub(r'[\(\[].*?[\)\]]', '', found).strip()
                if len(found) > 3:
                    return found

    # If first line looks like a title (not starting with Unit / Module)
    first_line = lines[0]
    if len(first_line) < 60 and not re.match(r'^(unit|module|chapter|syllabus|part)', first_line, re.IGNORECASE):
        return first_line

    return "Design and Analysis of Algorithms"

def _extract_units(lines: List[str]) -> List[Dict[str, Any]]:
    """Identifies UNIT / MODULE / CHAPTER blocks and extracts topics."""
    unit_header_pattern = re.compile(
        r'^(?:UNIT|MODULE|CHAPTER|PART)\s*[-:]?\s*([0-9]+|[IVXLCDM]+)\s*[:\-]?\s*(.*)$',
        re.IGNORECASE
    )

    unit_blocks = []
    current_unit = None
    current_lines = []

    for line in lines:
        m = unit_header_pattern.match(line)
        if m:
            if current_unit is not None:
                unit_blocks.append((current_unit['num'], current_unit['title'], current_lines))
                current_lines = []
            
            raw_num = m.group(1).lower()
            num = ROMAN_MAP.get(raw_num, int(raw_num) if raw_num.isdigit() else len(unit_blocks) + 1)
            title = m.group(2).strip()
            current_unit = {'num': num, 'title': title}
        else:
            if current_unit is not None:
                current_lines.append(line)

    if current_unit is not None:
        unit_blocks.append((current_unit['num'], current_unit['title'], current_lines))

    # Process each unit block into clean topics
    units = []
    for num, raw_title, block_lines in unit_blocks:
        topics, detected_title = _extract_topics_from_block(raw_title, block_lines)
        if not detected_title and raw_title:
            detected_title = raw_title
        units.append({
            'unit': num,
            'title': detected_title or f"Unit {num} Core Concepts",
            'topics': topics if topics else [f"Unit {num} Foundations", f"Unit {num} Advanced Methods"]
        })

    return units

def _extract_topics_from_block(header_title: str, block_lines: List[str]) -> (List[str], str):
    """Splits lines into distinct topics and derives title if missing."""
    title = header_title.strip()
    topics = []

    # Exclude common syllabus metadata lines
    ignore_patterns = [
        r'textbook', r'reference', r'hours', r'periods', r'objective', r'outcome',
        r'prerequisite', r'evaluation', r'total marks', r'credits'
    ]

    for line in block_lines:
        lower = line.lower()
        if any(re.search(pat, lower) for pat in ignore_patterns):
            continue

        # If header_title was empty and first line is clean, treat as title
        if not title and len(line) < 50 and not any(c in line for c in [',', ';', '•', '-']):
            title = line
            continue

        # Split line on separators: commas, semicolons, bullet points, or dashes
        # e.g., "Merge Sort, Quick Sort, Binary Search" -> 3 topics
        parts = re.split(r'[,;•\t\n]+|\s+-\s+|\s+\d+\.\s+', line)
        for p in parts:
            clean_p = p.strip()
            # Remove leading numbering like "1.", "1.1", "a)", "(i)", "(1)" without stripping valid words
            clean_p = re.sub(r'^(?:(?:\d+(?:\.\d+)*|[a-zA-Z]|[ivxIVX]+)[.\):\-]\s*|\([0-9a-zA-ZivxIVX]+\)\s*)', '', clean_p).strip()
            # Clean length
            if 3 <= len(clean_p) <= 80:
                if clean_p not in topics:
                    topics.append(clean_p)

    return topics, title

def _fallback_partition_into_units(lines: List[str]) -> List[Dict[str, Any]]:
    """Partitions unstructured syllabus into 3 to 5 logical units."""
    filtered_lines = [
        l for l in lines 
        if not any(k in l.lower() for k in ['textbook', 'reference', 'syllabus', 'credits', 'course outcomes'])
    ]

    chunk_size = max(1, len(filtered_lines) // 5)
    units = []

    for u_idx in range(1, 6):
        start = (u_idx - 1) * chunk_size
        end = start + chunk_size if u_idx < 5 else len(filtered_lines)
        chunk = filtered_lines[start:end]

        unit_topics = []
        for line in chunk:
            parts = re.split(r'[,;•]+|\s+-\s+', line)
            for p in parts:
                clean_p = p.strip()
                if 3 <= len(clean_p) <= 80 and clean_p not in unit_topics:
                    unit_topics.append(clean_p)

        if not unit_topics:
            unit_topics = [f"Module {u_idx} Principles", f"Module {u_idx} Implementation"]

        first_topic = unit_topics[0] if unit_topics else f"Foundations {u_idx}"
        units.append({
            'unit': u_idx,
            'title': f"Unit {u_idx}: {first_topic}",
            'topics': unit_topics[:8]
        })

    return units
