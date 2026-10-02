"""
Objective Function and Candidate Scoring Module for CoreAlgorithm PROBLEM95.
Provides transparent, normalized (0-100) objective evaluation and candidate selection heuristics.
"""

from typing import Dict, List, Any

SCORE_WEIGHTS = {
    'difficulty': 25.0,
    'unit': 25.0,
    'topic': 20.0,
    'marks_fit': 15.0,
    'novelty': 15.0
}

DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']

def calculate_objective_score(selected_questions: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a transparent, normalized 0 - 100 objective score for a given set of questions
    against the target configuration.

    Components:
    1. Difficulty Balance (25%): Proximity to target difficulty distribution.
    2. Unit Coverage (25%): Proximity to target unit distribution.
    3. Topic Coverage (20%): Percentage of required topics satisfied.
    4. Marks Accuracy (15%): Exactness of total marks target match.
    5. Novelty & Diversity (15%): Penalizes previously used questions and rewards diverse question types.
    """
    if not selected_questions:
        return {
            'total_score': 0.0,
            'breakdown': {
                'difficulty': 0.0,
                'unit': 0.0,
                'topic': 0.0,
                'marks_fit': 0.0,
                'novelty': 0.0
            },
            'details': {'error': 'No questions selected'}
        }

    total_count = len(selected_questions)
    target_count = config.get('question_count', 10)
    target_marks = config.get('total_marks', 100)
    target_diff_ratio = config.get('difficulty_ratio', {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20})
    target_unit_ratio = config.get('unit_ratio', {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20})
    required_topics = set(config.get('required_topics', []))

    # 1. Difficulty Balance Score (Max 25)
    diff_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
    for q in selected_questions:
        diff_counts[q.get('difficulty', 'Medium')] = diff_counts.get(q.get('difficulty', 'Medium'), 0) + 1
    
    diff_error = 0.0
    for d in DIFFICULTY_LEVELS:
        actual_ratio = diff_counts.get(d, 0) / max(total_count, 1)
        expected_ratio = target_diff_ratio.get(d, 0.33)
        diff_error += abs(actual_ratio - expected_ratio)
    # diff_error in [0, 2], normalized: 1 - (diff_error / 2)
    diff_balance_factor = max(0.0, 1.0 - (diff_error / 2.0))
    difficulty_score = diff_balance_factor * SCORE_WEIGHTS['difficulty']

    # 2. Unit Coverage Score (Max 25)
    unit_counts = {u: 0 for u in range(1, 6)}
    for q in selected_questions:
        u = q.get('unit', 1)
        unit_counts[u] = unit_counts.get(u, 0) + 1

    unit_error = 0.0
    for u in range(1, 6):
        actual_ratio = unit_counts.get(u, 0) / max(total_count, 1)
        expected_ratio = target_unit_ratio.get(u, 0.20)
        unit_error += abs(actual_ratio - expected_ratio)
    unit_balance_factor = max(0.0, 1.0 - (unit_error / 2.0))
    unit_score = unit_balance_factor * SCORE_WEIGHTS['unit']

    # 3. Topic Coverage Score (Max 20)
    covered_topics = set(q.get('topic') for q in selected_questions if q.get('topic'))
    if required_topics:
        matched_required = len(required_topics.intersection(covered_topics))
        topic_ratio = matched_required / len(required_topics)
    else:
        # If no specific required topics, reward variety (unique topics count)
        topic_ratio = min(1.0, len(covered_topics) / max(5, target_count * 0.6))
    topic_score = topic_ratio * SCORE_WEIGHTS['topic']

    # 4. Marks Accuracy Score (Max 15)
    actual_marks = sum(q.get('marks', 0) for q in selected_questions)
    marks_diff = abs(actual_marks - target_marks)
    if target_marks > 0:
        marks_accuracy_factor = max(0.0, 1.0 - (marks_diff / target_marks))
    else:
        marks_accuracy_factor = 1.0 if actual_marks == 0 else 0.0
    marks_score = marks_accuracy_factor * SCORE_WEIGHTS['marks_fit']

    # 5. Novelty & Diversity Score (Max 15)
    # Penalize used questions
    total_usage = sum(q.get('used_count', 0) for q in selected_questions)
    avg_usage = total_usage / max(total_count, 1)
    # 0 usage = 1.0, 1 usage = 0.8, 3+ usage <= 0.2
    novelty_factor = max(0.0, 1.0 - (avg_usage * 0.25))

    # Diversity of question types
    types = set(q.get('question_type') for q in selected_questions if q.get('question_type'))
    type_diversity_factor = min(1.0, len(types) / 3.0)

    novelty_diversity_score = (0.7 * novelty_factor + 0.3 * type_diversity_factor) * SCORE_WEIGHTS['novelty']

    total_score = round(difficulty_score + unit_score + topic_score + marks_score + novelty_diversity_score, 2)

    return {
        'total_score': total_score,
        'breakdown': {
            'difficulty': round(difficulty_score, 2),
            'unit': round(unit_score, 2),
            'topic': round(topic_score, 2),
            'marks_fit': round(marks_score, 2),
            'novelty': round(novelty_diversity_score, 2)
        },
        'details': {
            'actual_marks': actual_marks,
            'target_marks': target_marks,
            'marks_diff': marks_diff,
            'diff_counts': diff_counts,
            'unit_counts': unit_counts,
            'unique_topics': list(covered_topics),
            'total_usage': total_usage,
            'types_present': list(types)
        }
    }


def score_candidate_for_greedy(candidate: Dict[str, Any], current_state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes the greedy selection score for a single candidate question.

    Selection Score = Difficulty Match + Unit Deficit + Topic Need + Marks Fit + Novelty Bonus
    Returns:
        {
            'score': float,
            'reasons': List[str],
            'breakdown': Dict[str, float]
        }
    """
    reasons = []
    c_marks = candidate.get('marks', 0)
    c_diff = candidate.get('difficulty', 'Medium')
    c_unit = candidate.get('unit', 1)
    c_topic = candidate.get('topic', '')
    c_used = candidate.get('used_count', 0)

    rem_marks = current_state['remaining_marks']
    rem_count = current_state['remaining_count']
    current_units = current_state['unit_counts']
    current_diff = current_state['difficulty_counts']
    covered_topics = current_state['covered_topics']

    target_count = config.get('question_count', 10)
    target_diff_ratio = config.get('difficulty_ratio', {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20})
    target_unit_ratio = config.get('unit_ratio', {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20})
    required_topics = set(config.get('required_topics', []))

    # 1. Marks Fit Score (0 to 30)
    # Feasibility check: question marks cannot exceed remaining marks
    if c_marks > rem_marks:
        return {
            'score': -1.0,
            'reasons': [f'Exceeds remaining marks ({c_marks} > {rem_marks})'],
            'breakdown': {'marks_fit': -100}
        }
    
    # If this is the last question, we need an exact marks match!
    if rem_count == 1:
        if c_marks == rem_marks:
            marks_fit_score = 35.0
            reasons.append(f'Exact final marks match ({c_marks} marks matches remaining {rem_marks})')
        else:
            marks_fit_score = 0.0
            reasons.append(f'Final question does not meet remaining marks ({c_marks} != {rem_marks})')
    else:
        # Ideal average marks per remaining question
        avg_target_marks = rem_marks / max(rem_count, 1)
        deviation = abs(c_marks - avg_target_marks)
        marks_fit_score = max(5.0, 30.0 - (deviation * 3.0))
        reasons.append(f'Fits remaining {rem_marks} marks (deviation {deviation:.1f} from ideal {avg_target_marks:.1f})')

    # 2. Difficulty Need Score (0 to 25)
    needed_diff_count = target_diff_ratio.get(c_diff, 0.33) * target_count
    current_diff_count = current_diff.get(c_diff, 0)
    diff_deficit = needed_diff_count - current_diff_count
    if diff_deficit > 0:
        diff_score = min(25.0, 15.0 + diff_deficit * 5.0)
        reasons.append(f'Needed {c_diff} difficulty (deficit: {diff_deficit:.1f})')
    else:
        diff_score = max(2.0, 10.0 + diff_deficit * 4.0)
        reasons.append(f'{c_diff} quota already met or exceeded')

    # 3. Unit Deficit Score (0 to 25)
    needed_unit_count = target_unit_ratio.get(c_unit, 0.20) * target_count
    current_unit_count = current_units.get(c_unit, 0)
    unit_deficit = needed_unit_count - current_unit_count
    if unit_deficit > 0:
        unit_score = min(25.0, 15.0 + unit_deficit * 5.0)
        reasons.append(f'Unit {c_unit} coverage needed (deficit: {unit_deficit:.1f})')
    else:
        unit_score = max(2.0, 10.0 + unit_deficit * 4.0)
        reasons.append(f'Unit {c_unit} quota already satisfied')

    # 4. Topic Need Score (0 to 20)
    if c_topic in required_topics and c_topic not in covered_topics:
        topic_score = 20.0
        reasons.append(f'Mandatory topic "{c_topic}" not yet represented')
    elif c_topic not in covered_topics:
        topic_score = 14.0
        reasons.append(f'Introduces new topic "{c_topic}"')
    else:
        topic_score = 6.0
        reasons.append(f'Topic "{c_topic}" already covered')

    # 5. Novelty Bonus (0 to 15)
    if c_used == 0:
        novelty_score = 15.0
        reasons.append('Never used previously (100% novelty)')
    elif c_used == 1:
        novelty_score = 9.0
        reasons.append('Used only once previously')
    else:
        novelty_score = max(1.0, 15.0 - (c_used * 4.0))
        reasons.append(f'Repeated {c_used} times (penalized)')

    total_score = round(marks_fit_score + diff_score + unit_score + topic_score + novelty_score, 2)

    return {
        'score': total_score,
        'reasons': reasons,
        'breakdown': {
            'marks_fit': round(marks_fit_score, 2),
            'difficulty': round(diff_score, 2),
            'unit': round(unit_score, 2),
            'topic': round(topic_score, 2),
            'novelty': round(novelty_score, 2)
        }
    }
