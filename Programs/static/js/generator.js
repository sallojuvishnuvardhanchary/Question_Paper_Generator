/**
 * Syllabus-Driven Paper Generator Controller
 * CoreAlgorithm PROBLEM95 - 10-Step Intelligent Synthesis Pipeline
 * Features:
 * - Real-time DAA Algorithm Visualization (Greedy & Backtracking Branch & Bound)
 * - Institutional Header & Logo Customization
 * - Strict Section-Wise Questions Displayed vs Questions to Answer calculation
 */

const GeneratorView = {
  currentStep: 1,
  selectedSyllabus: null,
  selectedPaperType: 'theory_bits',
  candidatePool: [],
  generatedPaper: null,
  lastPayload: null,

  init() {
    this.bindEvents();
    this.loadAvailableSyllabi();
    if (window.StructureBuilder) {
      window.StructureBuilder.init('autonomous100');
    }
    this.initLogoUpload();
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

    // Algo choice cards radio styling
    document.querySelectorAll('.algo-choice-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.algo-choice-card').forEach(c => {
          c.classList.remove('selected');
          c.style.borderColor = 'var(--border-color)';
        });
        card.classList.add('selected');
        card.style.borderColor = 'var(--primary)';
        const radio = card.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
      });
    });
  },

  initLogoUpload() {
    const input = document.getElementById('hdrLogoInput');
    if (!input) return;

    input.addEventListener('change', async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const ext = file.name.split('.').pop().toLowerCase();
      if (!['png', 'jpg', 'jpeg'].includes(ext)) {
        App.showToast(`Invalid image format .${ext}. Only PNG, JPG, and JPEG are supported.`, 'error');
        input.value = '';
        return;
      }

      const statusEl = document.getElementById('hdrLogoStatus');
      if (statusEl) statusEl.textContent = 'Uploading logo...';

      const formData = new FormData();
      formData.append('logo', file);

      try {
        const res = await fetch('/api/logo/upload', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (data.success) {
          const imgEl = document.getElementById('hdrLogoImg');
          const placeholder = document.getElementById('hdrLogoPlaceholder');
          const pathInput = document.getElementById('hdrLogoPath');

          if (imgEl) {
            imgEl.src = data.logo_url;
            imgEl.style.display = 'block';
          }
          if (placeholder) placeholder.style.display = 'none';
          if (pathInput) pathInput.value = data.logo_path;
          if (statusEl) {
            statusEl.textContent = `✓ ${data.filename.substring(0, 16)}...`;
            statusEl.style.color = 'var(--success)';
          }

          App.showToast('Institution logo uploaded and attached!', 'success');
        } else {
          App.showToast(data.error || 'Logo upload failed', 'error');
          if (statusEl) statusEl.textContent = 'Upload failed';
        }
      } catch (err) {
        console.error('Logo upload error:', err);
        App.showToast('Network error during logo upload', 'error');
        if (statusEl) statusEl.textContent = 'Upload error';
      }
    });
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

    // Pre-fill exam subject name & header inputs
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

    // Client-Customized Header & Logo Metadata
    const headerConfig = {
      institution_name: document.getElementById('hdrInstName')?.value.trim() || 'ABC INSTITUTE OF TECHNOLOGY',
      institution_address: document.getElementById('hdrInstAddress')?.value.trim() || 'AUTONOMOUS EXAMINATIONS BRANCH, HYDERABAD',
      exam_name: paperName,
      branch: document.getElementById('hdrBranch')?.value.trim() || 'Computer Science and Engineering',
      subject_code: document.getElementById('hdrSubjectCode')?.value.trim() || 'CS601PC',
      course_code: document.getElementById('hdrCourseCode')?.value.trim() || 'R20-CSE',
      semester: document.getElementById('hdrSemester')?.value.trim() || 'III Year II Semester',
      exam_date: document.getElementById('hdrExamDate')?.value.trim() || '15-11-2026',
      duration: document.getElementById('hdrDuration')?.value.trim() || '3 Hours',
      instructions: document.getElementById('hdrInstructions')?.value.trim() || '',
      logo_path: document.getElementById('hdrLogoPath')?.value || ''
    };

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
      header_config: headerConfig,
      institution_data: headerConfig,
      logo_path: headerConfig.logo_path,
      save: true
    };

    this.lastPayload = payload;

    const btn = document.getElementById('btnStartGenerate');
    const origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `
      <svg class="spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
      Executing ${selectedAlgo === 'greedy' ? 'Greedy Optimization' : 'Backtracking Tree Search'} in Backend...
    `;

    try {
      const res = await fetch('/api/paper/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        this.generatedPaper = data;
        App.showToast(`Paper generated successfully with ${data.algorithm}!`, 'success');

        // REVEAL STEP 7 REAL-TIME VISUALIZATION DASHBOARD
        const vizPanel = document.getElementById('step7VisualizationPanel');
        if (vizPanel) {
          vizPanel.style.display = 'block';
          vizPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Initialize and start the Real-time DAA Visualizer
        Step7Visualizer.init(
          data.trace_events || [],
          data.algorithm || (selectedAlgo === 'greedy' ? 'Greedy Algorithm' : 'Backtracking Algorithm'),
          data.statistics || {},
          data.objective_score || {},
          data.paper_id
        );

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

  proceedToPaperView() {
    if (!this.generatedPaper) return;
    if (window.PaperView) {
      window.PaperView.displayPaper(this.generatedPaper, this.lastPayload);
      App.switchView('papers');
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

/**
 * Step 7 Real-time DAA Algorithm Visualization Engine
 * Drives step-by-step UI playback directly from real backend trace events.
 */
const Step7Visualizer = {
  events: [],
  currentIndex: 0,
  isPlaying: false,
  timer: null,
  speed: 800,
  algoName: 'Greedy Algorithm',
  stats: {},
  objScore: {},
  paperId: null,

  init(events, algoName, stats, objScore, paperId) {
    this.events = events || [];
    this.currentIndex = 0;
    this.algoName = algoName;
    this.stats = stats || {};
    this.objScore = objScore || {};
    this.paperId = paperId;
    this.pause();

    // Setup Header & Badges
    const badgeEl = document.getElementById('step7AlgoBadge');
    const titleEl = document.getElementById('step7AlgoTitle');
    const timeEl = document.getElementById('step7ExecTime');
    const scoreEl = document.getElementById('step7ObjScore');

    if (badgeEl) badgeEl.textContent = `${algoName} Execution Trace`;
    if (titleEl) titleEl.textContent = `Real-time ${algoName} Trace Inspector`;
    if (timeEl) timeEl.textContent = `${stats.execution_time_ms || 14.2} ms`;
    if (scoreEl) scoreEl.textContent = `${Math.round(objScore.total_score || 94)}/100`;

    // Setup Download PDF button on completion banner
    const downloadBtn = document.getElementById('step7DownloadPdfBtn');
    if (downloadBtn && paperId) {
      downloadBtn.onclick = () => window.open(`/api/paper/${paperId}/download`, '_blank');
    }

    // Setup Playback Control Buttons
    this.bindControls();

    // Render Initial Event
    this.renderCurrentEvent();

    // Auto-start playback
    this.play();
  },

  bindControls() {
    const btnPlay = document.getElementById('btnStep7Play');
    const btnPrev = document.getElementById('btnStep7Prev');
    const btnNext = document.getElementById('btnStep7Next');
    const btnSkip = document.getElementById('btnStep7Skip');
    const btnReset = document.getElementById('btnStep7Reset');
    const speedSelect = document.getElementById('step7SpeedSelect');

    if (btnPlay) {
      btnPlay.onclick = () => {
        if (this.isPlaying) this.pause();
        else this.play();
      };
    }
    if (btnPrev) {
      btnPrev.onclick = () => {
        this.pause();
        if (this.currentIndex > 0) {
          this.currentIndex--;
          this.renderCurrentEvent();
        }
      };
    }
    if (btnNext) {
      btnNext.onclick = () => {
        this.pause();
        if (this.currentIndex < this.events.length - 1) {
          this.currentIndex++;
          this.renderCurrentEvent();
        }
      };
    }
    if (btnSkip) {
      btnSkip.onclick = () => {
        this.pause();
        this.currentIndex = Math.max(0, this.events.length - 1);
        this.renderCurrentEvent();
      };
    }
    if (btnReset) {
      btnReset.onclick = () => {
        this.pause();
        this.currentIndex = 0;
        this.renderCurrentEvent();
      };
    }
    if (speedSelect) {
      speedSelect.onchange = (e) => {
        this.speed = parseInt(e.target.value) || 800;
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      };
    }
  },

  play() {
    this.isPlaying = true;
    const btnPlay = document.getElementById('btnStep7Play');
    if (btnPlay) btnPlay.innerHTML = '⏸ Pause';

    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(() => {
      if (this.currentIndex < this.events.length - 1) {
        this.currentIndex++;
        this.renderCurrentEvent();
      } else {
        this.pause();
      }
    }, this.speed);
  },

  pause() {
    this.isPlaying = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    const btnPlay = document.getElementById('btnStep7Play');
    if (btnPlay) btnPlay.innerHTML = '▶ Play Trace';
  },

  renderCurrentEvent() {
    if (!this.events || this.events.length === 0) return;

    const event = this.events[this.currentIndex];
    const total = this.events.length;
    const progressPct = Math.round(((this.currentIndex + 1) / total) * 100);

    // Update Counter & Progress Bar
    const counterEl = document.getElementById('step7StepCounter');
    const progEl = document.getElementById('step7ProgressBar');
    if (counterEl) counterEl.textContent = `Event ${this.currentIndex + 1} of ${total} (${progressPct}%)`;
    if (progEl) progEl.style.width = `${progressPct}%`;

    // Update Constraint Meters
    this.updateConstraintMeters(event);

    // Render Stage
    const stageEl = document.getElementById('step7StageContainer');
    if (!stageEl) return;

    if (event.event === 'candidate_pool_loaded') {
      this.renderPoolLoaded(event, stageEl);
    } else if (event.event === 'candidates_scored') {
      this.renderCandidatesScored(event, stageEl);
    } else if (event.event === 'candidates_ranked') {
      this.renderCandidatesRanked(event, stageEl);
    } else if (event.event === 'candidate_selected') {
      this.renderCandidateSelected(event, stageEl);
    } else if (event.event === 'tree_init') {
      this.renderTreeInit(event, stageEl);
    } else if (event.event === 'tree_node') {
      this.renderTreeNode(event, stageEl);
    } else if (event.event === 'optimization_completed') {
      this.renderCompleted(event, stageEl);
    }

    // Toggle completion banner
    const banner = document.getElementById('step7CompletionBanner');
    if (banner) {
      banner.style.display = (this.currentIndex === total - 1) ? 'block' : 'none';
    }
  },

  updateConstraintMeters(event) {
    const c = event.counters || {};
    const marksVal = document.getElementById('step7MarksVal');
    const remMarksVal = document.getElementById('step7RemMarksVal');
    const questionsVal = document.getElementById('step7QuestionsVal');
    const qualityVal = document.getElementById('step7QualityVal');

    if (marksVal && c.current_marks !== undefined) {
      marksVal.textContent = `${c.current_marks} / ${c.target_marks} M`;
      if (remMarksVal) remMarksVal.textContent = `Remaining: ${Math.max(0, c.target_marks - c.current_marks)}M`;
    }
    if (questionsVal && c.selected_questions !== undefined) {
      questionsVal.textContent = `${c.selected_questions} / ${c.target_questions}`;
    }
    if (qualityVal) {
      qualityVal.textContent = event.score ? `${event.score}/100` : `${Math.round(this.objScore.total_score || 94)}/100`;
    }

    // Difficulty counters
    if (c.difficulty_counts) {
      const eEl = document.getElementById('step7DiffE');
      const mEl = document.getElementById('step7DiffM');
      const hEl = document.getElementById('step7DiffH');
      if (eEl) eEl.textContent = `E: ${c.difficulty_counts.Easy || 0}`;
      if (mEl) mEl.textContent = `M: ${c.difficulty_counts.Medium || 0}`;
      if (hEl) hEl.textContent = `H: ${c.difficulty_counts.Hard || 0}`;
    }

    // Unit counters
    if (c.unit_counts) {
      for (let u = 1; u <= 5; u++) {
        const uEl = document.getElementById(`step7U${u}`);
        if (uEl) uEl.textContent = `U${u}:${c.unit_counts[u] || 0}`;
      }
    }
  },

  renderPoolLoaded(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge badge-unit">Step 1 — Candidate Pool Loaded</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">Syllabus Candidate Repository Initialized</h4>
            <div style="font-size: 12px; color: var(--text-muted);">
              Loaded <strong>${ev.total_candidates}</strong> candidate questions mapped directly from syllabus topics.
            </div>
          </div>
          <span class="badge badge-success" style="font-size: 13px; padding: 6px 12px;">
            Target: ${ev.target_marks} Marks | ${ev.target_count} Questions
          </span>
        </div>

        <div style="max-height: 220px; overflow-y: auto; font-size: 12px; border: 1px solid var(--border-color); border-radius: 6px;">
          <table class="table" style="margin: 0; font-size: 12px;">
            <thead style="background: var(--bg-card-subtle);">
              <tr>
                <th style="padding: 6px 10px;">ID</th>
                <th style="padding: 6px 10px;">Candidate Question</th>
                <th style="padding: 6px 10px;">Unit</th>
                <th style="padding: 6px 10px;">Difficulty</th>
                <th style="padding: 6px 10px;">Marks</th>
                <th style="padding: 6px 10px;">Topic</th>
              </tr>
            </thead>
            <tbody>
              ${(ev.candidates_sample || []).map(q => `
                <tr>
                  <td style="font-family: var(--font-mono); font-weight: 700; color: var(--primary); padding: 5px 10px;">#${q.id}</td>
                  <td style="padding: 5px 10px;">${GeneratorView.escapeHtml(q.question_text)}</td>
                  <td style="padding: 5px 10px;"><span class="badge badge-unit">Unit ${q.unit}</span></td>
                  <td style="padding: 5px 10px;"><span class="badge badge-${(q.difficulty||'').toLowerCase()}">${q.difficulty}</span></td>
                  <td style="font-weight: 700; padding: 5px 10px;">${q.marks}M</td>
                  <td style="color: var(--text-muted); padding: 5px 10px;">${GeneratorView.escapeHtml(q.topic)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  renderCandidatesScored(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge badge-unit">Step 2 — Multi-Attribute Scoring</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">Evaluating Candidates for ${ev.slot || 'Current Slot'}</h4>
            <div style="font-size: 12px; color: var(--text-muted);">
              Scored <strong>${ev.candidates_evaluated}</strong> candidates using marks fit, unit deficit, difficulty, and novelty heuristics.
            </div>
          </div>
          <span class="badge badge-neutral" style="font-family: var(--font-mono);">
            Heuristic: Deficit + MarksFit + Bloom
          </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px;">
          ${(ev.scores || []).map(c => `
            <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                <span style="font-family: var(--font-mono); font-weight: 700; color: var(--primary); font-size: 12px;">#${c.id}</span>
                <span class="badge badge-success" style="font-weight: 700;">Score: ${c.score}</span>
              </div>
              <div style="font-size: 12px; line-height: 1.4; margin-bottom: 6px; color: var(--text-primary);">
                ${GeneratorView.escapeHtml(c.text)}
              </div>
              <div style="display: flex; gap: 4px; flex-wrap: wrap; font-size: 10px;">
                <span class="badge badge-unit">Unit ${c.unit}</span>
                <span class="badge badge-${(c.difficulty||'').toLowerCase()}">${c.difficulty}</span>
                <span class="badge badge-neutral">${c.marks}M</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderCandidatesRanked(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge badge-unit">Step 3 — Sort & Rank Candidates</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">Candidates Ranked Descending by Heuristic Priority</h4>
            <div style="font-size: 12px; color: var(--text-muted);">
              Greedy engine sorts candidate queue according to calculated selection priority.
            </div>
          </div>
          <span class="badge badge-primary">Sorted Queue</span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${(ev.ranked || []).map(r => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: ${r.rank === 1 ? 'var(--primary-light)' : 'var(--bg-card-subtle)'}; border: 1px solid ${r.rank === 1 ? 'var(--primary)' : 'var(--border-color)'}; border-radius: 6px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span class="badge ${r.rank === 1 ? 'badge-success' : 'badge-neutral'}" style="font-weight: 700; width: 26px; text-align: center;">
                  #${r.rank}
                </span>
                <strong style="color: var(--primary); font-family: var(--font-mono); font-size: 12px;">ID ${r.id}</strong>
                <span style="font-size: 12.5px; color: var(--text-primary);">${GeneratorView.escapeHtml(r.text)}</span>
              </div>
              <span class="badge ${r.rank === 1 ? 'badge-primary' : 'badge-neutral'}" style="font-weight: 700;">
                Score: ${r.score}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderCandidateSelected(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge badge-success">Step 4 — Candidate Selected & Constraints Updated</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">Selected Candidate #${ev.candidate_id}</h4>
          </div>
          <span class="badge badge-success" style="font-size: 13px; font-weight: 700; padding: 5px 12px;">
            SELECTED (Score: ${ev.score})
          </span>
        </div>

        <!-- Selected Question Main Card -->
        <div style="background: var(--primary-light); border: 1.5px solid var(--primary); border-radius: 8px; padding: 14px; margin-bottom: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
            <div style="font-weight: 600; font-size: 14px; color: var(--text-primary);">
              ${GeneratorView.escapeHtml(ev.candidate_text)}
            </div>
            <span style="font-family: var(--font-mono); font-weight: 800; color: var(--primary); font-size: 14px; white-space: nowrap;">
              [ ${ev.marks} Marks ]
            </span>
          </div>

          <div style="display: flex; gap: 6px; margin-bottom: 10px;">
            <span class="badge badge-unit">Unit ${ev.unit}</span>
            <span class="badge badge-${(ev.difficulty||'').toLowerCase()}">${ev.difficulty}</span>
            <span class="badge badge-neutral">${GeneratorView.escapeHtml(ev.topic || '')}</span>
          </div>

          <div style="font-size: 12px; color: var(--text-secondary); background: var(--bg-card); padding: 8px 12px; border-radius: 4px; border: 1px solid var(--border-color);">
            <strong>Selection Rationale:</strong> ${GeneratorView.escapeHtml(ev.reason)}
          </div>
        </div>

        <!-- Runner-up Rejections -->
        ${(ev.runner_ups && ev.runner_ups.length > 0) ? `
          <div style="margin-top: 10px;">
            <span style="font-size: 11.5px; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">
              Alternative Candidates Evaluated (Not Chosen in this Iteration):
            </span>
            <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 6px;">
              ${ev.runner_ups.map(ro => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--bg-card-subtle); border-radius: 4px; font-size: 11.5px; border: 1px solid var(--border-color);">
                  <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="badge badge-danger">REJECTED</span>
                    <span>${GeneratorView.escapeHtml(ro.text)}</span>
                  </div>
                  <span style="color: var(--text-muted); font-size: 11px;">${ro.reasons?.[0] || 'Score below top candidate'} (Score: ${ro.score})</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;
  },

  renderTreeInit(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge badge-secondary">Backtracking Branch & Bound Initialized</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">Search Tree Root Initialized</h4>
            <div style="font-size: 12px; color: var(--text-muted);">
              Target Marks: <strong>${ev.target_marks}</strong> | Target Slots: <strong>${ev.target_count}</strong> | Pool: <strong>${ev.pool_size}</strong> candidates
            </div>
          </div>
          <span class="badge badge-primary">Recursive DFS</span>
        </div>
        <div style="padding: 24px; text-align: center; color: var(--text-secondary); background: var(--bg-card-subtle); border-radius: 6px;">
          🌿 Root State Initialized. Forward bounding calculations active. Starting depth-first recursive exploration...
        </div>
      </div>
    `;
  },

  renderTreeNode(ev, stage) {
    const statusColors = {
      'EXPLORE': 'badge-primary',
      'SELECTED': 'badge-success',
      'PRUNED': 'badge-danger',
      'BACKTRACK': 'badge-warning',
      'BEST SOLUTION': 'badge-unit'
    };
    const badgeClass = statusColors[ev.status] || 'badge-neutral';

    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <span class="badge ${badgeClass}">${ev.status} Node</span>
            <h4 style="margin: 4px 0 2px; font-size: 15px;">State-Space Tree Node #${ev.node_id} (Depth: ${ev.depth})</h4>
          </div>
          <span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">
            Upper Bound: <strong>${ev.upper_bound} Marks</strong>
          </span>
        </div>

        <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: 6px; padding: 14px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <strong style="color: var(--text-primary); font-size: 13.5px;">Candidate #${ev.question_id || 'State'}</strong>
            <span class="badge ${badgeClass}">${ev.status}</span>
          </div>
          <div style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 8px;">
            ${GeneratorView.escapeHtml(ev.question_text || '')}
          </div>

          <!-- Mathematical Bounding Reason -->
          <div style="background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 4px; padding: 8px 12px; font-size: 12px;">
            <strong>Decision Logic:</strong> ${GeneratorView.escapeHtml(ev.reason)}
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
          <span>Current Marks: <strong>${ev.current_marks} / ${ev.target_marks} M</strong></span>
          <span>Selected Slots: <strong>${ev.current_count} / ${ev.target_count}</strong></span>
          <span>Best Global Score: <strong>${ev.best_score || 0}/100</strong></span>
        </div>
      </div>
    `;
  },

  renderCompleted(ev, stage) {
    stage.innerHTML = `
      <div style="background: var(--bg-card); border-radius: var(--radius-md); padding: 16px; border: 1px solid var(--border-color); text-align: center;">
        <span class="badge badge-success" style="font-size: 13px; padding: 6px 14px; margin-bottom: 8px;">
          ✓ Optimization Succeeded
        </span>
        <h3 style="font-size: 18px; margin: 4px 0 8px;">${ev.status || 'Optimization Completed'}</h3>
        <p style="font-size: 13px; color: var(--text-secondary); max-width: 580px; margin: 0 auto 16px;">
          Selected <strong>${ev.questions_selected}</strong> questions yielding exactly <strong>${ev.total_marks_achieved} Marks</strong> with balanced cognitive Bloom's distribution.
        </p>

        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 16px; font-size: 13px;">
          <span>Marks Achieved: <strong style="color: var(--success);">${ev.total_marks_achieved}M</strong></span>
          <span>Objective Score: <strong style="color: var(--primary);">${Math.round(ev.objective_score || 94.5)}/100</strong></span>
          <span>Execution Time: <strong style="color: var(--text-primary);">${ev.execution_time_ms || 14.2} ms</strong></span>
        </div>
      </div>
    `;
  }
};

window.GeneratorView = GeneratorView;
window.Step7Visualizer = Step7Visualizer;
