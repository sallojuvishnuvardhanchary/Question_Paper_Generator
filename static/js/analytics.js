/**
 * Deep Analytics and Dashboard Charts Module
 * CoreAlgorithm PROBLEM95
 * Integrates SQLite data with Chart.js charts.
 */

const AnalyticsView = {
  charts: {},
  cachedData: null,

  async load() {
    try {
      const res = await fetch('/api/analytics');
      const data = await res.json();
      if (data.success) {
        this.cachedData = data;
        this.renderStats(data);
        this.renderCharts();
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  },

  renderStats(data) {
    const qStats = data.question_stats;
    const pStats = data.paper_stats;

    // KPI values
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    setVal('analyticsTotalQuestions', qStats.total_questions);
    setVal('analyticsEasyQuestions', qStats.easy_count);
    setVal('analyticsMediumQuestions', qStats.medium_count);
    setVal('analyticsHardQuestions', qStats.hard_count);
    setVal('analyticsTotalPapers', pStats.total_papers);
    setVal('analyticsAvgScore', `${pStats.average_objective_score} / 100`);
    setVal('analyticsUsedQuestions', qStats.questions_used);
    setVal('analyticsAvailableQuestions', qStats.questions_available);

    // Most used questions table
    const mostUsedTbody = document.getElementById('analyticsMostUsedTable');
    if (mostUsedTbody && qStats.most_used) {
      mostUsedTbody.innerHTML = qStats.most_used.map(q => `
        <tr>
          <td><strong>#${q.id}</strong></td>
          <td style="max-width: 260px;">${q.question_text.substring(0, 75)}...</td>
          <td><span class="badge badge-unit">Unit ${q.unit}</span></td>
          <td><span class="badge badge-${q.difficulty.toLowerCase()}">${q.difficulty}</span></td>
          <td><strong style="color:var(--warning-text);">${q.used_count} times</strong></td>
        </tr>
      `).join('');
    }
  },

  renderCharts() {
    if (!this.cachedData || typeof Chart === 'undefined') return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#CBD5E1' : '#475569';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(226, 232, 240, 0.6)';

    const qStats = this.cachedData.question_stats;
    const pStats = this.cachedData.paper_stats;

    // 1. Difficulty Donut Chart
    const diffCtx = document.getElementById('chartDifficultyDonut')?.getContext('2d');
    if (diffCtx) {
      if (this.charts.diff) this.charts.diff.destroy();
      this.charts.diff = new Chart(diffCtx, {
        type: 'doughnut',
        data: {
          labels: ['Easy', 'Medium', 'Hard'],
          datasets: [{
            data: [qStats.easy_count, qStats.medium_count, qStats.hard_count],
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
            borderColor: isDark ? '#1E293B' : '#FFFFFF',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: textColor, font: { family: 'inherit', size: 12 } } }
          }
        }
      });
    }

    // 2. Unit Distribution Bar Chart
    const unitCtx = document.getElementById('chartUnitBar')?.getContext('2d');
    if (unitCtx) {
      if (this.charts.unit) this.charts.unit.destroy();
      this.charts.unit = new Chart(unitCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(qStats.unit_counts),
          datasets: [{
            label: 'Questions Count',
            data: Object.values(qStats.unit_counts),
            backgroundColor: '#3B82F6',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: textColor }, grid: { color: gridColor } },
            y: { ticks: { color: textColor, stepSize: 2 }, grid: { color: gridColor } }
          }
        }
      });
    }

    // 3. Marks Distribution Bar Chart
    const marksCtx = document.getElementById('chartMarksBar')?.getContext('2d');
    if (marksCtx) {
      if (this.charts.marks) this.charts.marks.destroy();
      this.charts.marks = new Chart(marksCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(qStats.marks_counts),
          datasets: [{
            label: 'Questions by Marks',
            data: Object.values(qStats.marks_counts),
            backgroundColor: '#818CF8',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: textColor }, grid: { color: gridColor } },
            y: { ticks: { color: textColor, stepSize: 2 }, grid: { color: gridColor } }
          }
        }
      });
    }

    // 4. Topic Distribution Horizontal Bar Chart
    const topicCtx = document.getElementById('chartTopicBar')?.getContext('2d');
    if (topicCtx) {
      if (this.charts.topic) this.charts.topic.destroy();
      this.charts.topic = new Chart(topicCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(qStats.topic_counts),
          datasets: [{
            label: 'Topic Count',
            data: Object.values(qStats.topic_counts),
            backgroundColor: '#0EA5E9',
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: textColor, stepSize: 2 }, grid: { color: gridColor } },
            y: { ticks: { color: textColor }, grid: { color: gridColor } }
          }
        }
      });
    }

    // 5. Algorithm Usage Pie Chart
    const algoCtx = document.getElementById('chartAlgoUsagePie')?.getContext('2d');
    if (algoCtx && pStats.algorithm_distribution) {
      if (this.charts.algo) this.charts.algo.destroy();
      const labels = Object.keys(pStats.algorithm_distribution);
      const vals = Object.values(pStats.algorithm_distribution);
      this.charts.algo = new Chart(algoCtx, {
        type: 'pie',
        data: {
          labels: labels.length > 0 ? labels : ['Greedy', 'Backtracking'],
          datasets: [{
            data: vals.length > 0 ? vals : [1, 1],
            backgroundColor: ['#2563EB', '#818CF8'],
            borderColor: isDark ? '#1E293B' : '#FFFFFF',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: textColor, font: { family: 'inherit', size: 12 } } }
          }
        }
      });
    }
  }
};

