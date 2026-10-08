/**
 * Syllabus Management & Parsing Controller
 * CoreAlgorithm PROBLEM95 - Syllabus-Driven Automatic Paper Generation
 */

const SyllabusManager = {
  currentSyllabus: null,
  allSyllabi: [],

  init() {
    this.bindDropzone();
    this.loadSyllabiList();
  },

  bindDropzone() {
    const dropzone = document.getElementById('syllabusDropzone');
    const fileInput = document.getElementById('syllabusFileInput');

    if (!dropzone || !fileInput) return;

    // Dropzone click
    dropzone.addEventListener('click', (e) => {
      if (e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
        fileInput.click();
      }
    });

    // Drag & drop events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        this.handleFileUpload(files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files.length > 0) {
        this.handleFileUpload(fileInput.files[0]);
      }
    });
  },

  async handleFileUpload(file) {
    const validExtensions = ['pdf', 'docx', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(ext)) {
      App.showToast(`Unsupported format .${ext}. Allowed formats: PDF, DOCX, TXT`, 'error');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      App.showToast('File size exceeds 15MB limit.', 'error');
      return;
    }

    // Render Preview of file
    const dropzoneContent = document.getElementById('dropzoneContent');
    const dropzoneLoading = document.getElementById('dropzoneLoading');
    if (dropzoneContent) dropzoneContent.style.display = 'none';
    if (dropzoneLoading) dropzoneLoading.style.display = 'block';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/syllabus/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        App.showToast(`Syllabus parsed successfully: ${data.subject}`, 'success');
        this.currentSyllabus = {
          id: data.syllabus_id,
          filename: data.filename,
          subject: data.subject,
          parsed_text: data.parsed_text,
          structured_data: data.structured_data
        };
        this.renderSyllabusPreview(this.currentSyllabus);
        this.loadSyllabiList();

        // Also notify Generator wizard if active
        if (window.GeneratorView) {
          window.GeneratorView.onSyllabusLoaded(this.currentSyllabus);
        }
      } else {
        App.showToast(data.error || 'Failed to parse syllabus document.', 'error');
      }
    } catch (err) {
      console.error('Syllabus upload failed:', err);
      App.showToast('Network error during syllabus parsing.', 'error');
    } finally {
      if (dropzoneContent) dropzoneContent.style.display = 'block';
      if (dropzoneLoading) dropzoneLoading.style.display = 'none';
      const fileInput = document.getElementById('syllabusFileInput');
      if (fileInput) fileInput.value = '';
    }
  },

  async handleTextSubmit() {
    const textArea = document.getElementById('manualSyllabusText');
    const subjectInput = document.getElementById('manualSubjectName');

    const text = textArea?.value.trim();
    const subject = subjectInput?.value.trim() || 'Uploaded Course Syllabus';

    if (!text) {
      App.showToast('Please paste or type syllabus text.', 'warning');
      return;
    }

    try {
      const res = await fetch('/api/syllabus/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: text, subject: subject })
      });
      const data = await res.json();

      if (data.success) {
        App.showToast('Syllabus parsed and structured!', 'success');
        this.currentSyllabus = {
          id: data.syllabus_id,
          filename: data.filename,
          subject: data.subject,
          parsed_text: data.parsed_text,
          structured_data: data.structured_data
        };
        this.renderSyllabusPreview(this.currentSyllabus);
        this.loadSyllabiList();
        if (window.GeneratorView) {
          window.GeneratorView.onSyllabusLoaded(this.currentSyllabus);
        }
      } else {
        App.showToast(data.error || 'Failed to process syllabus text.', 'error');
      }
    } catch (err) {
      App.showToast('Failed to parse syllabus text.', 'error');
    }
  },

  renderSyllabusPreview(syllabus) {
    const previewContainer = document.getElementById('syllabusPreviewSection');
    if (!previewContainer) return;

    previewContainer.style.display = 'block';

    const struct = syllabus.structured_data || {};
    const units = struct.units || [];

    document.getElementById('previewSubjectTitle').value = struct.subject || syllabus.subject || 'Design and Analysis of Algorithms';
    document.getElementById('previewFileBadge').textContent = syllabus.filename || 'Uploaded Syllabus';

    const unitsContainer = document.getElementById('previewUnitsContainer');
    if (!unitsContainer) return;

    if (units.length === 0) {
      unitsContainer.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--text-muted); background: var(--bg-card-subtle); border-radius: var(--radius-md);">
          No distinct units could be automatically partitioned. Click "Add Unit" or edit the raw syllabus text.
        </div>
      `;
      return;
    }

    unitsContainer.innerHTML = units.map((u, uIdx) => {
      const topicsHtml = (u.topics || []).map((t, tIdx) => `
        <span class="topic-tag">
          <span>${this.escapeHtml(t)}</span>
          <span class="remove-topic-btn" onclick="SyllabusManager.removeTopic(${uIdx}, ${tIdx})" title="Remove Topic">✕</span>
        </span>
      `).join('');

      return `
        <div class="syllabus-unit-card" data-unit-index="${uIdx}">
          <div class="syllabus-unit-header">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span class="badge badge-unit">Unit ${u.unit || (uIdx + 1)}</span>
              <input type="text" class="form-control" value="${this.escapeHtml(u.title || '')}" 
                     placeholder="Unit Title (e.g. Divide & Conquer)" 
                     style="font-weight: 600; font-size: 14px; width: 340px;"
                     onchange="SyllabusManager.updateUnitTitle(${uIdx}, this.value)">
            </div>
            <span style="font-size: 12px; color: var(--text-muted);">${(u.topics || []).length} Topics</span>
          </div>

          <div class="topic-tag-container" id="unitTopicsContainer_${uIdx}">
            ${topicsHtml}
          </div>

          <div style="margin-top: 12px; display: flex; gap: 8px;">
            <input type="text" id="newTopicInput_${uIdx}" class="form-control form-control-sm" placeholder="Add topic (e.g. Master Theorem)..." style="max-width: 280px; font-size: 12px;">
            <button class="btn btn-outline btn-sm" onclick="SyllabusManager.addTopic(${uIdx})">+ Add Topic</button>
          </div>
        </div>
      `;
    }).join('');
  },

  updateUnitTitle(uIdx, newTitle) {
    if (this.currentSyllabus?.structured_data?.units?.[uIdx]) {
      this.currentSyllabus.structured_data.units[uIdx].title = newTitle.trim();
    }
  },

  addTopic(uIdx) {
    const input = document.getElementById(`newTopicInput_${uIdx}`);
    const val = input?.value.trim();
    if (!val) return;

    if (!this.currentSyllabus.structured_data.units[uIdx].topics) {
      this.currentSyllabus.structured_data.units[uIdx].topics = [];
    }

    this.currentSyllabus.structured_data.units[uIdx].topics.push(val);
    input.value = '';
    this.renderSyllabusPreview(this.currentSyllabus);
  },

  removeTopic(uIdx, tIdx) {
    if (this.currentSyllabus?.structured_data?.units?.[uIdx]?.topics) {
      this.currentSyllabus.structured_data.units[uIdx].topics.splice(tIdx, 1);
      this.renderSyllabusPreview(this.currentSyllabus);
    }
  },

  addUnit() {
    if (!this.currentSyllabus) return;
    if (!this.currentSyllabus.structured_data) {
      this.currentSyllabus.structured_data = { subject: 'Course', units: [] };
    }
    const nextUnitNum = (this.currentSyllabus.structured_data.units.length || 0) + 1;
    this.currentSyllabus.structured_data.units.push({
      unit: nextUnitNum,
      title: `Unit ${nextUnitNum} Topics`,
      topics: ['Overview & Concepts']
    });
    this.renderSyllabusPreview(this.currentSyllabus);
  },

  async saveSyllabusModifications() {
    if (!this.currentSyllabus || !this.currentSyllabus.id) {
      App.showToast('No active syllabus to save.', 'warning');
      return;
    }

    const subjectVal = document.getElementById('previewSubjectTitle')?.value.trim();
    if (subjectVal) {
      this.currentSyllabus.subject = subjectVal;
      this.currentSyllabus.structured_data.subject = subjectVal;
    }

    try {
      const res = await fetch(`/api/syllabus/${this.currentSyllabus.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: this.currentSyllabus.subject,
          structured_data: this.currentSyllabus.structured_data
        })
      });
      const data = await res.json();
      if (data.success) {
        App.showToast('Syllabus updates saved!', 'success');
        this.loadSyllabiList();
      } else {
        App.showToast(data.error || 'Failed to save changes.', 'error');
      }
    } catch (err) {
      App.showToast('Error saving syllabus updates.', 'error');
    }
  },

  async loadSyllabiList() {
    const listContainer = document.getElementById('syllabiHistoryList');
    if (!listContainer) return;

    try {
      const res = await fetch('/api/syllabus');
      const data = await res.json();

      if (data.success && data.syllabi) {
        this.allSyllabi = data.syllabi;
        this.renderSyllabiList(data.syllabi);
      }
    } catch (err) {
      console.error('Failed to load syllabi history:', err);
    }
  },

  renderSyllabiList(syllabi) {
    const listContainer = document.getElementById('syllabiHistoryList');
    if (!listContainer) return;

    if (syllabi.length === 0) {
      listContainer.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--text-muted);">
          No syllabi stored yet. Upload a syllabus PDF, DOCX, or TXT file to begin.
        </div>
      `;
      return;
    }

    listContainer.innerHTML = syllabi.map(s => {
      const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recent';
      const isCurrent = this.currentSyllabus && this.currentSyllabus.id === s.id;
      return `
        <div class="card" style="margin-bottom: 12px; ${isCurrent ? 'border-color: var(--primary);' : ''}">
          <div class="card-body" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 18px;">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="width: 38px; height: 38px; border-radius: var(--radius-sm); background: var(--primary-light); color: var(--primary); display: flex; align-items: center; justify-content: center; font-weight: 700;">
                ${(s.filename.split('.').pop() || 'TXT').toUpperCase()}
              </div>
              <div>
                <h4 style="font-size: 14.5px; font-weight: 600; margin: 0 0 2px;">${this.escapeHtml(s.subject)}</h4>
                <div style="font-size: 12px; color: var(--text-muted); display: flex; gap: 12px;">
                  <span>${this.escapeHtml(s.filename)}</span>
                  <span>•</span>
                  <span>${dateStr}</span>
                  <span>•</span>
                  <span>${s.papers_generated || 0} papers generated</span>
                </div>
              </div>
            </div>

            <div style="display: flex; gap: 8px;">
              <button class="btn btn-outline btn-sm" onclick="SyllabusManager.selectSyllabus(${s.id})">
                Inspect / Edit
              </button>
              <button class="btn btn-primary btn-sm" onclick="SyllabusManager.useForPaperGeneration(${s.id})">
                Use for Paper
              </button>
              <button class="btn btn-outline btn-sm" onclick="SyllabusManager.deleteSyllabus(${s.id})" style="color: var(--danger); border-color: rgba(239,68,68,0.25);">
                Delete
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  async selectSyllabus(id) {
    try {
      const res = await fetch(`/api/syllabus/${id}`);
      const data = await res.json();
      if (data.success && data.syllabus) {
        this.currentSyllabus = data.syllabus;
        this.renderSyllabusPreview(this.currentSyllabus);
        App.showToast(`Loaded syllabus: ${data.syllabus.subject}`, 'info');
      }
    } catch (err) {
      App.showToast('Failed to retrieve syllabus details.', 'error');
    }
  },

  async useForPaperGeneration(id) {
    await this.selectSyllabus(id);
    if (this.currentSyllabus) {
      App.switchView('generate');
      if (window.GeneratorView) {
        window.GeneratorView.onSyllabusLoaded(this.currentSyllabus);
      }
    }
  },

  async deleteSyllabus(id) {
    if (!confirm('Are you sure you want to delete this syllabus? Past generated papers will be preserved.')) return;

    try {
      const res = await fetch(`/api/syllabus/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        App.showToast('Syllabus deleted.', 'success');
        if (this.currentSyllabus && this.currentSyllabus.id === id) {
          this.currentSyllabus = null;
          const previewContainer = document.getElementById('syllabusPreviewSection');
          if (previewContainer) previewContainer.style.display = 'none';
        }
        this.loadSyllabiList();
      } else {
        App.showToast(data.error || 'Failed to delete syllabus.', 'error');
      }
    } catch (err) {
      App.showToast('Network error while deleting syllabus.', 'error');
    }
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

window.SyllabusManager = SyllabusManager;
