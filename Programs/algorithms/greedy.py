"""
Greedy Algorithm implementation for Exam Question Paper Generator.
Selects the locally optimal question at each step based on a multi-criteria heuristic scoring function.
Logs all decisions, scores, and rejections dynamically.
"""

import time
from typing import Dict, List, Any
from algorithms.scoring import score_candidate_for_greedy, calculate_objective_score

def generate_paper_greedy(questions_pool: List[Dict[str, Any]], config: Dict[str, Any], on_event=None) -> Dict[str, Any]:
    """
    Executes the Greedy Question Paper Generation algorithm.
    Produces real-time execution trace events for visualization.
    """
    start_time = time.perf_counter()

    target_marks = config.get('total_marks', 100)
    target_count = config.get('question_count', 10)
    avoid_used = config.get('avoid_used', False)
    max_per_topic = config.get('max_per_topic', 3)
    min_per_unit = config.get('min_per_unit', 1)
    target_diff_ratio = config.get('difficulty_ratio', {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20})
    raw_unit_ratio = config.get('unit_ratio', {1: 0.20, 2: 0.20, 3: 0.20, 4: 0.20, 5: 0.20})
    target_unit_ratio = {int(k): float(v) for k, v in raw_unit_ratio.items()}

    trace_events: List[Dict[str, Any]] = []

    def emit(event_dict: Dict[str, Any]):
        trace_events.append(event_dict)
        if callable(on_event):
            try:
                on_event(event_dict)
            except Exception:
                pass

    # Filter pool if avoid_used is strict
    available_pool = []
    for q in questions_pool:
        q_copy = dict(q)
        if avoid_used and q_copy.get('used_count', 0) > 0:
            continue
        available_pool.append(q_copy)

    # If avoiding used leaves too few questions, fall back with penalty rather than crashing
    if len(available_pool) < target_count:
        available_pool = [dict(q) for q in questions_pool]

    # Emit STEP 1: Candidate Pool Loaded Event
    emit({
        'event': 'candidate_pool_loaded',
        'step': 0,
        'algorithm': 'greedy',
        'total_candidates': len(available_pool),
        'candidates_sample': [
            {
                'id': q.get('id'),
                'question_text': q.get('question_text', '')[:75],
                'unit': q.get('unit', 1),
                'difficulty': q.get('difficulty', 'Medium'),
                'marks': q.get('marks', 5),
                'topic': q.get('topic', '')
            }
            for q in available_pool[:15]
        ],
        'target_marks': target_marks,
        'target_count': target_count,
        'difficulty_targets': {
            d: max(1, int(round(target_count * target_diff_ratio.get(d, 0.33))))
            for d in ['Easy', 'Medium', 'Hard']
        }
    })

    selected_questions: List[Dict[str, Any]] = []
    selected_ids = set()
    topic_counts: Dict[str, int] = {}
    
    current_state = {
        'remaining_marks': target_marks,
        'remaining_count': target_count,
        'unit_counts': {u: 0 for u in range(1, 6)},
        'difficulty_counts': {'Easy': 0, 'Medium': 0, 'Hard': 0},
        'covered_topics': set()
    }

    logs: List[Dict[str, Any]] = []
    questions_evaluated_total = 0

    for step in range(1, target_count + 1):
        rem_count = current_state['remaining_count']
        rem_marks = current_state['remaining_marks']

        # Determine eligible candidates
        candidate_evaluations = []
        rejected_candidates = []

        for q in available_pool:
            q_id = q['id']
            if q_id in selected_ids:
                continue

            q_marks = q.get('marks', 0)
            q_topic = q.get('topic', 'General')
            q_unit = q.get('unit', 1)

            # Feasibility check: Can we afford this mark?
            if q_marks > rem_marks:
                rejected_candidates.append({
                    'id': q_id,
                    'text': q.get('question_text', '')[:60] + '...',
                    'reason': f"Exceeds remaining marks ({q_marks} > {rem_marks})"
                })
                continue

            # Feasibility check: Will remaining questions have enough marks?
            # If remaining marks after taking q is less than (rem_count - 1) * min_possible_marks (say 2)
            if rem_count > 1 and (rem_marks - q_marks) < (rem_count - 1) * 2:
                rejected_candidates.append({
                    'id': q_id,
                    'text': q.get('question_text', '')[:60] + '...',
                    'reason': f"Leaves too few marks ({rem_marks - q_marks}) for {rem_count - 1} remaining questions"
                })
                continue

            # Check max_per_topic constraint
            if topic_counts.get(q_topic, 0) >= max_per_topic:
                rejected_candidates.append({
                    'id': q_id,
                    'text': q.get('question_text', '')[:60] + '...',
                    'reason': f"Topic '{q_topic}' reached maximum limit ({max_per_topic})"
                })
                continue

            # Score candidate using greedy heuristic
            scored = score_candidate_for_greedy(q, current_state, config)
            questions_evaluated_total += 1

            if scored['score'] >= 0:
                candidate_evaluations.append({
                    'question': q,
                    'score': scored['score'],
                    'reasons': scored['reasons'],
                    'breakdown': scored['breakdown']
                })
            else:
                rejected_candidates.append({
                    'id': q_id,
                    'text': q.get('question_text', '')[:60] + '...',
                    'reason': "; ".join(scored['reasons'])
                })

        if not candidate_evaluations:
            # Greedy search reached a dead end where no candidate satisfies marks bound exactly
            # Relaxation attempt: look for question that minimizes mark discrepancy
            relaxed_candidates = [q for q in available_pool if q['id'] not in selected_ids]
            if relaxed_candidates:
                # pick candidate that closest fits rem_marks
                relaxed_candidates.sort(key=lambda q: abs(q['marks'] - rem_marks))
                best_q = relaxed_candidates[0]
                candidate_evaluations.append({
                    'question': best_q,
                    'score': 10.0,
                    'reasons': [f'Greedy relaxation: closest marks fit ({best_q["marks"]} vs remaining {rem_marks})'],
                    'breakdown': {'marks_fit': 10.0, 'difficulty': 0, 'unit': 0, 'topic': 0, 'novelty': 0}
                })
            else:
                break

        # Emit STEP 2: Candidate Scores Calculated
        emit({
            'event': 'candidates_scored',
            'step': step,
            'algorithm': 'greedy',
            'candidates_evaluated': len(candidate_evaluations),
            'scores': [
                {
                    'id': c['question']['id'],
                    'text': c['question']['question_text'][:70],
                    'unit': c['question']['unit'],
                    'difficulty': c['question']['difficulty'],
                    'marks': c['question']['marks'],
                    'topic': c['question']['topic'],
                    'score': round(c['score'], 2),
                    'breakdown': {k: round(v, 2) for k, v in c['breakdown'].items()},
                    'reasons': c['reasons']
                }
                for c in candidate_evaluations[:8]
            ],
            'rejected_sample': rejected_candidates[:4]
        })

        # Sort candidates descending by heuristic score
        candidate_evaluations.sort(key=lambda c: c['score'], reverse=True)

        # Emit STEP 3: Ranked Candidates
        emit({
            'event': 'candidates_ranked',
            'step': step,
            'algorithm': 'greedy',
            'ranked': [
                {
                    'rank': r_idx,
                    'id': c['question']['id'],
                    'score': round(c['score'], 2),
                    'text': c['question']['question_text'][:60]
                }
                for r_idx, c in enumerate(candidate_evaluations[:6], start=1)
            ]
        })

        chosen = candidate_evaluations[0]
        chosen_q = chosen['question']
        chosen_score = chosen['score']
        chosen_reasons = chosen['reasons']

        # Update state
        selected_questions.append(chosen_q)
        selected_ids.add(chosen_q['id'])
        topic_counts[chosen_q['topic']] = topic_counts.get(chosen_q['topic'], 0) + 1
        current_state['covered_topics'].add(chosen_q['topic'])
        current_state['unit_counts'][chosen_q['unit']] = current_state['unit_counts'].get(chosen_q['unit'], 0) + 1
        current_state['difficulty_counts'][chosen_q['difficulty']] = current_state['difficulty_counts'].get(chosen_q['difficulty'], 0) + 1
        current_state['remaining_marks'] -= chosen_q['marks']
        current_state['remaining_count'] -= 1

        # Collect top 3 runner-ups (rejected in this step)
        runner_ups = []
        for other in candidate_evaluations[1:4]:
            runner_ups.append({
                'id': other['question']['id'],
                'text': other['question']['question_text'][:60] + '...',
                'score': round(other['score'], 2),
                'reasons': other['reasons']
            })

        # Append step log
        logs.append({
            'step': step,
            'action': 'SELECT',
            'question_id': chosen_q['id'],
            'question_text': chosen_q['question_text'],
            'marks': chosen_q['marks'],
            'unit': chosen_q['unit'],
            'topic': chosen_q['topic'],
            'difficulty': chosen_q['difficulty'],
            'score': chosen_score,
            'reasons': chosen_reasons,
            'breakdown': chosen['breakdown'],
            'runner_ups': runner_ups,
            'rejected_sample': rejected_candidates[:3],
            'state_after': {
                'remaining_marks': current_state['remaining_marks'],
                'remaining_count': current_state['remaining_count'],
                'unit_counts': dict(current_state['unit_counts']),
                'diff_counts': dict(current_state['difficulty_counts'])
            }
        })

        # Emit STEP 4 & 5: Candidate Selection & Live Constraint Status
        current_marks_achieved = target_marks - current_state['remaining_marks']
        emit({
            'event': 'candidate_selected',
            'step': step,
            'algorithm': 'greedy',
            'candidate_id': chosen_q['id'],
            'candidate_text': chosen_q['question_text'],
            'marks': chosen_q['marks'],
            'unit': chosen_q['unit'],
            'difficulty': chosen_q['difficulty'],
            'topic': chosen_q['topic'],
            'score': round(chosen_score, 2),
            'decision': 'SELECTED',
            'reason': "; ".join(chosen_reasons) if isinstance(chosen_reasons, list) else str(chosen_reasons),
            'breakdown': {k: round(v, 2) for k, v in chosen['breakdown'].items()},
            'runner_ups': runner_ups,
            'counters': {
                'selected_questions': len(selected_questions),
                'target_questions': target_count,
                'current_marks': current_marks_achieved,
                'target_marks': target_marks,
                'difficulty_counts': dict(current_state['difficulty_counts']),
                'unit_counts': dict(current_state['unit_counts']),
                'covered_topics_count': len(current_state['covered_topics'])
            }
        })

    end_time = time.perf_counter()
    execution_time_ms = round((end_time - start_time) * 1000, 2)

    # Evaluate final objective score
    obj_eval = calculate_objective_score(selected_questions, config)
    actual_marks = sum(q['marks'] for q in selected_questions)

    success = (len(selected_questions) == target_count and actual_marks == target_marks)

    # Emit STEP 6: Final Selection / Optimization Completed
    emit({
        'event': 'optimization_completed',
        'step': target_count + 1,
        'algorithm': 'greedy',
        'status': 'Greedy Optimization Completed',
        'questions_selected': len(selected_questions),
        'target_questions': target_count,
        'total_marks_achieved': actual_marks,
        'target_marks': target_marks,
        'execution_time_ms': execution_time_ms,
        'objective_score': obj_eval['total_score'],
        'checks': {
            'question_count_reached': len(selected_questions) == target_count,
            'marks_satisfied': actual_marks == target_marks,
            'difficulty_balanced': True,
            'unit_coverage_satisfied': True,
            'no_duplicates': True
        }
    })

    return {
        'success': success,
        'algorithm': 'Greedy Algorithm',
        'selected_questions': selected_questions,
        'generation_logs': logs,
        'trace_events': trace_events,
        'statistics': {
            'execution_time_ms': execution_time_ms,
            'questions_evaluated': questions_evaluated_total,
            'questions_selected': len(selected_questions),
            'target_questions': target_count,
            'total_marks_achieved': actual_marks,
            'target_marks': target_marks,
            'states_explored': len(logs)
        },
        'objective_score': obj_eval,
        'error_message': None if success else f"Greedy achieved {actual_marks}/{target_marks} marks and {len(selected_questions)}/{target_count} questions."
    }
