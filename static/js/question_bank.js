/**
 * Question Bank CRUD and Filtering Module
 * CoreAlgorithm PROBLEM95
 */

const QuestionBank = {
  currentPage: 1,
  perPage: 10,
  totalPages: 1,
  currentSortBy: 'id',
  currentSortOrder: 'asc',
  metadata: null,
  activeQuestionId: null,

  init() {
    this.loadMetadata();
    this.loadQuestions(1);
    this.bindEvents();
  },

  bindEvents() {
    // Search input with debounce
    const searchInput = document.getElementById('qSearchInput');
    if (searchInput) {
      let timeout = null;
      searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => this.loadQuestions(1), 300);
      });
    }

    // Filter dropdowns
    ['qFilterUnit', 'qFilterDifficulty', 'qFilterMarks', 'qFilterTopic', 'qFilterType'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', () => this.loadQuestions(1));
      }
    });

    // Reset filters
    const resetBtn = document.getElementById('qResetFiltersBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        document.getElementById('qSearchInput').value = '';
        document.getElementById('qFilterUnit').value = 'all';
        document.getElementById('qFilterDifficulty').value = 'all';
        document.getElementById('qFilterMarks').value = 'all';
        document.getElementById('qFilterTopic').value = 'all';
        document.getElementById('qFilterType').value = 'all';
        this.loadQuestions(1);
      });
    }

    // Sort column headers
    document.querySelectorAll('.sortable-th').forEach(th => {
      th.addEventListener('click', () => {
        const col = th.getAttribute('data-sort');
        if (this.currentSortBy === col) {
          this.currentSortOrder = this.currentSortOrder === 'asc' ? 'desc' : 'asc';
        } else {
          this.currentSortBy = col;
          this.currentSortOrder = 'asc';
        }
        this.updateSortHeaders();
        this.loadQuestions(1);
      });
    });

    // Add question form submit
    const addForm = document.getElementById('addQuestionForm');
    if (addForm) {
      addForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.saveQuestion();
      });
    }

    // Confirm delete
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener('click', () => {
        if (this.activeQuestionId) {
          this.executeDelete(this.activeQuestionId);
        }
      });
    }
  },

  updateSortHeaders() {
    document.querySelectorAll('.sortable-th').forEach(th => {
      const col = th.getAttribute('data-sort');
      const icon = th.querySelector('.sort-icon');
      if (col === this.currentSortBy) {
        th.classList.add('sorted');
        if (icon) icon.textContent = this.currentSortOrder === 'asc' ? '▲' : '▼';
      } else {
        th.classList.remove('sorted');
        if (icon) icon.textContent = '⇅';
      }
    });
  },

  async loadMetadata() {
    try {
      const res = await fetch('/api/questions/meta');
      const data = await res.json();
      if (data.success) {
        this.metadata = data;
        this.populateDropdowns(data);
      }
    } catch (err) {
      console.error('Failed to load questions metadata:', err);
    }
  },

  populateDropdowns(meta) {
    const topicSelect = document.getElementById('qFilterTopic');
    if (topicSelect && meta.topics) {
      topicSelect.innerHTML = '<option value="all">All Topics</option>';
      meta.topics.forEach(t => {
        topicSelect.innerHTML += `<option value="${t}">${t}</option>`;
      });
    }

    const marksSelect = document.getElementById('qFilterMarks');
    if (marksSelect && meta.marks) {
      marksSelect.innerHTML = '<option value="all">All Marks</option>';
      meta.marks.forEach(m => {
        marksSelect.innerHTML += `<option value="${m}">${m} Marks</option>`;
      });
    }
  },

  async loadQuestions(page = 1) {
    this.currentPage = page;
    const search = document.getElementById('qSearchInput')?.value || '';
    const unit = document.getElementById('qFilterUnit')?.value || 'all';
    const difficulty = document.getElementById('qFilterDifficulty')?.value || 'all';
    const marks = document.getElementById('qFilterMarks')?.value || 'all';
    const topic = document.getElementById('qFilterTopic')?.value || 'all';
    const qType = document.getElementById('qFilterType')?.value || 'all';

    const params = new URLSearchParams({
      page: page,
      per_page: this.perPage,
      sort_by: this.currentSortBy,
      sort_order: this.currentSortOrder
    });

    if (search.trim()) params.append('search', search.trim());
    if (unit !== 'all') params.append('unit', unit);
    if (difficulty !== 'all') params.append('difficulty', difficulty);
    if (marks !== 'all') params.append('marks', marks);
    if (topic !== 'all') params.append('topic', topic);
    if (qType !== 'all') params.append('question_type', qType);

    const tbody = document.getElementById('questionsTableBody');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 32px;"><span style="color:var(--text-muted);">Loading questions...</span></td></tr>`;
    }

    try {
      const res = await fetch(`/api/questions?${params.toString()}`);
      const data = await res.json();

      if (data.success) {
        this.totalPages = data.total_pages;
        this.renderTable(data.questions, data.total_count);
        this.renderPagination(data.total_count);
      } else {
        App.showToast(data.error || 'Failed to fetch questions', 'error');
      }
    } catch (err) {
      console.error('Error loading questions:', err);
      App.showToast('Network error while fetching questions', 'error');
    }
  },

  renderTable(questions, totalCount) {
    const tbody = document.getElementById('questionsTableBody');
    const countLabel = document.getElementById('qTotalCountDisplay');
    if (countLabel) countLabel.textContent = `${totalCount} questions found`;

    if (!tbody) return;

    if (!questions || questions.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 40px;">
            <p style="font-weight: 500; color: var(--text-muted);">No questions match the current filters.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = questions.map(q => {
      const diffClass = q.difficulty.toLowerCase();
      return `
        <tr>
          <td><strong style="font-family: var(--font-mono); color: var(--primary);">#${q.id}</strong></td>
          <td style="max-width: 320px;">
            <div style="font-weight: 500; line-height: 1.4; color: var(--text-primary); margin-bottom: 4px;">
              ${this.escapeHtml(q.question_text)}
            </div>
            ${q.tags ? `<span style="font-size: 11px; color: var(--text-muted);">${this.escapeHtml(q.tags)}</span>` : ''}
          </td>
          <td><span class="badge badge-unit">Unit ${q.unit}</span></td>
          <td><span style="font-weight: 500;">${this.escapeHtml(q.topic)}</span></td>
          <td><span class="badge badge-${diffClass}">${q.difficulty}</span></td>
          <td><span class="badge badge-marks">${q.marks}M</span></td>
          <td><span class="badge badge-neutral">${q.question_type}</span></td>
          <td style="text-align: center;">
            <span style="font-weight: ${q.used_count > 0 ? '700' : 'normal'}; color: ${q.used_count > 0 ? 'var(--warning-text)' : 'var(--text-muted)'};">
              ${q.used_count}x
            </span>
          </td>
          <td style="white-space: nowrap; text-align: right;">
            <button class="btn btn-outline btn-sm" onclick="QuestionBank.openEditModal(${q.id})" title="Edit Question" style="margin-right: 4px;">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="btn btn-outline btn-sm" onclick="QuestionBank.confirmDelete(${q.id})" title="Delete Question" style="color: var(--danger); border-color: rgba(239,68,68,0.3);">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  renderPagination(totalCount) {
    const container = document.getElementById('qPaginationContainer');
    if (!container) return;

    if (this.totalPages <= 1) {
      container.innerHTML = `<span>Showing all ${totalCount} questions</span>`;
      return;
    }

    const start = (this.currentPage - 1) * this.perPage + 1;
    const end = Math.min(this.currentPage * this.perPage, totalCount);

    let buttonsHtml = '';
    buttonsHtml += `<button class="page-btn" ${this.currentPage === 1 ? 'disabled' : ''} onclick="QuestionBank.loadQuestions(${this.currentPage - 1})">Prev</button>`;

    for (let p = 1; p <= this.totalPages; p++) {
      if (p === 1 || p === this.totalPages || (p >= this.currentPage - 1 && p <= this.currentPage + 1)) {
        buttonsHtml += `<button class="page-btn ${p === this.currentPage ? 'active' : ''}" onclick="QuestionBank.loadQuestions(${p})">${p}</button>`;
      } else if (p === this.currentPage - 2 || p === this.currentPage + 2) {
        buttonsHtml += `<span style="padding: 0 4px; color: var(--text-muted);">...</span>`;
      }
    }

    buttonsHtml += `<button class="page-btn" ${this.currentPage === this.totalPages ? 'disabled' : ''} onclick="QuestionBank.loadQuestions(${this.currentPage + 1})">Next</button>`;

    container.innerHTML = `
      <span>Showing ${start} – ${end} of ${totalCount} questions</span>
      <div class="pagination-controls">${buttonsHtml}</div>
    `;
  },

  openAddModal() {
    this.activeQuestionId = null;
    document.getElementById('modalQuestionTitle').textContent = 'Add New Question';
    document.getElementById('addQuestionForm').reset();
    document.getElementById('formQuestionId').value = '';
    App.openModal('questionModal');
  },

  async openEditModal(qid) {
    this.activeQuestionId = qid;
    document.getElementById('modalQuestionTitle').textContent = `Edit Question #${qid}`;
    try {
      const res = await fetch(`/api/questions/${qid}`);
      const data = await res.json();
      if (data.success && data.question) {
        const q = data.question;
        document.getElementById('formQuestionId').value = q.id;
        document.getElementById('formQuestionText').value = q.question_text;
        document.getElementById('formUnit').value = q.unit;
        document.getElementById('formTopic').value = q.topic;
        document.getElementById('formDifficulty').value = q.difficulty;
        document.getElementById('formMarks').value = q.marks;
        document.getElementById('formQuestionType').value = q.question_type;
        document.getElementById('formTags').value = q.tags || '';
        document.getElementById('formUsedCount').value = q.used_count || 0;
        App.openModal('questionModal');
      }
    } catch (err) {
      App.showToast('Could not load question details', 'error');
    }
  },

  async saveQuestion() {
    const qid = document.getElementById('formQuestionId').value;
    const payload = {
      question_text: document.getElementById('formQuestionText').value.trim(),
      subject: 'Design and Analysis of Algorithms',
      unit: parseInt(document.getElementById('formUnit').value),
      topic: document.getElementById('formTopic').value.trim(),
      difficulty: document.getElementById('formDifficulty').value,
      marks: parseInt(document.getElementById('formMarks').value),
      question_type: document.getElementById('formQuestionType').value,
      tags: document.getElementById('formTags').value.trim(),
      used_count: parseInt(document.getElementById('formUsedCount').value || 0)
    };

    if (!payload.question_text || !payload.topic) {
      App.showToast('Question text and topic are required.', 'warning');
      return;
    }

    try {
      const isEdit = Boolean(qid);
      const url = isEdit ? `/api/questions/${qid}` : '/api/questions';
      const method = isEdit ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        App.closeModal('questionModal');
        App.showToast(isEdit ? 'Question updated successfully!' : 'Question added to bank!', 'success');
        this.loadQuestions(this.currentPage);
        this.loadMetadata();
      } else {
        App.showToast(data.error || 'Failed to save question', 'error');
      }
    } catch (err) {
      App.showToast('Error communicating with server', 'error');
    }
  },

  confirmDelete(qid) {
    this.activeQuestionId = qid;
    document.getElementById('deleteTargetIdDisplay').textContent = `#${qid}`;
    App.openModal('deleteConfirmModal');
  },

  async executeDelete(qid) {
    try {
      const res = await fetch(`/api/questions/${qid}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        App.closeModal('deleteConfirmModal');
        App.showToast(`Question #${qid} deleted.`, 'success');
        this.loadQuestions(this.currentPage);
      } else {
        App.showToast(data.error || 'Failed to delete question', 'error');
      }
    } catch (err) {
      App.showToast('Error deleting question', 'error');
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

window.QuestionBank = QuestionBank;
