/**
 * Syllabus-Driven Paper Generator Controller
 * CoreAlgorithm PROBLEM95 - 10-Step Intelligent Synthesis Pipeline
 */

const GeneratorView = {
  currentStep: 1,
  selectedSyllabus: null,
  selectedPaperType: 'theory_bits',
  candidatePool: [],
  generatedPaper: null,

  init() {
    this.bindEvents();
    this.loadAvailableSyllabi();
    if (window.StructureBuilder) {
      window.StructureBuilder.init('autonomous100');
    }
    this.goToStep(1);
  },

  bindEvents() {
    // Stepper pills
    document.querySelectorAll('.wizard-step-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const targetStep = parseInt(pill.getAttribute('data-step'));
        if (this.canNavigateToStep(targetStep)) {
          this.goToStep(targetStep);
        }
      });
    });

    // Paper type selection cards
    document.querySelectorAll('.paper-type-card').forEach(card => {
      card.addEventListener('click', () => {
        const pType = card.getAttribute('data-type');
        this.setPaperType(pType, true);
      });
    });

    // Difficulty Sliders
    ['diffEasy', 'diffMedium', 'diffHard'].forEach(id => {
      const slider = document.getElementById(id);
      if (slider) {
        slider.addEventListener('input', () => this.updateDifficultySum());
      }
    });

    // Preset Buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = btn.getAttribute('data-preset');
        if (window.StructureBuilder) {
          window.StructureBuilder.applyPreset(preset);
          App.showToast(`Applied template: ${preset}`, 'info');
        }
      });
    });

    // Candidate Generation Button
    const btnGenCandidates = document.getElementById('btnGenerateCandidates');
    if (btnGenCandidates) {
      btnGenCandidates.addEventListener('click', () => this.generateCandidatesFromSyllabus());
    }

    // Main Paper Generation Button
    const btnGeneratePaper = document.getElementById('btnStartGenerate');
    if (btnGeneratePaper) {
      btnGeneratePaper.addEventListener('click', () => this.executePaperSynthesis());
    }
  },

  canNavigateToStep(step) {
    if (step > 1 && !this.selectedSyllabus) {
      App.showToast('Please select or upload a syllabus in Step 1 first.', 'warning');
      return false;
    }
    return true;
  },

  goToStep(stepNumber) {
    this.currentStep = stepNumber;

    // Update wizard pills
    document.querySelectorAll('.wizard-step-pill').forEach(pill => {
      const s = parseInt(pill.getAttribute('data-step'));
      pill.classList.toggle('active', s === stepNumber);
      pill.classList.toggle('completed', s < stepNumber);
    });

    // Toggle wizard step panels
    document.querySelectorAll('.wizard-step-pane').forEach(pane => {
      const pStep = parseInt(pane.getAttribute('data-step'));
      pane.style.display = (pStep === stepNumber) ? 'block' : 'none';
    });

    // Step-specific activations
    if (stepNumber === 2 && this.selectedSyllabus) {
      this.renderExtractedSyllabusView();
    }
    if (stepNumber === 4 && window.StructureBuilder) {
      window.StructureBuilder.updateSummary();
    }
  },

  async loadAvailableSyllabi() {
    const selectEl = document.getElementById('genSelectExistingSyllabus');
    if (!selectEl) return;

    try {
      const res = await fetch('/api/syllabus');
      const data = await res.json();
      if (data.success && data.syllabi) {
        selectEl.innerHTML = '<option value="">-- Choose an existing syllabus --</option>' + 
          data.syllabi.map(s => `<option value="${s.id}">${this.escapeHtml(s.subject)} (${s.filename})</option>`).join('');

        selectEl.addEventListener('change', async (e) => {
          const sid = e.target.value;
          if (sid) {
            await this.loadSyllabusById(sid);
          }
        });
      }
    } catch (err) {
      console.error('Failed to load syllabi dropdown:', err);
    }
  },

  async loadSyllabusById(sid) {
    try {
      const res = await fetch(`/api/syllabus/${sid}`);
      const data = await res.json();
      if (data.success && data.syllabus) {
        this.onSyllabusLoaded(data.syllabus);
        App.showToast(`Selected syllabus: ${data.syllabus.subject}`, 'success');
      }
    } catch (err) {
      App.showToast('Failed to load syllabus', 'error');
    }
  },

  onSyllabusLoaded(syllabus) {
    this.selectedSyllabus = syllabus;

    // Update badge / card
    const infoCard = document.getElementById('selectedSyllabusInfoCard');
    if (infoCard) {
      infoCard.style.display = 'flex';
      document.getElementById('selectedSyllabusName').textContent = syllabus.subject || 'Uploaded Course';
      document.getElementById('selectedSyllabusFile').textContent = syllabus.filename || 'Direct Input';
      const uCount = syllabus.structured_data?.units?.length || 0;
      document.getElementById('selectedSyllabusUnitsCount').textContent = `${uCount} Units Detected`;
    }

    // Pre-fill exam subject name
    const examNameInput = document.getElementById('genPaperName');
    if (examNameInput && (!examNameInput.value || examNameInput.value.includes('DAA'))) {
      examNameInput.value = `${syllabus.subject || 'Course'} Semester Examination`;
    }

    this.renderExtractedSyllabusView();
  },

  renderExtractedSyllabusView() {
    if (!this.selectedSyllabus) return;
    const container = document.getElementById('genExtractedSyllabusPreview');
    if (!container) return;

    const struct = this.selectedSyllabus.structured_data || {};
    const units = struct.units || [];

    if (units.length === 0) {
      container.innerHTML = `<div style="padding: 20px; color: var(--text-muted); text-align: center;">No structured units found. You can add units below.</div>`;
      return;
    }

    container.innerHTML = units.map((u, uIdx) => `
      <div class="syllabus-unit-card" style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div>
            <span class="badge badge-unit">Unit ${u.unit || (uIdx + 1)}</span>
            <strong style="margin-left: 8px; font-size: 14px;">${this.escapeHtml(u.title || '')}</strong>
          </div>
          <span style="font-size: 12px; color: var(--text-muted);">${(u.topics || []).length} Topics</span>
        </div>
        <div class="topic-tag-container">
          ${(u.topics || []).map(t => `<span class="topic-tag">${this.escapeHtml(t)}</span>`).join('')}
        </div>
      </div>
    `).join('');
  },

  setPaperType(paperType, updateStructurePreset = true) {
    this.selectedPaperType = paperType;

    // Highlight card
    document.querySelectorAll('.paper-type-card').forEach(card => {
      card.classList.toggle('selected', card.getAttribute('data-type') === paperType);
    });

    if (updateStructurePreset && window.StructureBuilder) {
      if (paperType === 'theory_bits') {
        window.StructureBuilder.applyPreset('autonomous100');
      } else if (paperType === 'theory') {
        window.StructureBuilder.applyPreset('theory70');
      } else if (paperType === 'mcq') {
        window.StructureBuilder.applyPreset('mcq50');
      }
    }
  },

  updateDifficultySum() {
    const e = parseInt(document.getElementById('diffEasy')?.value || 30);
    const m = parseInt(document.getElementById('diffMedium')?.value || 50);
    const h = parseInt(document.getElementById('diffHard')?.value || 20);

    const diffEasyVal = document.getElementById('diffEasyVal');
    const diffMediumVal = document.getElementById('diffMediumVal');
    const diffHardVal = document.getElementById('diffHardVal');

    if (diffEasyVal) diffEasyVal.textContent = `${e}%`;
    if (diffMediumVal) diffMediumVal.textContent = `${m}%`;
    if (diffHardVal) diffHardVal.textContent = `${h}%`;

    const sum = e + m + h;
    const sumEl = document.getElementById('diffSumIndicator');
    if (sumEl) {
      sumEl.textContent = `Total: ${sum}%`;
      sumEl.style.color = sum === 100 ? 'var(--success)' : 'var(--warning)';
    }
  },

  async generateCandidatesFromSyllabus() {
    if (!this.selectedSyllabus) {
      App.showToast('Please select a syllabus first.', 'warning');
      return;
    }

    const btn = document.getElementById('btnGenerateCandidates');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spin">⏳</span> Synthesizing Candidate Questions from Syllabus Topics...`;

    try {
      const payload = {
        syllabus_id: this.selectedSyllabus.id,
        syllabus_data: this.selectedSyllabus.structured_data,
        paper_type: this.selectedPaperType
      };

      const res = await fetch('/api/questions/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success && data.questions) {
        this.candidatePool = data.questions;
        App.showToast(`Synthesized ${data.questions.length} questions across syllabus units!`, 'success');
        this.renderCandidateQuestionsPreview(data.questions);
      } else {
        App.showToast(data.error || 'Failed to synthesize candidate questions.', 'error');
      }
    } catch (err) {
      console.error('Candidate generation failed:', err);
      App.showToast('Network error during question synthesis.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  },

  renderCandidateQuestionsPreview(questions) {
    const container = document.getElementById('candidateQuestionsPreviewContainer');
    const countBadge = document.getElementById('candidateQuestionsCountBadge');
    if (!container) return;

    if (countBadge) countBadge.textContent = `${questions.length} Questions in Pool`;

    container.innerHTML = questions.slice(0, 15).map(q => `
      <div class="candidate-q-card">
        <div style="flex: 1;">
          <div style="font-weight: 500; font-size: 13.5px; color: var(--text-primary); margin-bottom: 4px;">
            ${this.escapeHtml(q.question_text)}
          </div>
          <div style="display: flex; gap: 6px; align-items: center; font-size: 11.5px;">
            <span class="badge badge-unit">Unit ${q.unit}</span>
            <span class="badge badge-neutral">${this.escapeHtml(q.topic)}</span>
            <span class="badge badge-${(q.difficulty || 'Medium').toLowerCase()}">${q.difficulty}</span>
            <span class="badge badge-neutral">${q.question_type}</span>
          </div>
        </div>
        <div style="font-family: var(--font-mono); font-weight: 700; color: var(--primary); white-space: nowrap;">
          [ ${q.marks}M ]
        </div>
      </div>
    `).join('') + (questions.length > 15 ? `<div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 8px;">+ ${questions.length - 15} more candidate questions prepared for algorithmic optimization...</div>` : '');
  },

  async executePaperSynthesis() {
    if (!this.selectedSyllabus) {
      App.showToast('Please select or upload a syllabus first.', 'warning');
      this.goToStep(1);
      return;
    }

    const structure = window.StructureBuilder ? window.StructureBuilder.getStructureConfig() : [];
    const { totalMarks, totalQuestions } = window.StructureBuilder ? window.StructureBuilder.calculateTotals() : { totalMarks: 100, totalQuestions: 10 };

    const paperName = document.getElementById('genPaperName')?.value.trim() || `${this.selectedSyllabus.subject} Examination`;
    const selectedAlgo = document.querySelector('input[name="algoChoice"]:checked')?.value || 'greedy';
    const avoidUsed = document.getElementById('genAvoidUsed')?.checked ?? true;

    // Difficulty percentages
    const diffRatio = {
      'Easy': parseInt(document.getElementById('diffEasy')?.value || 30) / 100,
      'Medium': parseInt(document.getElementById('diffMedium')?.value || 50) / 100,
      'Hard': parseInt(document.getElementById('diffHard')?.value || 20) / 100
    };

    const payload = {
      syllabus_id: this.selectedSyllabus.id,
      syllabus_data: this.selectedSyllabus.structured_data,
      subject: this.selectedSyllabus.subject,
      paper_name: paperName,
      paper_type: this.selectedPaperType,
      structure: structure,
      total_marks: totalMarks,
      question_count: totalQuestions,
      algorithm: selectedAlgo,
      difficulty_ratio: diffRatio,
      avoid_used: avoidUsed,
      candidate_pool: this.candidatePool.length > 0 ? this.candidatePool : null,
      save: true
    };

    const btn = document.getElementById('btnStartGenerate');
    const origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `
      <svg class="spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
      Executing ${selectedAlgo === 'greedy' ? 'Greedy Optimization' : 'Backtracking Tree Search'}...
    `;

    try {
      const res = await fetch('/api/paper/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        App.showToast(`Paper generated successfully with ${data.algorithm}!`, 'success');
        this.generatedPaper = data;
        
        // Show in Paper View
        if (window.PaperView) {
          window.PaperView.displayPaper(data, payload);
          App.switchView('papers');
        }
      } else {
        App.showToast(data.error || 'Paper synthesis failed constraints.', 'error', 6000);
      }
    } catch (err) {
      console.error('Paper generation request error:', err);
      App.showToast('Network error during algorithmic paper synthesis.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = origText;
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

window.GeneratorView = GeneratorView;
