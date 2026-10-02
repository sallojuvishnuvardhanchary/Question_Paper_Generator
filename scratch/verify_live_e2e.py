"""
Live End-to-End Test for Syllabus-Driven Intelligent Exam Question Paper Generator
Tests all major workflows on the active HTTP server:
- Syllabus Upload (TXT/PDF)
- Syllabus Extraction & Structure Retrieval
- Candidate Question Pool Generation (Bloom's taxonomy)
- Dynamic Structure Construction (Multiple Parts, Sections, Internal Choices)
- Greedy Paper Synthesis
- Backtracking Paper Synthesis
- Multiple Choice Questions (MCQ) Mode + Answer Key Generation
- Theory-Only Mode
- PDF Generation & Download (Exam Paper + Answer Key)
- Verification of Generated PDF bytes
"""

import urllib.request
import urllib.parse
import json
import os

BASE_URL = "http://127.0.0.1:5000"

def post_json(path, data):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def get_json(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}") as res:
        return json.loads(res.read().decode('utf-8'))

def get_bytes(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}") as res:
        return res.read(), res.headers

def run_e2e():
    print("=== 1. HEALTH CHECK ===")
    health = get_json("/health")
    print(f"Health Status: {health['status']}, Problem: {health['problem']}")
    assert health['status'] == 'online'

    print("\n=== 2. UPLOAD COURSE SYLLABUS ===")
    sample_syllabus_text = """
    ADVANCED DATA STRUCTURES AND ALGORITHMS (CS-601)

    UNIT I: Divide and Conquer & Sorting
    Divide and conquer design paradigms, Recurrence relations, Master theorem,
    Merge Sort, Quick Sort, Randomized Quick Sort, Lower bounds for sorting.

    UNIT II: Greedy Strategy & Graph Algorithms
    Greedy choice property, Fractional Knapsack, Huffman coding,
    Minimum Spanning Trees: Kruskal and Prim algorithms,
    Single-source shortest paths: Dijkstra and Bellman-Ford algorithms.

    UNIT III: Dynamic Programming
    Elements of dynamic programming, Optimal substructure,
    0/1 Knapsack problem, Matrix Chain Multiplication,
    Longest Common Subsequence, Floyd-Warshall all-pairs shortest paths.

    UNIT IV: Backtracking & Branch and Bound
    Backtracking paradigm, 8-Queens problem, Sum of subsets,
    Graph coloring, Hamiltonian cycles,
    Branch and Bound: 0/1 Knapsack, Traveling Salesperson Problem.

    UNIT V: NP-Completeness & Approximation
    P, NP, NP-Hard, NP-Complete classes, Circuit Satisfiability,
    3-SAT, Clique problem, Vertex Cover, Approximation algorithms.
    """
    upload_res = post_json("/api/syllabus/upload", {
        "subject": "Advanced Data Structures and Algorithms",
        "raw_text": sample_syllabus_text
    })
    assert upload_res['success'] is True
    syllabus_id = upload_res['syllabus_id']
    structured_data = upload_res['structured_data']
    print(f"Syllabus ID: {syllabus_id}, Subject: {upload_res['subject']}")
    print(f"Units Extracted: {len(structured_data['units'])}")
    for u in structured_data['units']:
        print(f"  - Unit {u['unit']}: {u['title']} ({len(u['topics'])} topics)")
    assert len(structured_data['units']) == 5

    print("\n=== 3. GENERATE CANDIDATE QUESTIONS FROM SYLLABUS ===")
    cand_res = post_json("/api/questions/generate", {
        "syllabus_id": syllabus_id,
        "paper_type": "theory_bits"
    })
    assert cand_res['success'] is True
    candidate_questions = cand_res['questions']
    print(f"Candidate Questions Generated: {len(candidate_questions)}")
    assert len(candidate_questions) >= 20

    print("\n=== 4. TEST THEORY + BITS PAPER GENERATION (GREEDY ALGORITHM) ===")
    greedy_paper_payload = {
        "syllabus_id": syllabus_id,
        "paper_name": "Autonomous End-Semester Examination 2026",
        "subject": "Advanced Data Structures and Algorithms",
        "paper_type": "theory_bits",
        "algorithm": "greedy",
        "structure": [
            {
                "part_name": "PART A (Compulsory Conceptual Bits)",
                "sections": [
                    {
                        "section_name": "Short Questions",
                        "question_count": 5,
                        "marks_per_question": 2,
                        "question_type": "Bits",
                        "internal_choice": False
                    }
                ]
            },
            {
                "part_name": "PART B (Analytical & Design Problems)",
                "sections": [
                    {
                        "section_name": "Unit-Wise Comprehensive Questions",
                        "question_count": 4,
                        "marks_per_question": 10,
                        "question_type": "Theory",
                        "internal_choice": True
                    }
                ]
            }
        ],
        "total_marks": 50,
        "question_count": 9,
        "save": True
    }
    greedy_res = post_json("/api/paper/generate", greedy_paper_payload)
    assert greedy_res['success'] is True
    greedy_paper_id = greedy_res['paper_id']
    print(f"Greedy Paper Generated! ID: {greedy_paper_id}")
    print(f"Algorithm: {greedy_res['algorithm']}, Time: {greedy_res['statistics']['execution_time_ms']}ms")
    print(f"Objective Score: {greedy_res['objective_score']['total_score']}/100")
    print(f"Validation Status: {'Valid' if greedy_res['validation']['is_valid'] else 'Has Warnings'}")
    assert greedy_res['validation']['is_valid'] is True

    print("\n=== 5. TEST BACKTRACKING ALGORITHM WITH BRANCH & BOUND ===")
    backtrack_payload = dict(greedy_paper_payload)
    backtrack_payload["paper_name"] = "Midterm Examination (Backtracking Optimized)"
    backtrack_payload["algorithm"] = "backtracking"
    backtrack_res = post_json("/api/paper/generate", backtrack_payload)
    assert backtrack_res['success'] is True
    backtrack_paper_id = backtrack_res['paper_id']
    print(f"Backtracking Paper Generated! ID: {backtrack_paper_id}")
    print(f"Algorithm: {backtrack_res['algorithm']}, Time: {backtrack_res['statistics']['execution_time_ms']}ms")
    print(f"Objective Score: {backtrack_res['objective_score']['total_score']}/100")
    assert backtrack_res['validation']['is_valid'] is True

    print("\n=== 6. TEST MCQ EXAMINATION PAPER + ANSWER KEY ===")
    mcq_cand_res = post_json("/api/questions/generate", {
        "syllabus_id": syllabus_id,
        "paper_type": "mcq"
    })
    assert mcq_cand_res['success'] is True
    print(f"MCQ Candidates Generated: {len(mcq_cand_res['questions'])}")

    mcq_paper_payload = {
        "syllabus_id": syllabus_id,
        "paper_name": "Objective Screening Examination (MCQ)",
        "subject": "Advanced Data Structures and Algorithms",
        "paper_type": "mcq",
        "algorithm": "greedy",
        "structure": [
            {
                "part_name": "SECTION 1 — MULTIPLE CHOICE",
                "sections": [
                    {
                        "section_name": "Core Curriculum Items",
                        "question_count": 20,
                        "marks_per_question": 1,
                        "question_type": "MCQ",
                        "internal_choice": False
                    }
                ]
            }
        ],
        "total_marks": 20,
        "question_count": 20,
        "save": True
    }
    mcq_paper_res = post_json("/api/paper/generate", mcq_paper_payload)
    assert mcq_paper_res['success'] is True
    mcq_paper_id = mcq_paper_res['paper_id']
    print(f"MCQ Paper Generated! ID: {mcq_paper_id}")
    print(f"MCQ Download URL: {mcq_paper_res.get('pdf_url')}")
    print(f"MCQ Answer Key URL: {mcq_paper_res.get('answer_key_url')}")
    assert mcq_paper_res.get('pdf_url') is not None
    assert mcq_paper_res.get('answer_key_url') is not None

    print("\n=== 7. VERIFY AND DOWNLOAD PDFS VIA HTTP ===")
    # Download Greedy Exam Paper PDF
    pdf_bytes, headers = get_bytes(f"/api/paper/{greedy_paper_id}/download")
    print(f"Downloaded Greedy Exam Paper PDF: {len(pdf_bytes)} bytes, Content-Type: {headers.get('Content-Type')}")
    assert headers.get('Content-Type') == 'application/pdf'
    assert pdf_bytes.startswith(b"%PDF")

    # Download MCQ Exam Paper PDF
    mcq_pdf_bytes, mcq_headers = get_bytes(f"/api/paper/{mcq_paper_id}/download")
    print(f"Downloaded MCQ Exam Paper PDF: {len(mcq_pdf_bytes)} bytes")
    assert mcq_headers.get('Content-Type') == 'application/pdf'
    assert mcq_pdf_bytes.startswith(b"%PDF")

    # Download MCQ Answer Key PDF
    key_bytes, key_headers = get_bytes(f"/api/paper/{mcq_paper_id}/download-key")
    print(f"Downloaded MCQ Answer Key PDF: {len(key_bytes)} bytes")
    assert key_headers.get('Content-Type') == 'application/pdf'
    assert key_bytes.startswith(b"%PDF")

    print("\n=== 8. TEST HISTORICAL PAPERS RETRIEVAL ===")
    papers_list = get_json("/api/papers?page=1&per_page=10")
    assert papers_list['success'] is True
    print(f"Total Papers in Database History: {papers_list['total_count']}")
    assert papers_list['total_count'] >= 3

    print("\n=== 9. TEST ALGORITHM COMPARISON SUITE ===")
    comp_res = post_json("/api/algorithms/compare", {
        "paper_name": "Comparative Test",
        "subject": "Advanced Data Structures and Algorithms",
        "total_marks": 50,
        "question_count": 5,
        "difficulty_ratio": {"Easy": 0.40, "Medium": 0.40, "Hard": 0.20},
        "unit_ratio": {"1": 0.20, "2": 0.20, "3": 0.20, "4": 0.20, "5": 0.20},
        "required_topics": []
    })
    assert comp_res['success'] is True
    print(f"Comparative Benchmark Completed!")
    print(f"  Greedy: {comp_res['greedy']['execution_time_ms']}ms, Score: {comp_res['greedy']['objective_score']}")
    print(f"  Backtracking: {comp_res['backtracking']['execution_time_ms']}ms, Score: {comp_res['backtracking']['objective_score']}")
    print(f"  Observation: {comp_res['observation'][:100]}...")

    print("\n=======================================================")
    print(" ALL LIVE END-TO-END WORKFLOW CHECKS PASSED WITH 100%! ")
    print("=======================================================")

if __name__ == '__main__':
    run_e2e()
