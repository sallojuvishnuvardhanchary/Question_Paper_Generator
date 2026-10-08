/**
 * Interactive Algorithm Lab / Visualizer Module
 * CoreAlgorithm PROBLEM95
 * Implements step-by-step visualizations for Greedy, Backtracking, and Sorting.
 */

const VisualizerView = {
  activeTab: 'greedy',
  initialized: false,

  // Greedy state
  greedyLogs: [],
  greedyStep: 0,
  greedyPlaying: false,
  greedyTimer: null,
  greedySpeed: 1000,

  // Backtracking state
  treeLogs: [],
  treeStep: 0,
  treePlaying: false,
  treeTimer: null,
  treeSpeed: 600,

  // Sorting state
  sortSteps: [],
  sortStepIndex: 0,
  sortPlaying: false,
  sortTimer: null,
  sortSpeed: 400,
  sortCurrentArray: [],

  init() {
    if (!this.initialized) {
      this.bindTabEvents();
      this.bindGreedyControls();
      this.bindBacktrackControls();
      this.bindSortingControls();
      this.initialized = true;
    }
    // Load initial greedy trace if empty
    if (this.greedyLogs.length === 0) {
      this.fetchGreedyTrace();
    }
  },

  bindTabEvents() {
    document.querySelectorAll('.algo-lab-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.getAttribute('data-tab');
        this.switchTab(tab);
      });
    });
  },

  switchTab(tab) {
    this.activeTab = tab;
    document.querySelectorAll('.algo-lab-tab-btn').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-tab') === tab);
    });
    document.querySelectorAll('.algo-lab-pane').forEach(p => {
      const isTarget = (p.id === `labPane-${tab}`);
      p.style.display = isTarget ? 'block' : 'none';
      p.classList.toggle('active', isTarget);
    });

    if (tab === 'greedy' && this.greedyLogs.length === 0) this.fetchGreedyTrace();
    if (tab === 'backtracking' && this.treeLogs.length === 0) this.fetchBacktrackingTrace();
    if (tab === 'sorting' && this.sortSteps.length === 0) this.fetchSortingTrace();
  },

  // ==========================================
  // 1. GREEDY ALGORITHM VISUALIZATION
  // ==========================================
  bindGreedyControls() {
    document.getElementById('btnGreedyPlay')?.addEventListener('click', () => this.toggleGreedyPlay());
    document.getElementById('btnGreedyNext')?.addEventListener('click', () => this.stepGreedy(1));
    document.getElementById('btnGreedyPrev')?.addEventListener('click', () => this.stepGreedy(-1));
    document.getElementById('btnGreedyReset')?.addEventListener('click', () => this.resetGreedy());
    
    const speedSelect = document.getElementById('greedySpeedSelect');
    if (speedSelect) {
      speedSelect.addEventListener('change', (e) => {
        this.greedySpeed = parseInt(e.target.value);
        if (this.greedyPlaying) {
          this.pauseGreedy();
          this.playGreedy();
        }
      });
    }

    document.getElementById('btnGreedyFetchNew')?.addEventListener('click', () => this.fetchGreedyTrace());
  },

  async fetchGreedyTrace() {
    try {
      const res = await fetch('/api/algorithms/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'greedy' })
      });
      const data = await res.json();
      if (data.success && data.logs) {
        this.greedyLogs = data.logs;
        this.resetGreedy();
      }
    } catch (err) {
      console.error('Failed to load greedy trace:', err);
    }
  },

  resetGreedy() {
    this.pauseGreedy();
    this.greedyStep = 0;
    this.renderGreedyStep();
  },

  toggleGreedyPlay() {
    if (this.greedyPlaying) {
      this.pauseGreedy();
    } else {
      this.playGreedy();
    }
  },

  playGreedy() {
    this.greedyPlaying = true;
    const playBtn = document.getElementById('btnGreedyPlay');
    if (playBtn) playBtn.innerHTML = `<span>⏸ Pause</span>`;

    this.greedyTimer = setInterval(() => {
      if (this.greedyStep < this.greedyLogs.length) {
        this.greedyStep++;
        this.renderGreedyStep();
      } else {
        this.pauseGreedy();
      }
    }, this.greedySpeed);
  },

  pauseGreedy() {
    this.greedyPlaying = false;
    clearInterval(this.greedyTimer);
    const playBtn = document.getElementById('btnGreedyPlay');
    if (playBtn) playBtn.innerHTML = `<span>▶ Play</span>`;
  },

  stepGreedy(direction) {
    this.pauseGreedy();
    const next = this.greedyStep + direction;
    if (next >= 0 && next <= this.greedyLogs.length) {
      this.greedyStep = next;
      this.renderGreedyStep();
    }
  },

  renderGreedyStep() {
    const stepDisplay = document.getElementById('greedyStepCounter');
    if (stepDisplay) stepDisplay.textContent = `Step ${this.greedyStep} of ${this.greedyLogs.length}`;

    const container = document.getElementById('greedyStageContent');
    if (!container) return;

    if (this.greedyStep === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-muted);">
          <h4>Greedy Heuristic Selection Initialized</h4>
          <p style="margin-top: 8px;">Target Marks: 100 | Questions to Select: 10</p>
          <p style="margin-top: 4px; font-size: 13px;">Press <strong>Play</strong> or <strong>Next Step</strong> to evaluate candidates using the multi-attribute greedy score.</p>
        </div>
      `;
      return;
    }

    const currentLog = this.greedyLogs[this.greedyStep - 1];
    const state = currentLog.state_after;

    container.innerHTML = `
      <div style="display: flex; gap: 20px; flex-wrap: wrap;">
        <!-- Left: Selected Question Card -->
        <div style="flex: 1.4; background: var(--bg-card); border: 2px solid var(--primary); border-radius: var(--radius-lg); padding: 18px; box-shadow: var(--shadow-md);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span class="badge badge-unit">Step ${currentLog.step}: SELECTED</span>
            <span style="font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: var(--primary);">Score: ${currentLog.score}</span>
          </div>
          <h3 style="font-size: 15px; color: var(--text-primary); margin-bottom: 8px;">Q${currentLog.step}. ${this.escapeHtml(currentLog.question_text)}</h3>
          <div style="display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;">
            <span class="badge badge-unit">Unit ${currentLog.unit}</span>
            <span class="badge badge-neutral">${currentLog.topic}</span>
            <span class="badge badge-${currentLog.difficulty.toLowerCase()}">${currentLog.difficulty}</span>
            <span class="badge badge-marks">${currentLog.marks} Marks</span>
          </div>

          <h5 style="font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Why this question won this step:</h5>
          <ul style="padding-left: 20px; font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
            ${(currentLog.reasons || []).map(r => `<li><strong>${this.escapeHtml(r)}</strong></li>`).join('')}
          </ul>

          <div style="margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--border-color); display: flex; gap: 8px; font-size: 11.5px; font-family: var(--font-mono);">
            <span>Diff Score: <strong>${currentLog.breakdown?.difficulty || 0}</strong></span> |
            <span>Unit: <strong>${currentLog.breakdown?.unit || 0}</strong></span> |
            <span>Topic: <strong>${currentLog.breakdown?.topic || 0}</strong></span> |
            <span>Marks Fit: <strong>${currentLog.breakdown?.marks_fit || 0}</strong></span>
          </div>
        </div>

        <!-- Right: Runner-ups & Remaining Constraints -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 14px;">
          <!-- Constraints Progress -->
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px;">
            <h5 style="font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">State After Selection</h5>
            <div style="display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 4px;">
              <span>Remaining Marks:</span>
              <strong>${state.remaining_marks} Marks</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 8px;">
              <span>Remaining Questions:</span>
              <strong>${state.remaining_count}</strong>
            </div>
            <div style="font-size: 11.5px; color: var(--text-muted);">
              Units: U1:${state.unit_counts[1]}, U2:${state.unit_counts[2]}, U3:${state.unit_counts[3]}, U4:${state.unit_counts[4]}, U5:${state.unit_counts[5]}
            </div>
          </div>

          <!-- Runner-ups Evaluated -->
          <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px;">
            <h5 style="font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">Runner-ups (Rejected at this step)</h5>
            ${(currentLog.runner_ups && currentLog.runner_ups.length > 0) ? `
              <div style="display: flex; flex-direction: column; gap: 8px;">
                ${currentLog.runner_ups.map(r => `
                  <div style="font-size: 12px; padding: 6px 8px; background: var(--bg-card-subtle); border-radius: var(--radius-sm);">
                    <div style="display: flex; justify-content: space-between; font-weight: 600;">
                      <span>#${r.id}: ${r.text}</span>
                      <span style="color: var(--primary);">${r.score}</span>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : '<p style="font-size: 12px; color: var(--text-muted);">No close contenders in this step.</p>'}
          </div>
        </div>
      </div>
    `;
  },

  // ==========================================
  // 2. BACKTRACKING TREE VISUALIZATION
  // ==========================================
  bindBacktrackControls() {
    document.getElementById('btnTreePlay')?.addEventListener('click', () => this.toggleTreePlay());
    document.getElementById('btnTreeNext')?.addEventListener('click', () => this.stepTree(1));
    document.getElementById('btnTreeReset')?.addEventListener('click', () => this.resetTree());
    document.getElementById('btnTreeFetchNew')?.addEventListener('click', () => this.fetchBacktrackingTrace());
  },

  async fetchBacktrackingTrace() {
    try {
      const res = await fetch('/api/algorithms/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'backtracking' })
      });
      const data = await res.json();
      if (data.success && data.search_tree) {
        this.treeLogs = data.search_tree;
        document.getElementById('treeStatesExplored').textContent = data.statistics.states_explored;
        document.getElementById('treeBranchesPruned').textContent = data.statistics.branches_pruned;
        document.getElementById('treeBacktracksCount').textContent = data.statistics.backtracks_count;
        this.resetTree();
      }
    } catch (err) {
      console.error('Failed to load backtracking trace:', err);
    }
  },

  resetTree() {
    this.pauseTree();
    this.treeStep = 0;
    this.renderTreeStep();
  },

  toggleTreePlay() {
    if (this.treePlaying) {
      this.pauseTree();
    } else {
      this.playTree();
    }
  },

  playTree() {
    this.treePlaying = true;
    const playBtn = document.getElementById('btnTreePlay');
    if (playBtn) playBtn.innerHTML = `<span>⏸ Pause</span>`;

    this.treeTimer = setInterval(() => {
      if (this.treeStep < this.treeLogs.length) {
        this.treeStep += 2; // Jump by 2 steps for snappy tree rendering
        if (this.treeStep > this.treeLogs.length) this.treeStep = this.treeLogs.length;
        this.renderTreeStep();
      } else {
        this.pauseTree();
      }
    }, this.treeSpeed);
  },

  pauseTree() {
    this.treePlaying = false;
    clearInterval(this.treeTimer);
    const playBtn = document.getElementById('btnTreePlay');
    if (playBtn) playBtn.innerHTML = `<span>▶ Play</span>`;
  },

  stepTree(direction) {
    this.pauseTree();
    const next = this.treeStep + direction;
    if (next >= 0 && next <= this.treeLogs.length) {
      this.treeStep = next;
      this.renderTreeStep();
    }
  },

  renderTreeStep() {
    const counter = document.getElementById('treeStepCounter');
    if (counter) counter.textContent = `Tree Event ${this.treeStep} of ${this.treeLogs.length}`;

    const container = document.getElementById('backtrackingStageContent');
    if (!container) return;

    if (this.treeStep === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-muted);">
          <h4>Backtracking State-Space Tree Initialized</h4>
          <p style="margin-top: 8px;">Root node ready. Press <strong>Play</strong> or <strong>Next Step</strong> to follow recursive decisions, branch pruning, and backtrack operations.</p>
        </div>
      `;
      return;
    }

    // Render tree events up to current step
    const visibleEvents = this.treeLogs.slice(Math.max(0, this.treeStep - 15), this.treeStep);

    container.innerHTML = `
      <div class="tree-container">
        ${visibleEvents.map((evt, idx) => {
          const actionClass = `action-${evt.action.toLowerCase()}`;
          const isLatest = (idx === visibleEvents.length - 1);
          return `
            <div class="tree-step-row ${actionClass} ${isLatest ? 'current-active' : ''}">
              <span style="font-weight: 700; min-width: 60px;">[Depth ${evt.depth}]</span>
              <span class="badge ${evt.action === 'SELECT' ? 'badge-easy' : (evt.action === 'PRUNE' ? 'badge-hard' : (evt.action === 'SOLUTION' ? 'badge-unit' : 'badge-medium'))}">
                ${evt.action}
              </span>
              <span style="flex: 1; color: var(--text-primary);">
                ${evt.question_id ? `<strong>Q#${evt.question_id}</strong>: ` : ''}${this.escapeHtml(evt.reason)}
              </span>
              <span style="font-size: 11px; color: var(--text-muted);">
                Marks: <strong>${evt.current_marks}</strong> | Count: <strong>${evt.current_count}</strong>
              </span>
            </div>
          `;
        }).join('')}
      </div>
    `;

    // Scroll container to bottom
    container.scrollTop = container.scrollHeight;
  },

  // ==========================================
  // 3. SORTING ALGORITHMS VISUALIZATION
  // ==========================================
  bindSortingControls() {
    document.getElementById('btnSortPlay')?.addEventListener('click', () => this.toggleSortPlay());
    document.getElementById('btnSortNext')?.addEventListener('click', () => this.stepSort(1));
    document.getElementById('btnSortReset')?.addEventListener('click', () => this.resetSort());
    
    ['sortAlgoSelect', 'sortKeySelect'].forEach(id => {
      document.getElementById(id)?.addEventListener('change', () => this.fetchSortingTrace());
    });

    document.getElementById('btnRunAllSortBenchmarks')?.addEventListener('click', () => this.runAllSortBenchmarks());
  },

  async fetchSortingTrace() {
    const algo = document.getElementById('sortAlgoSelect')?.value || 'bubble';
    const key = document.getElementById('sortKeySelect')?.value || 'marks';

    try {
      const res = await fetch('/api/algorithms/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'sorting', algorithm: algo, key: key })
      });
      const data = await res.json();
      if (data.success) {
        this.sortSteps = data.steps || [];
        this.sortCurrentArray = [...data.initial_array];
        this.sortInitialArray = [...data.initial_array];
        this.sortQuestions = data.questions || [];

        document.getElementById('sortComparisonsVal').textContent = data.metrics.comparisons;
        document.getElementById('sortSwapsVal').textContent = data.metrics.swaps;
        document.getElementById('sortTimeVal').textContent = `${data.metrics.execution_time_ms} ms`;
        document.getElementById('sortComplexityVal').textContent = data.metrics.time_complexity;

        this.resetSort();
      }
    } catch (err) {
      console.error('Failed to load sorting trace:', err);
    }
  },

  resetSort() {
    this.pauseSort();
    this.sortStepIndex = 0;
    this.sortCurrentArray = [...(this.sortInitialArray || [])];
    this.renderSortBars([], 'default');
  },

  toggleSortPlay() {
    if (this.sortPlaying) {
      this.pauseSort();
    } else {
      this.playSort();
    }
  },

  playSort() {
    this.sortPlaying = true;
    const playBtn = document.getElementById('btnSortPlay');
    if (playBtn) playBtn.innerHTML = `<span>⏸ Pause</span>`;

    this.sortTimer = setInterval(() => {
      if (this.sortStepIndex < this.sortSteps.length) {
        this.stepSort(1);
      } else {
        this.pauseSort();
        this.renderSortBars([], 'sorted');
      }
    }, this.sortSpeed);
  },

  pauseSort() {
    this.sortPlaying = false;
    clearInterval(this.sortTimer);
    const playBtn = document.getElementById('btnSortPlay');
    if (playBtn) playBtn.innerHTML = `<span>▶ Play</span>`;
  },

  stepSort(direction) {
    if (direction > 0 && this.sortStepIndex < this.sortSteps.length) {
      const step = this.sortSteps[this.sortStepIndex];
      this.sortCurrentArray = [...step.array];
      this.renderSortBars(step.indices, step.type);
      this.sortStepIndex++;
    } else if (direction < 0 && this.sortStepIndex > 0) {
      this.sortStepIndex--;
      const step = this.sortSteps[this.sortStepIndex];
      this.sortCurrentArray = [...step.array];
      this.renderSortBars(step.indices, step.type);
    }
    document.getElementById('sortStepCounter').textContent = `Step ${this.sortStepIndex} / ${this.sortSteps.length}`;
  },

  renderSortBars(activeIndices = [], type = 'default') {
    const container = document.getElementById('sortingBarsContainer');
    if (!container) return;

    const maxVal = Math.max(...this.sortCurrentArray, 20);

    container.innerHTML = this.sortCurrentArray.map((val, idx) => {
      const heightPercent = Math.max(12, Math.round((val / maxVal) * 100));
      let barClass = 'sort-bar';
      if (type === 'compare' && activeIndices.includes(idx)) barClass += ' comparing';
      if ((type === 'swap' || type === 'overwrite') && activeIndices.includes(idx)) barClass += ' swapping';
      if (type === 'sorted') barClass += ' sorted';

      return `
        <div class="sort-bar-column">
          <div class="${barClass}" style="height: ${heightPercent}%;">
            ${val}
          </div>
          <span class="bar-label">#${idx + 1}</span>
        </div>
      `;
    }).join('');
  },

  async runAllSortBenchmarks() {
    const key = document.getElementById('sortKeySelect')?.value || 'marks';
    const tbody = document.getElementById('sortBenchmarkTableBody');
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">Running high-resolution benchmarks across all 5 algorithms...</td></tr>`;

    try {
      const res = await fetch('/api/algorithms/sort', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithm: 'all', key: key })
      });
      const data = await res.json();
      if (data.success && data.benchmarks) {
        tbody.innerHTML = data.benchmarks.map(b => `
          <tr>
            <td><strong>${b.algorithm}</strong></td>
            <td>${b.input_size}</td>
            <td><strong style="color:var(--primary);">${b.comparisons}</strong></td>
            <td>${b.swaps}</td>
            <td><strong>${b.execution_time_ms} ms</strong></td>
            <td><span class="badge badge-unit">${b.time_complexity}</span></td>
            <td><span class="badge badge-neutral">${b.stability}</span></td>
          </tr>
        `).join('');
        App.showToast('Sorting benchmark executed on full question bank!', 'success');
      }
    } catch (err) {
      App.showToast('Benchmark run failed', 'error');
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

window.VisualizerView = VisualizerView;
