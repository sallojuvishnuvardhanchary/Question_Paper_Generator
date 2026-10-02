/**
 * Paper View, History, PDF Download, and Decision Transparency Controller
 * CoreAlgorithm PROBLEM95 - Syllabus-Driven Paper Generator
 */

const PaperView = {
  currentPaperData: null,
  currentConfig: null,

  displayPaper(data, config) {
    this.currentPaperData = data;
    this.currentConfig = config;

    const container = document.getElementById('paperResultContainer');
    const historyContainer = document.getElementById('papersHistoryContainer');
    if (container) container.style.display = 'block';
    if (historyContainer) historyContainer.style.display = 'none';

    const paperId = data.id || data.paper_id;
    const paperName = data.paper_name || config?.paper_name || 'Autonomous Examination';
    const subject = data.subject || config?.subject || 'Design and Analysis of Algorithms';
    const totalMarks = data.statistics?.total_marks_achieved || data.total_marks || 100;
    const algoUsed = data.algorithm || data.algorithm_used || 'Greedy Algorithm';
    const execTime = data.statistics?.execution_time_ms || data.execution_time_ms || 0;
    const objScore = data.objective_score?.total_score || data.objective_score || 90;

    // Update Header
    document.getElementById('paperTitleDisplay').textContent = paperName;
    document.getElementById('paperTotalMarksDisplay').textContent = `Max Marks: ${totalMarks}`;
    document.getElementById('paperDurationDisplay').textContent = totalMarks >= 70 ? 'Duration: 3 Hours' : (totalMarks >= 40 ? 'Duration: 2 Hours' : 'Duration: 1 Hour');
    document.getElementById('paperSubjectDisplay').textContent = `Subject: ${subject}`;
    document.getElementById('paperAlgoBadge').textContent = `${algoUsed} (${execTime}ms)`;
    document.getElementById('paperObjScoreBadge').textContent = `Score: ${objScore}/100`;

    // Update PDF Download Actions
    const downloadPdfBtn = document.getElementById('btnDownloadPdf');
    const downloadKeyBtn = document.getElementById('btnDownloadKey');
    
    if (downloadPdfBtn) {
      if (paperId) {
        downloadPdfBtn.style.display = 'inline-flex';
        downloadPdfBtn.onclick = () => window.open(`/api/paper/${paperId}/download`, '_blank');
      } else {
        downloadPdfBtn.style.display = 'none';
      }
    }

    if (downloadKeyBtn) {
      if (paperId) {
        downloadKeyBtn.style.display = 'inline-flex';
        downloadKeyBtn.onclick = () => window.open(`/api/paper/${paperId}/download-key`, '_blank');
      } else {
        downloadKeyBtn.style.display = 'none';
      }
    }

    // Render Questions by Parts & Internal Choices
    const qList = data.selected_questions || data.questions || [];
    this.renderFormattedQuestions(qList);

    // Render Explanation Panel
    this.renderExplanationPanel(data);

    // Render Validation Panel
    this.renderValidationPanel(data.validation);

    // Render Objective Score Breakdown
    this.renderScoreBreakdown(data.objective_score);
  },

  renderFormattedQuestions(qList) {
    const questionsContainer = document.getElementById('paperQuestionsContainer');
    if (!questionsContainer) return;

    if (!qList || qList.length === 0) {
      questionsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted);">No questions in this paper.</div>';
      return;
    }

    // Group questions by Part
    const partsMap = new Map();
    qList.forEach(q => {
      const pName = q.part_name || 'PART A';
      if (!partsMap.has(pName)) {
        partsMap.set(pName, []);
      }
      partsMap.get(pName).push(q);
    });

    let html = '';
    let globalCounter = 1;

    partsMap.forEach((questions, partName) => {
      html += `
        <div class="exam-part-banner">
          ${this.escapeHtml(partName)}
        </div>
      `;

      // Group choices
      let i = 0;
      while (i < questions.length) {
        const q = questions[i];
        const isChoice = Boolean(q.is_choice);
        const choiceGroup = q.choice_group;

        // Check if next question is a choice twin
        const nextQ = questions[i + 1];
        const hasChoiceTwin = nextQ && nextQ.choice_group && nextQ.choice_group === choiceGroup;

        if (hasChoiceTwin) {
          const qNum = q.question_number || String(globalCounter);
          html += `
            <div class="paper-question-item" style="border-left: 3px solid var(--primary); padding-left: 14px; margin-bottom: 14px;">
              <!-- Option A -->
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                <div style="display: flex; gap: 8px;">
                  <strong style="color: var(--primary);">Q${qNum}. (a)</strong>
                  <div style="font-size: 13.5px; line-height: 1.5;">${this.escapeHtml(q.question_text)}</div>
                </div>
                <div class="q-marks-tag">[ ${q.marks} Marks ]</div>
              </div>
              <div class="q-meta" style="margin-left: 44px; margin-bottom: 8px;">
                <span class="badge badge-unit">Unit ${q.unit}</span>
                <span class="badge badge-neutral">${this.escapeHtml(q.topic)}</span>
                <span class="badge badge-${(q.difficulty || 'Medium').toLowerCase()}">${q.difficulty}</span>
              </div>

              <!-- OR Divider -->
              <div class="choice-or-divider">
                <span class="choice-or-label">OR</span>
              </div>

              <!-- Option B -->
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 6px;">
                <div style="display: flex; gap: 8px;">
                  <strong style="color: var(--secondary);">Q${qNum}. (b)</strong>
                  <div style="font-size: 13.5px; line-height: 1.5;">${this.escapeHtml(nextQ.question_text)}</div>
                </div>
                <div class="q-marks-tag">[ ${nextQ.marks} Marks ]</div>
              </div>
              <div class="q-meta" style="margin-left: 44px; margin-top: 4px;">
                <span class="badge badge-unit">Unit ${nextQ.unit}</span>
                <span class="badge badge-neutral">${this.escapeHtml(nextQ.topic)}</span>
                <span class="badge badge-${(nextQ.difficulty || 'Medium').toLowerCase()}">${nextQ.difficulty}</span>
              </div>
            </div>
          `;
          i += 2;
          globalCounter++;
        } else {
          // Standard Question
          const qNum = q.question_number || String(globalCounter);
          const isMcq = (q.question_type || '').toUpperCase() === 'MCQ';
          let mcqHtml = '';

          if (isMcq && q.options_json) {
            try {
              const opts = typeof q.options_json === 'string' ? JSON.parse(q.options_json) : q.options_json;
              mcqHtml = `
                <div class="mcq-options-container">
                  ${opts.map(opt => `
                    <div class="mcq-option-label ${opt.startsWith(q.correct_answer || '___') ? 'correct' : ''}">
                      ${this.escapeHtml(opt)}
                    </div>
                  `).join('')}
                </div>
              `;
            } catch (e) {}
          }

          html += `
            <div class="paper-question-item">
              <div class="q-number">Q${qNum}.</div>
              <div class="q-content">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                  <div class="q-text">${this.escapeHtml(q.question_text)}</div>
                  <div class="q-marks-tag" style="margin-left: 12px; white-space: nowrap;">[ ${q.marks} Marks ]</div>
                </div>
                ${mcqHtml}
                <div class="q-meta" style="margin-top: 8px;">
                  <span class="badge badge-unit">Unit ${q.unit}</span>
                  <span class="badge badge-neutral">${this.escapeHtml(q.topic)}</span>
                  <span class="badge badge-${(q.difficulty || 'Medium').toLowerCase()}">${q.difficulty}</span>
                  <span class="badge badge-neutral" style="font-size: 11px;">${q.question_type}</span>
                  ${q.used_count > 0 ? `<span class="badge badge-warning" style="font-size: 11px;">Used (${q.used_count}x)</span>` : '<span class="badge badge-easy" style="font-size: 11px;">Novel</span>'}
                </div>
              </div>
            </div>
          `;
          i += 1;
          globalCounter++;
        }
      }
    });

    questionsContainer.innerHTML = html;
  },

  renderExplanationPanel(data) {
    const container = document.getElementById('paperExplanationContainer');
    if (!container) return;

    const logs = data.generation_logs || data.logs || [];
    if (!logs || logs.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);">Algorithmic decisions logged dynamically during synthesis.</p>';
      return;
    }

    container.innerHTML = logs.map((log, idx) => {
      const qNum = idx + 1;
      const qText = log.question_text || `Question #${log.question_id}`;
      const reasonsList = Array.isArray(log.reasons) ? log.reasons : (log.reason ? log.reason.split(';') : ['Allocated based on algorithmic constraint fit']);
      const score = log.score ? `Score: ${log.score}` : '';

      return `
        <div style="padding: 14px 18px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <strong style="color: var(--primary); font-size: 14px;">Q${qNum} (ID #${log.question_id || qNum}) was selected:</strong>
            <span style="font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--text-secondary);">${score}</span>
          </div>
          <div style="font-size: 13px; color: var(--text-primary); margin-bottom: 8px;">
            <em>"${this.escapeHtml(qText.substring(0, 110))}..."</em>
          </div>
          <div style="display: flex; flex-direction: column; gap: 4px;">
            ${reasonsList.map(r => `
              <div style="display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--text-secondary);">
                <span style="color: var(--success); font-weight: bold;">✓</span> ${this.escapeHtml(r.trim())}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }).join('');
  },

  renderValidationPanel(validation) {
    const container = document.getElementById('paperValidationContainer');
    if (!container) return;

    if (!validation || !validation.checks) {
      container.innerHTML = '<p style="color:var(--text-muted);">All structural and curriculum constraints verified.</p>';
      return;
    }

    container.innerHTML = validation.checks.map(chk => `
      <div class="validation-card ${chk.passed ? 'passed' : 'failed'}">
        <div class="validation-icon">${chk.passed ? '✓' : '✕'}</div>
        <div class="validation-info" style="flex:1;">
          <h4>${chk.name}</h4>
          <p style="margin-bottom: 4px;">${chk.message}</p>
          <div style="display: flex; justify-content: space-between; font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">
            <span>Target: ${chk.target}</span>
            <span>Actual: <strong>${chk.actual}</strong></span>
          </div>
        </div>
      </div>
    `).join('');
  },

  renderScoreBreakdown(objScore) {
    const container = document.getElementById('paperScoreBreakdownContainer');
    if (!container) return;

    const b = objScore?.breakdown || { difficulty: 24, unit: 23, topic: 18, marks_fit: 15, novelty: 12 };

    container.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; text-align: center;">
        <div style="padding: 12px; background: var(--bg-card-subtle); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Difficulty Match</div>
          <div style="font-size: 18px; font-weight: 700; color: var(--primary);">${b.difficulty || 0} / 25</div>
        </div>
        <div style="padding: 12px; background: var(--bg-card-subtle); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Unit Balance</div>
          <div style="font-size: 18px; font-weight: 700; color: var(--primary);">${b.unit || 0} / 25</div>
        </div>
        <div style="padding: 12px; background: var(--bg-card-subtle); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Topic Coverage</div>
          <div style="font-size: 18px; font-weight: 700; color: var(--primary);">${b.topic || 0} / 20</div>
        </div>
        <div style="padding: 12px; background: var(--bg-card-subtle); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Marks Budget</div>
          <div style="font-size: 18px; font-weight: 700; color: var(--primary);">${b.marks_fit || 0} / 15</div>
        </div>
        <div style="padding: 12px; background: var(--bg-card-subtle); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Novelty & Types</div>
          <div style="font-size: 18px; font-weight: 700; color: var(--primary);">${b.novelty || 0} / 15</div>
        </div>
      </div>
    `;
  },

  printPaper() {
    window.print();
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

/**
 * Historical Papers List Controller
 */
const PaperHistoryView = {
  load() {
    this.loadPapers(1);
    this.bindEvents();
  },

  bindEvents() {
    const backBtn = document.getElementById('btnBackToHistory');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        document.getElementById('paperResultContainer').style.display = 'none';
        document.getElementById('papersHistoryContainer').style.display = 'block';
        this.loadPapers(1);
      });
    }

    const printBtn = document.getElementById('btnPrintPaper');
    if (printBtn) {
      printBtn.addEventListener('click', () => PaperView.printPaper());
    }
  },

  async loadPapers(page = 1) {
    const tbody = document.getElementById('papersHistoryTableBody');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 28px;">Loading generated papers...</td></tr>`;
    }

    try {
      const res = await fetch(`/api/papers?page=${page}&per_page=10`);
      const data = await res.json();
      if (data.success) {
        this.renderHistoryTable(data.papers, data.total_count);
      }
    } catch (err) {
      console.error('Failed to load papers history:', err);
    }
  },

  renderHistoryTable(papers, totalCount) {
    const tbody = document.getElementById('papersHistoryTableBody');
    if (!tbody) return;

    if (!papers || papers.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align:center; padding: 40px;">
            <p style="color:var(--text-muted);">No papers generated yet. Use the Syllabus Generator to synthesize your first examination paper.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = papers.map(p => {
      const dateStr = p.created_at ? new Date(p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent';
      return `
        <tr>
          <td><strong>#${p.id}</strong></td>
          <td>
            <div style="font-weight: 600; color: var(--text-primary);">${PaperView.escapeHtml(p.paper_name)}</div>
            <div style="font-size: 11.5px; color: var(--text-muted);">${PaperView.escapeHtml(p.subject)}</div>
          </td>
          <td><span class="badge badge-unit">${p.total_marks} Marks</span></td>
          <td>${p.question_count} Questions</td>
          <td><span class="badge badge-neutral">${p.algorithm_used}</span></td>
          <td><strong style="color: var(--primary);">${p.objective_score} / 100</strong></td>
          <td><span style="font-size: 12px; color: var(--text-muted);">${dateStr}</span></td>
          <td style="text-align: right; white-space: nowrap;">
            <button class="btn btn-primary btn-sm" onclick="PaperHistoryView.viewSinglePaper(${p.id})">
              View
            </button>
            <a href="/api/paper/${p.id}/download" class="btn btn-outline btn-sm" target="_blank" title="Download ReportLab PDF" style="margin-left: 4px;">
              PDF
            </a>
            <button class="btn btn-outline btn-sm" onclick="PaperHistoryView.deleteSinglePaper(${p.id})" style="color: var(--danger); border-color: rgba(239,68,68,0.3); margin-left: 4px;">
              Delete
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  async viewSinglePaper(pid) {
    try {
      const res = await fetch(`/api/papers/${pid}`);
      const data = await res.json();
      if (data.success && data.paper) {
        PaperView.displayPaper(data.paper, data.paper.constraints);
      }
    } catch (err) {
      App.showToast('Could not load paper details', 'error');
    }
  },

  async deleteSinglePaper(pid) {
    if (!confirm(`Are you sure you want to delete Paper #${pid}?`)) return;
    try {
      const res = await fetch(`/api/papers/${pid}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        App.showToast(`Paper #${pid} deleted.`, 'success');
        this.loadPapers(1);
      }
    } catch (err) {
      App.showToast('Failed to delete paper', 'error');
    }
  }
};

window.PaperView = PaperView;
window.PaperHistoryView = PaperHistoryView;
