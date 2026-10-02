import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.database import get_db_connection, init_db

SAMPLE_QUESTIONS = [
    # --- UNIT 1: Analysis of Algorithms & Divide and Conquer (16 Questions) ---
    {
        "question_text": "Define Big-O, Big-Omega, and Big-Theta asymptotic notations with standard mathematical definitions and graphical representations.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Asymptotic Analysis",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "complexity, asymptotic, definitions", "used_count": 2
    },
    {
        "question_text": "What is the time complexity of binary search in the worst case? A) O(n) B) O(log n) C) O(n log n) D) O(1)",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "binary search, search, basics", "used_count": 3
    },
    {
        "question_text": "State the Master Theorem for divide-and-conquer recurrences. Apply it to solve T(n) = 4T(n/2) + n^2.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Recurrence Relations",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "master theorem, recurrence, divide and conquer", "used_count": 1
    },
    {
        "question_text": "Explain the design methodology of the Divide and Conquer paradigm. Walk through Merge Sort on an array of 8 elements and prove its time complexity.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "merge sort, sorting, divide and conquer", "used_count": 0
    },
    {
        "question_text": "Write a clean C++/Python function implementing the Randomized QuickSort partition algorithm. Analyze its best, worst, and expected average-case time complexities.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Sorting",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "quicksort, randomized, partition, code", "used_count": 0
    },
    {
        "question_text": "Derive Strassen's Matrix Multiplication algorithm. Explain how it reduces the number of recursive multiplications from 8 to 7 and analyze the recurrence relation.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "strassen, matrices, divide and conquer", "used_count": 1
    },
    {
        "question_text": "Which asymptotic notation provides an asymptotically tight bound? A) Big-Oh B) Little-Oh C) Big-Theta D) Big-Omega",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Asymptotic Analysis",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "theta, bounds, notations", "used_count": 0
    },
    {
        "question_text": "Explain the difference between amortized analysis and average-case analysis. Describe the Accounting (Banker's) method using a dynamic array doubling example.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Amortized Analysis",
        "difficulty": "Hard", "marks": 10, "question_type": "Descriptive", "tags": "amortized, accounting, dynamic array", "used_count": 0
    },
    {
        "question_text": "Solve the recurrence relation T(n) = 2T(n/2) + n log n using the recursion tree method.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Recurrence Relations",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "recursion tree, recurrences", "used_count": 0
    },
    {
        "question_text": "Describe the algorithm to find the Closest Pair of Points in a 2D plane in O(n log n) time using Divide and Conquer.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "computational geometry, closest pair, divide and conquer", "used_count": 0
    },
    {
        "question_text": "Define Little-o and Little-omega notations and contrast them with Big-O and Big-Omega.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Asymptotic Analysis",
        "difficulty": "Easy", "marks": 5, "question_type": "Short Answer", "tags": "little-o, little-omega, limits", "used_count": 1
    },
    {
        "question_text": "What is the worst-case space complexity of standard recursive Merge Sort on an array of size n? A) O(1) B) O(log n) C) O(n) D) O(n log n)",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Sorting",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "merge sort, space complexity", "used_count": 2
    },
    {
        "question_text": "Implement the QuickSelect algorithm to find the k-th smallest element in an unsorted array in O(n) expected time. Provide complete pseudocode and recurrence analysis.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Medium", "marks": 10, "question_type": "Programming", "tags": "quickselect, order statistics, divide and conquer", "used_count": 0
    },
    {
        "question_text": "Compare the iterative vs recursive implementations of Binary Search in terms of auxiliary stack space and overhead.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "binary search, recursion, space", "used_count": 0
    },
    {
        "question_text": "Solve the recurrence T(n) = T(sqrt(n)) + 1 using substitution and change of variables.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Recurrence Relations",
        "difficulty": "Hard", "marks": 5, "question_type": "Short Answer", "tags": "recurrence, square root, substitution", "used_count": 0
    },
    {
        "question_text": "Comprehensive formulation of Divide and Conquer: (a) Formulate the general recurrence, (b) Discuss the impact of subproblem overlap, (c) Design an algorithm to calculate x^n in O(log n) multiplications.",
        "subject": "Design and Analysis of Algorithms", "unit": 1, "topic": "Divide and Conquer",
        "difficulty": "Medium", "marks": 15, "question_type": "Descriptive", "tags": "modular exponentiation, divide and conquer, fundamentals", "used_count": 0
    },

    # --- UNIT 2: Greedy Method & Graph Traversals (16 Questions) ---
    {
        "question_text": "Explain the Greedy Choice Property and Optimal Substructure. Contrast the Greedy method with Dynamic Programming.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "greedy choice, optimal substructure, theory", "used_count": 1
    },
    {
        "question_text": "In Huffman coding, characters with higher frequencies are assigned codewords of: A) Longer length B) Shorter length C) Fixed 8-bit length D) Equal length",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "huffman, prefix code, greedy", "used_count": 2
    },
    {
        "question_text": "Solve the Fractional Knapsack problem using a Greedy approach for a knapsack capacity W = 50 and items: (v1=60, w1=10), (v2=100, w2=20), (v3=120, w3=30). Show the value-to-weight ratios.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Easy", "marks": 5, "question_type": "Short Answer", "tags": "fractional knapsack, greedy, numerical", "used_count": 3
    },
    {
        "question_text": "Describe Kruskal's algorithm to compute the Minimum Spanning Tree of a weighted undirected graph. Explain how the Disjoint-Set Union (Union-Find) data structure optimizes cycle detection.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "kruskal, mst, union-find, graphs", "used_count": 0
    },
    {
        "question_text": "Implement Dijkstra's Single Source Shortest Path algorithm using a min-priority queue (binary heap). Analyze the overall time complexity for a graph with V vertices and E edges.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "dijkstra, shortest path, priority queue, graphs", "used_count": 0
    },
    {
        "question_text": "Given 5 jobs with deadlines d = [2, 1, 2, 1, 3] and profits p = [100, 19, 27, 25, 15], find the optimal schedule to maximize profit using Job Sequencing with Deadlines.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Medium", "marks": 10, "question_type": "Short Answer", "tags": "job sequencing, deadlines, greedy", "used_count": 0
    },
    {
        "question_text": "Prove that Prim's algorithm correctly produces a Minimum Spanning Tree using the Cut Property of graphs.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Hard", "marks": 10, "question_type": "Theory", "tags": "prim, mst, cut property, proof", "used_count": 1
    },
    {
        "question_text": "Which algorithm is suitable for finding Minimum Spanning Tree in dense graphs? A) Kruskal's with array B) Prim's with adjacency matrix O(V^2) C) Boruvka's D) Dijkstra's",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "prim, dense graph, mst", "used_count": 0
    },
    {
        "question_text": "Construct the optimal Huffman tree and prefix codes for characters A, B, C, D, E, F with frequencies 5, 9, 12, 13, 16, 45. Calculate the average codeword length.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "huffman coding, prefix codes, trees", "used_count": 0
    },
    {
        "question_text": "Formulate and solve the Activity Selection Problem. Prove why choosing the activity with the earliest finish time yields an optimal solution.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Greedy Algorithms",
        "difficulty": "Medium", "marks": 10, "question_type": "Theory", "tags": "activity selection, interval scheduling, greedy", "used_count": 0
    },
    {
        "question_text": "What happens if Dijkstra's algorithm is executed on a graph with negative edge weights? Explain why it fails and provide a concrete counterexample graph.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "dijkstra, negative weights, counterexample", "used_count": 2
    },
    {
        "question_text": "Design an O(E log V) algorithm to solve the Single-Source Shortest Path in a Directed Acyclic Graph (DAG) using Topological Sort.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "dag, topological sort, shortest path", "used_count": 0
    },
    {
        "question_text": "In a connected weighted graph, if all edge weights are distinct, the Minimum Spanning Tree is: A) Not unique B) Strictly unique C) Contains cycles D) Undefined",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "mst, uniqueness, distinct weights", "used_count": 0
    },
    {
        "question_text": "Write pseudocode for Breadth First Search (BFS) and Depth First Search (DFS). Contrast their time and space complexities on an adjacency list representation.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "bfs, dfs, graph traversal", "used_count": 1
    },
    {
        "question_text": "Explain Boruvka's parallel algorithm for Minimum Spanning Trees. Show how components are merged in phases.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Hard", "marks": 10, "question_type": "Descriptive", "tags": "boruvka, parallel, mst", "used_count": 0
    },
    {
        "question_text": "A telecommunication company needs to lay fiber optic cables connecting 6 city hubs with minimum total cost. Given the distance matrix, formulate as an MST problem and solve using both Kruskal and Prim algorithms.",
        "subject": "Design and Analysis of Algorithms", "unit": 2, "topic": "Graphs",
        "difficulty": "Hard", "marks": 20, "question_type": "Long Answer", "tags": "mst, application, case study, prim, kruskal", "used_count": 0
    },

    # --- UNIT 3: Dynamic Programming (16 Questions) ---
    {
        "question_text": "State the Principle of Optimality in Dynamic Programming. How does memoization (top-down) differ from tabulation (bottom-up)?",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "dp concepts, memoization, tabulation", "used_count": 2
    },
    {
        "question_text": "In 0/1 Knapsack, fractional items can be included in the knapsack. True or False? A) True B) False",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "0/1 knapsack, basics", "used_count": 4
    },
    {
        "question_text": "Compute the Longest Common Subsequence (LCS) for sequences X = 'ABCBDAB' and Y = 'BDCABA'. Show the DP table, lengths, and trace back the LCS string.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "lcs, strings, dp table", "used_count": 0
    },
    {
        "question_text": "Solve the Matrix Chain Multiplication problem for 4 matrices with dimensions: A1 (10x30), A2 (30x5), A3 (5x60), A4 (60x10). Find the minimum number of scalar multiplications and optimal parenthesization.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "matrix chain, dynamic programming, parenthesization", "used_count": 1
    },
    {
        "question_text": "Implement the 0/1 Knapsack DP solution in Python/C++ with space optimization reducing auxiliary memory from O(n*W) to O(W).",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "0/1 knapsack, space optimization, code", "used_count": 0
    },
    {
        "question_text": "What is the time complexity of the Floyd-Warshall All-Pairs Shortest Path algorithm for a graph with V vertices? A) O(V^2) B) O(V^3) C) O(V log V) D) O(V*E)",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "floyd-warshall, complexity, graphs", "used_count": 1
    },
    {
        "question_text": "Explain Bellman-Ford algorithm for single-source shortest paths. Show how it detects negative weight cycles and state its time complexity.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "bellman-ford, negative cycles, shortest path", "used_count": 0
    },
    {
        "question_text": "Write the recurrence relation for the Coin Change problem (minimum coins to make change for amount A). Trace it for denominations [1, 2, 5] and amount 11.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "coin change, recurrence, dp", "used_count": 0
    },
    {
        "question_text": "Explain Warshall's algorithm for finding the Transitive Closure of a directed graph. Provide the recurrence equation.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "warshall, transitive closure, bitmatrix", "used_count": 0
    },
    {
        "question_text": "Formulate the Optimal Binary Search Tree (OBST) problem using Dynamic Programming. Given keys K = [k1, k2, k3] with search probabilities p = [0.5, 0.1, 0.05] and unsuccessful probabilities q = [0.15, 0.1, 0.05, 0.05], construct the cost and root tables.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "obst, binary search tree, dp", "used_count": 0
    },
    {
        "question_text": "What is the optimal substructure property of the Traveling Salesperson Problem (TSP)? Write the Held-Karp dynamic programming formulation and its time complexity.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Hard", "marks": 10, "question_type": "Theory", "tags": "tsp, held-karp, exponential dp", "used_count": 0
    },
    {
        "question_text": "Solve the Subset Sum problem: given S = [3, 34, 4, 12, 5, 2] and Target = 9, determine using a boolean DP table whether a subset with sum 9 exists.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "subset sum, boolean dp, partition", "used_count": 0
    },
    {
        "question_text": "The time complexity of finding the n-th Fibonacci number using bottom-up dynamic programming with two variables is: A) O(2^n) B) O(n) C) O(1) D) O(log n)",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "fibonacci, space optimization", "used_count": 0
    },
    {
        "question_text": "Design an algorithm to find the Longest Increasing Subsequence (LIS) of an array of n integers. Compare the O(n^2) DP approach with the O(n log n) patience-sorting/binary-search approach.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "lis, subsequence, optimization", "used_count": 0
    },
    {
        "question_text": "Explain the Edit Distance (Levenshtein Distance) problem. Formulate the dynamic programming recurrence and trace the minimum operations to convert 'SUNDAY' to 'SATURDAY'.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "edit distance, string alignment, dp", "used_count": 1
    },
    {
        "question_text": "A software architecture requires caching intermediate solutions for subproblems with high overlap. Compare Greedy, Divide & Conquer, and DP with respect to substructure, overlap, and memorization strategies.",
        "subject": "Design and Analysis of Algorithms", "unit": 3, "topic": "Dynamic Programming",
        "difficulty": "Hard", "marks": 20, "question_type": "Long Answer", "tags": "paradigm comparison, architectural design, comprehensive", "used_count": 0
    },

    # --- UNIT 4: Backtracking & Branch and Bound (16 Questions) ---
    {
        "question_text": "What is the primary difference between Backtracking and Branch and Bound? Explain state-space tree traversal strategies (DFS vs BFS/Best-First).",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "backtracking, branch and bound, state space", "used_count": 1
    },
    {
        "question_text": "In the N-Queens problem, how many queens are placed on an N x N chessboard such that no two queens attack each other? A) N/2 B) N C) N^2 D) 2N",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "n-queens, constraints", "used_count": 2
    },
    {
        "question_text": "Formulate the 4-Queens problem. Draw the complete state-space tree showing active states, pruned branches, and backtrack actions to find all distinct valid solutions.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "4-queens, state-space tree, pruning", "used_count": 0
    },
    {
        "question_text": "Solve the Sum of Subsets problem for w = [5, 10, 12, 13, 15, 18] and target sum M = 30 using Backtracking. Illustrate how bounding functions prune dead ends.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "sum of subsets, bounding functions, pruning", "used_count": 1
    },
    {
        "question_text": "Implement a recursive Backtracking solver in Python/C++ for the m-Coloring Problem on an undirected graph. Demonstrate safe vertex coloring validation.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "graph coloring, recursive backtracking, code", "used_count": 0
    },
    {
        "question_text": "Explain the Hamiltonian Circuit problem. How is it solved using Backtracking? Show the step-by-step decision sequence on a 5-vertex pentagonal graph.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "hamiltonian circuit, cycles, graphs", "used_count": 0
    },
    {
        "question_text": "Describe the 15-Puzzle problem using Branch and Bound. Explain the Manhattan distance and out-of-place heuristics used in the state evaluation function c(x) = f(x) + g(x).",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "15-puzzle, branch and bound, heuristics, manhattan", "used_count": 0
    },
    {
        "question_text": "Which data structure is typically used to implement Least Cost Branch and Bound (LCBB)? A) Stack B) Queue C) Min-Priority Queue D) Circular Buffer",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "lcbb, priority queue, search", "used_count": 1
    },
    {
        "question_text": "Solve the 0/1 Knapsack problem using LC Branch and Bound with upper and lower bound calculations. Trace the active state queue and bounding steps.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "knapsack, lcbb, upper bound, branch and bound", "used_count": 0
    },
    {
        "question_text": "Define a bounding function. What two conditions must a bounding function satisfy to guarantee finding an optimal solution without exhaustive search?",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "bounding function, admissibility, pruning", "used_count": 0
    },
    {
        "question_text": "Explain how the Traveling Salesperson Problem (TSP) is solved using Branch and Bound with reduced cost matrices.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "tsp, reduced cost matrix, branch and bound", "used_count": 0
    },
    {
        "question_text": "In the Subset Sum problem, if elements are sorted in non-decreasing order, how does it optimize the pruning of the state-space tree?",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "subset sum, sorting optimization, pruning", "used_count": 0
    },
    {
        "question_text": "Which of the following problems cannot be solved with Backtracking? A) N-Queens B) Sudoku C) Knight's Tour D) None of the above",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "backtracking, applications", "used_count": 0
    },
    {
        "question_text": "Implement the Knight's Tour problem using Warnsdorff's heuristic. Contrast it with brute-force backtracking in terms of steps explored.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "knights tour, warnsdorff, heuristic, code", "used_count": 0
    },
    {
        "question_text": "Explain the concept of live nodes, dead nodes, and E-node in Branch and Bound state exploration.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Branch and Bound",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "e-node, live nodes, terminology", "used_count": 1
    },
    {
        "question_text": "Comprehensive Examination Problem: Formulate an automated circuit layout placement problem on an FPGA grid as a constraint satisfaction problem. Design a Backtracking algorithm with forward checking and Minimum Remaining Values (MRV) heuristic.",
        "subject": "Design and Analysis of Algorithms", "unit": 4, "topic": "Backtracking",
        "difficulty": "Hard", "marks": 20, "question_type": "Long Answer", "tags": "csp, mrv heuristic, backtracking, design", "used_count": 0
    },

    # --- UNIT 5: NP-Completeness & Advanced Algorithms (16 Questions) ---
    {
        "question_text": "Define the complexity classes P, NP, NP-Complete, and NP-Hard. Draw the Venn diagram illustrating both scenarios: P = NP and P != NP.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Easy", "marks": 5, "question_type": "Theory", "tags": "p, np, np-complete, np-hard, venn diagram", "used_count": 2
    },
    {
        "question_text": "Which of the following problems is known to be in P? A) 3-SAT B) Minimum Spanning Tree C) Traveling Salesperson Decision Problem D) Vertex Cover",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "class p, polynomial time", "used_count": 1
    },
    {
        "question_text": "State Cook's Theorem. Explain its historic significance in establishing SAT (Boolean Satisfiability) as the first known NP-Complete problem.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Medium", "marks": 5, "question_type": "Theory", "tags": "cooks theorem, sat, historic significance", "used_count": 1
    },
    {
        "question_text": "Explain polynomial-time reductions. Prove that the Clique Problem is NP-Complete by reducing 3-CNF-SAT to Clique in polynomial time.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Hard", "marks": 15, "question_type": "Long Answer", "tags": "reduction, 3-sat, clique, proof", "used_count": 0
    },
    {
        "question_text": "Prove that the Vertex Cover problem is NP-Complete by showing a polynomial-time reduction from the Independent Set problem.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Hard", "marks": 10, "question_type": "Theory", "tags": "vertex cover, independent set, reduction", "used_count": 0
    },
    {
        "question_text": "What is an approximation algorithm? Define approximation ratio rho(n). Explain the 2-approximation greedy algorithm for the Vertex Cover problem.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "approximation ratio, vertex cover, 2-approx", "used_count": 0
    },
    {
        "question_text": "Explain the 1.5-approximation Christofides algorithm for the Metric Traveling Salesperson Problem. List its five core steps (MST, odd-degree matchings, Eulerian tour).",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Hard", "marks": 10, "question_type": "Descriptive", "tags": "christofides, metric tsp, eulerian, approximation", "used_count": 0
    },
    {
        "question_text": "A non-deterministic algorithm operates in two phases: A) Sorting and Searching B) Guessing and Verifying C) Compiling and Executing D) Encoding and Decoding",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "nondeterministic, guessing, verification", "used_count": 1
    },
    {
        "question_text": "Distinguish between Monte Carlo algorithms and Las Vegas randomized algorithms with examples (e.g., Randomized QuickSort vs Miller-Rabin primality test).",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Randomized Algorithms",
        "difficulty": "Medium", "marks": 5, "question_type": "Theory", "tags": "las vegas, monte carlo, randomized", "used_count": 0
    },
    {
        "question_text": "Define a Polynomial-Time Approximation Scheme (PTAS) and Fully Polynomial-Time Approximation Scheme (FPTAS). Why is FPTAS preferable?",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "ptas, fptas, approximation scheme", "used_count": 0
    },
    {
        "question_text": "Implement the greedy 2-approximation algorithm for Vertex Cover in Python. Run it on a bipartite graph and compare its vertex count with the optimal solution.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Hard", "marks": 10, "question_type": "Programming", "tags": "vertex cover, approx implementation, bipartite", "used_count": 0
    },
    {
        "question_text": "Explain why the general Traveling Salesperson Problem cannot be approximated within any constant factor rho unless P = NP.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Hard", "marks": 10, "question_type": "Theory", "tags": "tsp inapproximability, triangle inequality, proof", "used_count": 0
    },
    {
        "question_text": "Which of the following problems is NP-Hard but NOT in NP? A) Halting Problem B) 3-SAT C) Circuit-SAT D) Knapsack",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "NP-Completeness",
        "difficulty": "Easy", "marks": 2, "question_type": "MCQ", "tags": "halting problem, undecidability, np-hard", "used_count": 0
    },
    {
        "question_text": "Describe the Set Cover problem. Show that the greedy heuristic provides an O(ln |U|) approximation ratio for the universe U.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Medium", "marks": 10, "question_type": "Descriptive", "tags": "set cover, greedy approx, harmonic number", "used_count": 0
    },
    {
        "question_text": "Explain Rabin-Karp randomized string matching algorithm using rolling hash functions. What is its average and worst-case time complexity?",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Randomized Algorithms",
        "difficulty": "Medium", "marks": 5, "question_type": "Short Answer", "tags": "rabin-karp, rolling hash, string matching", "used_count": 0
    },
    {
        "question_text": "Comprehensive Industrial Case Study: A cloud datacenter needs to allocate virtual machines to physical servers to minimize active servers (Bin Packing Problem). (a) Formulate Bin Packing, (b) Prove it is NP-Hard, (c) Design First-Fit and First-Fit-Decreasing heuristics and analyze their competitive bounds.",
        "subject": "Design and Analysis of Algorithms", "unit": 5, "topic": "Approximation Algorithms",
        "difficulty": "Hard", "marks": 20, "question_type": "Long Answer", "tags": "bin packing, heuristics, cloud allocation, comprehensive", "used_count": 0
    }
]

def seed_database():
    """Populates database with sample questions if empty."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check count
    count = cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count == 0:
        print(f"Seeding database with {len(SAMPLE_QUESTIONS)} DAA questions across 5 units...")
        for q in SAMPLE_QUESTIONS:
            cursor.execute("""
                INSERT INTO questions 
                (question_text, subject, unit, topic, difficulty, marks, question_type, tags, used_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q['question_text'], q['subject'], q['unit'], q['topic'],
                q['difficulty'], q['marks'], q['question_type'], q['tags'], q['used_count']
            ))
        conn.commit()
        print("Database seeded successfully!")
    else:
        print(f"Database already contains {count} questions. Skipping seed.")
    conn.close()

if __name__ == '__main__':
    seed_database()
