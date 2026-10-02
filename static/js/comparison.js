/**
 * Algorithm Comparison Module
 * CoreAlgorithm PROBLEM95
 * Executes Greedy vs Backtracking on identical inputs and provides side-by-side metrics & analysis.
 */

const ComparisonView = {
  initialized: false,

  init() {
    if (!this.initialized) {
      document.getElementById('btnRunComparison')?.addEventListener('click', () => this.runComparison());
      this.initialized = true;
    }
    // Auto-run if first time
    const resultBox = document.getElementById('comparisonResultsBox');
    if (resultBox && resultBox.style.display === 'none') {
      this.runComparison();
    }
  },

  async runComparison() {
    const totalMarks = parseInt(document.getElementById('compTotalMarks')?.value || 100);
    const questionCount = parseInt(document.getElementById('compQuestionCount')?.value || 10);
    const avoidUsed = document.getElementById('compAvoidUsed')?.checked || false;

    const payload = {
      paper_name: 'Comparative Benchmark Examination',
      subject: 'Design and Analysis of Algorithms',
      total_marks: totalMarks,
      question_count: questionCount,
      difficulty_ratio: {'Easy': 0.30, 'Medium': 0.50, 'Hard': 0.20},
      unit_ratio: {'1': 0.20, '2': 0.20, '3': 0.20, '4': 0.20, '5': 0.20},
      required_topics: ['Divide and Conquer', 'Greedy Algorithms', 'Dynamic Programming', 'Backtracking', 'NP-Completeness'],
      avoid_used: avoidUsed,
      max_per_topic: 3
    };

    const runBtn = document.getElementById('btnRunComparison');
    const origHtml = runBtn.innerHTML;
    runBtn.disabled = true;
    runBtn.innerHTML = `Running Benchmarks...`;

    try {
      const res = await fetch('/api/algorithms/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        this.renderResults(data);
        App.showToast('Benchmark completed successfully!', 'success');
      } else {
        App.showToast(data.error || 'Benchmark failed', 'error');
      }
    } catch (err) {
      console.error('Comparison error:', err);
      App.showToast('Network error during benchmark', 'error');
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = origHtml;
    }
  },

  renderResults(data) {
    const box = document.getElementById('comparisonResultsBox');
    if (box) box.style.display = 'block';

    const g = data.greedy;
    const b = data.backtracking;

    // Metric cards
    document.getElementById('compGreedyTime').textContent = `${g.execution_time_ms} ms`;
    document.getElementById('compBacktrackTime').textContent = `${b.execution_time_ms} ms`;

    document.getElementById('compGreedyScore').textContent = `${g.objective_score} / 100`;
    document.getElementById('compBacktrackScore').textContent = `${b.objective_score} / 100`;

    document.getElementById('compGreedyEval').textContent = g.questions_evaluated;
    document.getElementById('compBacktrackStates').textContent = `${b.states_explored} states (${b.branches_pruned} pruned)`;

    // Detailed Comparison Table
    const tbody = document.getElementById('compTableBody');
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td><strong>Execution Time</strong></td>
          <td><strong style="color:var(--primary);">${g.execution_time_ms} ms</strong></td>
          <td><strong style="color:var(--secondary);">${b.execution_time_ms} ms</strong></td>
          <td><em>${g.execution_time_ms < b.execution_time_ms ? 'Greedy faster' : 'Backtracking comparable'}</em></td>
        </tr>
        <tr>
          <td><strong>Questions / States Evaluated</strong></td>
          <td>${g.questions_evaluated} candidates</td>
          <td>${b.states_explored} state-space nodes</td>
          <td><em>Backtracking explores recursive combinations</em></td>
        </tr>
        <tr>
          <td><strong>Branches Pruned (Bounds)</strong></td>
          <td>0 (No tree branching)</td>
          <td><span class="badge badge-hard">${b.branches_pruned} pruned</span></td>
          <td><em>Branch-and-bound eliminates infeasible subtrees</em></td>
        </tr>
        <tr>
          <td><strong>Backtrack Events (Undone Choices)</strong></td>
          <td>0 (Irrevocable decisions)</td>
          <td><span class="badge badge-medium">${b.backtracks_count} backtracks</span></td>
          <td><em>Backtracking reverts choices upon dead-ends</em></td>
        </tr>
        <tr>
          <td><strong>Total Marks Satisfied</strong></td>
          <td>${g.total_marks} / ${data.config.total_marks}</td>
          <td>${b.total_marks} / ${data.config.total_marks}</td>
          <td><span class="badge ${g.is_valid ? 'badge-easy' : 'badge-medium'}">${g.is_valid ? 'Valid' : 'Adjusted'}</span> vs <span class="badge ${b.is_valid ? 'badge-easy' : 'badge-medium'}">${b.is_valid ? 'Valid' : 'Adjusted'}</span></td>
        </tr>
        <tr>
          <td><strong>Final Objective Score</strong></td>
          <td><strong style="color:var(--primary);">${g.objective_score} / 100</strong></td>
          <td><strong style="color:var(--secondary);">${b.objective_score} / 100</strong></td>
          <td><em>Based on transparent 5-attribute objective function</em></td>
        </tr>
        <tr>
          <td><strong>Time Complexity</strong></td>
          <td><code>${g.time_complexity}</code></td>
          <td><code>${b.time_complexity}</code></td>
          <td><em>Polynomial vs Exponential worst-case</em></td>
        </tr>
        <tr>
          <td><strong>Auxiliary Space</strong></td>
          <td><code>${g.space_complexity}</code></td>
          <td><code>${b.space_complexity}</code></td>
          <td><em>Greedy uses flat array; Backtracking uses call stack</em></td>
        </tr>
      `;
    }

    // Academic Observation
    const obsEl = document.getElementById('compAcademicObservation');
    if (obsEl) {
      obsEl.innerHTML = `
        <div style="padding: 16px; background: var(--bg-card-subtle); border-left: 4px solid var(--primary); border-radius: var(--radius-md); font-size: 13.5px; line-height: 1.6; color: var(--text-secondary);">
          <strong style="color: var(--text-primary); display: block; margin-bottom: 6px;">Academic Synthesis & Algorithmic Trade-off:</strong>
          ${data.observation}
        </div>
      `;
    }
  }
};

window.ComparisonView = ComparisonView;
