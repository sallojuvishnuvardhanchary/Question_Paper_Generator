"""
Duplicate Question & Similarity Detector Service for CoreAlgorithm PROBLEM95.
Provides exact text normalization comparison and token-set Jaccard similarity detection.
"""

import re
from typing import Dict, List, Any, Tuple

def normalize_text(text: str) -> str:
    """Normalizes string by lowercasing and removing punctuation and excess whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())

def get_tokens(text: str) -> set:
    """Extracts informative word tokens excluding common English stop words."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'is', 'are', 'was', 'were', 'what', 'how', 'why', 'explain', 'describe',
        'discuss', 'define', 'write', 'illustrate', 'using', 'example', 'with'
    }
    normalized = normalize_text(text)
    tokens = set(normalized.split()) - stop_words
    return tokens

def calculate_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard token similarity coefficient between two question strings."""
    tokens1 = get_tokens(text1)
    tokens2 = get_tokens(text2)

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return intersection / union if union > 0 else 0.0

def detect_duplicates_in_pool(questions: List[Dict[str, Any]], similarity_threshold: float = 0.70) -> Dict[str, Any]:
    """
    Scans a list of questions for exact duplicates and near-duplicate / highly similar questions.
    Returns:
      {
        "exact_duplicates": List[Tuple[int, int]],
        "similar_pairs": List[Dict],
        "has_duplicates": bool
      }
    """
    exact_duplicates = []
    similar_pairs = []
    normalized_map = {}

    for i, q1 in enumerate(questions):
        q1_text = q1.get('question_text', '')
        norm1 = normalize_text(q1_text)

        if norm1 in normalized_map:
            prev_idx = normalized_map[norm1]
            exact_duplicates.append({
                'q1_id': questions[prev_idx].get('id', prev_idx),
                'q2_id': q1.get('id', i),
                'text': q1_text
            })
        else:
            normalized_map[norm1] = i

        # Check similarity against previously seen questions
        for j in range(i + 1, len(questions)):
            q2 = questions[j]
            q2_text = q2.get('question_text', '')
            score = calculate_similarity(q1_text, q2_text)

            if score >= similarity_threshold:
                similar_pairs.append({
                    'q1_id': q1.get('id', i),
                    'q2_id': q2.get('id', j),
                    'q1_text': q1_text[:60] + '...',
                    'q2_text': q2_text[:60] + '...',
                    'similarity': round(score * 100, 1)
                })

    return {
        'exact_duplicates': exact_duplicates,
        'exact_count': len(exact_duplicates),
        'similar_pairs': similar_pairs,
        'similar_count': len(similar_pairs),
        'is_clean': len(exact_duplicates) == 0 and len(similar_pairs) == 0
    }
