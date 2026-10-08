"""
Sorting Algorithms implementation for CoreAlgorithm PROBLEM95.
Provides Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, and Quick Sort.
Tracks exact comparisons, swaps/moves, high-resolution execution time, and animation steps.
"""

import time
from typing import Dict, List, Any, Tuple

DIFFICULTY_MAP = {'Easy': 1, 'Medium': 2, 'Hard': 3}

def get_key_value(item: Dict[str, Any], key: str):
    """Extracts comparable value from question dict based on key."""
    if key == 'difficulty':
        return DIFFICULTY_MAP.get(item.get('difficulty', 'Medium'), 2)
    elif key == 'marks':
        return int(item.get('marks', 0))
    elif key == 'unit':
        return int(item.get('unit', 1))
    elif key == 'used_count':
        return int(item.get('used_count', 0))
    elif key == 'id':
        return int(item.get('id', 0))
    elif key == 'topic':
        return str(item.get('topic', '')).lower()
    else:
        return str(item.get(key, '')).lower()

# --- 1. Bubble Sort ---
def bubble_sort(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True, record_steps: bool = False) -> Dict[str, Any]:
    arr = [dict(x) for x in items]
    n = len(arr)
    comparisons = 0
    swaps = 0
    steps = []

    start = time.perf_counter()
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val_a = get_key_value(arr[j], key)
            val_b = get_key_value(arr[j + 1], key)
            comparisons += 1

            if record_steps and len(steps) < 150:
                steps.append({'type': 'compare', 'indices': [j, j + 1], 'array': [get_key_value(x, key) for x in arr]})

            condition = (val_a > val_b) if ascending else (val_a < val_b)
            if condition:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                if record_steps and len(steps) < 150:
                    steps.append({'type': 'swap', 'indices': [j, j + 1], 'array': [get_key_value(x, key) for x in arr]})
        if not swapped:
            break
    duration_ms = (time.perf_counter() - start) * 1000

    return {
        'algorithm': 'Bubble Sort',
        'key': key,
        'ascending': ascending,
        'input_size': n,
        'comparisons': comparisons,
        'swaps': swaps,
        'execution_time_ms': round(duration_ms, 4),
        'time_complexity': 'O(n²)',
        'best_time': 'O(n)',
        'worst_time': 'O(n²)',
        'space_complexity': 'O(1)',
        'stability': 'Stable',
        'sorted_items': arr,
        'steps': steps
    }

# --- 2. Selection Sort ---
def selection_sort(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True, record_steps: bool = False) -> Dict[str, Any]:
    arr = [dict(x) for x in items]
    n = len(arr)
    comparisons = 0
    swaps = 0
    steps = []

    start = time.perf_counter()
    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            val_j = get_key_value(arr[j], key)
            val_target = get_key_value(arr[target_idx], key)

            if record_steps and len(steps) < 150:
                steps.append({'type': 'compare', 'indices': [target_idx, j], 'array': [get_key_value(x, key) for x in arr]})

            condition = (val_j < val_target) if ascending else (val_j > val_target)
            if condition:
                target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            swaps += 1
            if record_steps and len(steps) < 150:
                steps.append({'type': 'swap', 'indices': [i, target_idx], 'array': [get_key_value(x, key) for x in arr]})
    duration_ms = (time.perf_counter() - start) * 1000

    return {
        'algorithm': 'Selection Sort',
        'key': key,
        'ascending': ascending,
        'input_size': n,
        'comparisons': comparisons,
        'swaps': swaps,
        'execution_time_ms': round(duration_ms, 4),
        'time_complexity': 'O(n²)',
        'best_time': 'O(n²)',
        'worst_time': 'O(n²)',
        'space_complexity': 'O(1)',
        'stability': 'Unstable',
        'sorted_items': arr,
        'steps': steps
    }

# --- 3. Insertion Sort ---
def insertion_sort(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True, record_steps: bool = False) -> Dict[str, Any]:
    arr = [dict(x) for x in items]
    n = len(arr)
    comparisons = 0
    swaps = 0  # In insertion sort, counted as shifts/moves
    steps = []

    start = time.perf_counter()
    for i in range(1, n):
        key_item = arr[i]
        key_val = get_key_value(key_item, key)
        j = i - 1

        while j >= 0:
            comparisons += 1
            curr_val = get_key_value(arr[j], key)
            if record_steps and len(steps) < 150:
                steps.append({'type': 'compare', 'indices': [j, j + 1], 'array': [get_key_value(x, key) for x in arr]})

            condition = (curr_val > key_val) if ascending else (curr_val < key_val)
            if condition:
                arr[j + 1] = arr[j]
                swaps += 1
                if record_steps and len(steps) < 150:
                    steps.append({'type': 'overwrite', 'indices': [j + 1, j], 'array': [get_key_value(x, key) for x in arr]})
                j -= 1
            else:
                break
        arr[j + 1] = key_item
    duration_ms = (time.perf_counter() - start) * 1000

    return {
        'algorithm': 'Insertion Sort',
        'key': key,
        'ascending': ascending,
        'input_size': n,
        'comparisons': comparisons,
        'swaps': swaps,
        'execution_time_ms': round(duration_ms, 4),
        'time_complexity': 'O(n²)',
        'best_time': 'O(n)',
        'worst_time': 'O(n²)',
        'space_complexity': 'O(1)',
        'stability': 'Stable',
        'sorted_items': arr,
        'steps': steps
    }