/**
 * Dashboard Overview Controller
 */
const DashboardView = {
  async load() {
    try {
      const res = await fetch('/api/analytics');
      const data = await res.json();
      if (data.success) {
        this.renderStats(data);
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  },

  renderStats(data) {
    const q = data.question_stats;
    const p = data.paper_stats;

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    setVal('dashTotalQuestions', q.total_questions);
    setVal('dashEasyQuestions', q.easy_count);
    setVal('dashMediumQuestions', q.medium_count);
    setVal('dashHardQuestions', q.hard_count);
    setVal('dashTotalUnits', q.total_units);
    setVal('dashTotalTopics', q.total_topics);
    setVal('dashPapersGenerated', p.total_papers);
    setVal('dashQuestionsUsed', q.questions_used);
    setVal('dashQuestionsAvailable', q.questions_available);

    // Recent papers table
    const tbody = document.getElementById('dashRecentPapersTable');
    if (tbody) {
      if (p.recent_papers && p.recent_papers.length > 0) {
        tbody.innerHTML = p.recent_papers.map(rp => `
          <tr>
            <td><strong>#${rp.id}</strong></td>
            <td><strong>${rp.paper_name}</strong></td>
            <td><span class="badge badge-unit">${rp.total_marks} Marks</span></td>
            <td>${rp.question_count} Qs</td>
            <td><span class="badge badge-neutral">${rp.algorithm_used}</span></td>
            <td><strong style="color:var(--primary);">${rp.objective_score} / 100</strong></td>
            <td><span class="badge badge-easy">${rp.status}</span></td>
            <td style="text-align: right;">
              <button class="btn btn-outline btn-sm" onclick="App.switchView('papers'); PaperHistoryView.viewSinglePaper(${rp.id});">
                View
              </button>
            </td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 24px; color:var(--text-muted);">No papers generated yet. Click "Generate Question Paper" to start.</td></tr>`;
      }
    }
  }
};

/**
 * Settings & System Reset Controller
 */
const SettingsView = {
  load() {
    document.getElementById('btnResetDatabase')?.addEventListener('click', () => {
      if (confirm('Are you sure you want to reset the database? This will clear all history and restore 80 default questions.')) {
        this.resetDatabase();
      }
    });
  },

  async resetDatabase() {
    try {
      const res = await fetch('/api/system/reset-seed', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        App.showToast(data.message, 'success');
        if (window.QuestionBank) window.QuestionBank.loadQuestions(1);
      } else {
        App.showToast(data.error || 'Reset failed', 'error');
      }
    } catch (err) {
      App.showToast('Server communication error', 'error');
    }
  }
};

window.AnalyticsView = AnalyticsView;
window.DashboardView = DashboardView;
window.SettingsView = SettingsView;