# --- 4. Merge Sort ---
def merge_sort(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True, record_steps: bool = False) -> Dict[str, Any]:
    arr = [dict(x) for x in items]
    comparisons = 0
    swaps = 0
    steps = []

    start = time.perf_counter()

    def merge(left: int, mid: int, right: int):
        nonlocal comparisons, swaps
        L = arr[left:mid + 1]
        R = arr[mid + 1:right + 1]
        i = j = 0
        k = left

        while i < len(L) and j < len(R):
            comparisons += 1
            val_l = get_key_value(L[i], key)
            val_r = get_key_value(R[j], key)
            if record_steps and len(steps) < 150:
                steps.append({'type': 'compare', 'indices': [left + i, mid + 1 + j], 'array': [get_key_value(x, key) for x in arr]})

            condition = (val_l <= val_r) if ascending else (val_l >= val_r)
            if condition:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            swaps += 1
            if record_steps and len(steps) < 150:
                steps.append({'type': 'overwrite', 'indices': [k], 'array': [get_key_value(x, key) for x in arr]})
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
            swaps += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
            swaps += 1

    def recursive_sort(left: int, right: int):
        if left < right:
            mid = (left + right) // 2
            recursive_sort(left, mid)
            recursive_sort(mid + 1, right)
            merge(left, mid, right)

    if len(arr) > 1:
        recursive_sort(0, len(arr) - 1)

    duration_ms = (time.perf_counter() - start) * 1000

    return {
        'algorithm': 'Merge Sort',
        'key': key,
        'ascending': ascending,
        'input_size': len(arr),
        'comparisons': comparisons,
        'swaps': swaps,
        'execution_time_ms': round(duration_ms, 4),
        'time_complexity': 'O(n log n)',
        'best_time': 'O(n log n)',
        'worst_time': 'O(n log n)',
        'space_complexity': 'O(n)',
        'stability': 'Stable',
        'sorted_items': arr,
        'steps': steps
    }

# --- 5. Quick Sort ---
def quick_sort(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True, record_steps: bool = False) -> Dict[str, Any]:
    arr = [dict(x) for x in items]
    comparisons = 0
    swaps = 0
    steps = []

    start = time.perf_counter()

    def partition(low: int, high: int) -> int:
        nonlocal comparisons, swaps
        pivot_val = get_key_value(arr[high], key)
        i = low - 1

        for j in range(low, high):
            comparisons += 1
            val_j = get_key_value(arr[j], key)
            if record_steps and len(steps) < 150:
                steps.append({'type': 'compare', 'indices': [j, high], 'array': [get_key_value(x, key) for x in arr]})

            condition = (val_j <= pivot_val) if ascending else (val_j >= pivot_val)
            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                swaps += 1
                if record_steps and len(steps) < 150:
                    steps.append({'type': 'swap', 'indices': [i, j], 'array': [get_key_value(x, key) for x in arr]})

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        swaps += 1
        if record_steps and len(steps) < 150:
            steps.append({'type': 'swap', 'indices': [i + 1, high], 'array': [get_key_value(x, key) for x in arr]})
        return i + 1

    def recursive_sort(low: int, high: int):
        if low < high:
            pi = partition(low, high)
            recursive_sort(low, pi - 1)
            recursive_sort(pi + 1, high)

    if len(arr) > 1:
        recursive_sort(0, len(arr) - 1)

    duration_ms = (time.perf_counter() - start) * 1000

    return {
        'algorithm': 'Quick Sort',
        'key': key,
        'ascending': ascending,
        'input_size': len(arr),
        'comparisons': comparisons,
        'swaps': swaps,
        'execution_time_ms': round(duration_ms, 4),
        'time_complexity': 'O(n log n)',
        'best_time': 'O(n log n)',
        'worst_time': 'O(n²)',
        'space_complexity': 'O(log n)',
        'stability': 'Unstable',
        'sorted_items': arr,
        'steps': steps
    }

def run_all_sorting_benchmarks(items: List[Dict[str, Any]], key: str = 'marks', ascending: bool = True) -> List[Dict[str, Any]]:
    """Runs all 5 sorting algorithms on identical input and returns side-by-side comparison data."""
    results = [
        bubble_sort(items, key, ascending, record_steps=False),
        selection_sort(items, key, ascending, record_steps=False),
        insertion_sort(items, key, ascending, record_steps=False),
        merge_sort(items, key, ascending, record_steps=False),
        quick_sort(items, key, ascending, record_steps=False),
    ]
    # Remove sorted_items from summary to keep payload lightweight
    summary = []
    for r in results:
        summary.append({
            'algorithm': r['algorithm'],
            'input_size': r['input_size'],
            'comparisons': r['comparisons'],
            'swaps': r['swaps'],
            'execution_time_ms': r['execution_time_ms'],
            'time_complexity': r['time_complexity'],
            'space_complexity': r['space_complexity'],
            'stability': r['stability']
        })
    return summary
