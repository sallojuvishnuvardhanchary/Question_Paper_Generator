/**
 * Dynamic Paper Structure Builder Controller
 * CoreAlgorithm PROBLEM95 - Syllabus-Driven Paper Generator
 */

const StructureBuilder = {
  currentStructure: [],

  // Pre-configured university templates
  presets: {
    autonomous100: {
      name: 'Autonomous Engineering (100 Marks)',
      paper_type: 'theory_bits',
      parts: [
        {
          part_name: 'PART A (Short Answer & Conceptual Bits)',
          sections: [
            {
              section_name: 'Compulsory Bits',
              question_count: 10,
              marks_per_question: 2,
              question_type: 'Bits',
              internal_choice: false
            }
          ]
        },
        {
          part_name: 'PART B (Descriptive Theory & Problems)',
          sections: [
            {
              section_name: 'Unit-wise Analytical Questions (With Internal Choice)',
              question_count: 5,
              marks_per_question: 16,
              question_type: 'Theory',
              internal_choice: true
            }
          ]
        }
      ]
    },
    midterm50: {
      name: 'Mid-Term Assessment (50 Marks)',
      paper_type: 'theory_bits',
      parts: [
        {
          part_name: 'PART A',
          sections: [
            {
              section_name: 'Short Answer Questions',
              question_count: 5,
              marks_per_question: 2,
              question_type: 'Short Answer',
              internal_choice: false
            }
          ]
        },
        {
          part_name: 'PART B',
          sections: [
            {
              section_name: 'Detailed Questions',
              question_count: 4,
              marks_per_question: 10,
              question_type: 'Theory',
              internal_choice: true
            }
          ]
        }
      ]
    },
    theory70: {
      name: 'Pure Theory Examination (70 Marks)',
      paper_type: 'theory',
      parts: [
        {
          part_name: 'SECTION I',
          sections: [
            {
              section_name: 'Analytical & Design Problems',
              question_count: 5,
              marks_per_question: 14,
              question_type: 'Theory',
              internal_choice: true
            }
          ]
        }
      ]
    },
    mcq50: {
      name: 'Objective Multiple Choice Examination (50 Marks)',
      paper_type: 'mcq',
      parts: [
        {
          part_name: 'MULTIPLE CHOICE QUESTIONS',
          sections: [
            {
              section_name: 'Core Curriculum MCQs',
              question_count: 50,
              marks_per_question: 1,
              question_type: 'MCQ',
              internal_choice: false
            }
          ]
        }
      ]
    }
  },

  init(defaultPreset = 'autonomous100') {
    this.applyPreset(defaultPreset);
  },

  applyPreset(presetKey) {
    const p = this.presets[presetKey];
    if (!p) return;

    this.currentStructure = JSON.parse(JSON.stringify(p.parts));
    if (window.GeneratorView) {
      window.GeneratorView.setPaperType(p.paper_type, false);
    }
    this.render();
  },

  addPart() {
    const nextChar = String.fromCharCode(65 + this.currentStructure.length);
    this.currentStructure.push({
      part_name: `PART ${nextChar}`,
      sections: [
        {
          section_name: 'Section 1',
          question_count: 5,
          marks_per_question: 10,
          question_type: 'Theory',
          internal_choice: false
        }
      ]
    });
    this.render();
  },

  removePart(pIdx) {
    if (this.currentStructure.length <= 1) {
      App.showToast('Examination must contain at least one Part.', 'warning');
      return;
    }
    this.currentStructure.splice(pIdx, 1);
    this.render();
  },

  addSection(pIdx) {
    const part = this.currentStructure[pIdx];
    if (!part) return;
    const nextNum = (part.sections?.length || 0) + 1;
    part.sections.push({
      section_name: `Section ${nextNum}`,
      question_count: 5,
      marks_per_question: 4,
      question_type: 'Theory',
      internal_choice: false
    });
    this.render();
  },

  removeSection(pIdx, sIdx) {
    const part = this.currentStructure[pIdx];
    if (!part || !part.sections) return;
    if (part.sections.length <= 1) {
      App.showToast('Each Part must contain at least one Section.', 'warning');
      return;
    }
    part.sections.splice(sIdx, 1);
    this.render();
  },

  updatePartName(pIdx, name) {
    if (this.currentStructure[pIdx]) {
      this.currentStructure[pIdx].part_name = name.trim();
    }
  },

  updateSection(pIdx, sIdx, field, val) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec) return;

    if (field === 'question_count' || field === 'marks_per_question') {
      sec[field] = Math.max(1, parseInt(val) || 1);
    } else if (field === 'internal_choice') {
      sec[field] = Boolean(val);
    } else {
      sec[field] = val;
    }
    this.updateSummary();
  },

  calculateTotals() {
    let totalMarks = 0;
    let totalQuestions = 0;

    this.currentStructure.forEach(part => {
      (part.sections || []).forEach(sec => {
        const count = parseInt(sec.question_count) || 0;
        const marks = parseInt(sec.marks_per_question) || 0;
        totalMarks += count * marks;
        totalQuestions += count;
      });
    });

    return { totalMarks, totalQuestions };
  },

  updateSummary() {
    const { totalMarks, totalQuestions } = this.calculateTotals();
    const marksEl = document.getElementById('structTotalMarksBadge');
    const countEl = document.getElementById('structTotalQuestionsBadge');
    const durationEl = document.getElementById('structDurationBadge');

    if (marksEl) marksEl.textContent = `${totalMarks} Marks`;
    if (countEl) countEl.textContent = `${totalQuestions} Questions`;

    let duration = '3 Hours';
    if (totalMarks <= 30) duration = '1 Hour';
    else if (totalMarks <= 60) duration = '2 Hours';
    if (durationEl) durationEl.textContent = duration;

    // Sync with hidden generator inputs
    const genTotalMarks = document.getElementById('genTotalMarks');
    const genQuestionCount = document.getElementById('genQuestionCount');
    if (genTotalMarks) genTotalMarks.value = totalMarks;
    if (genQuestionCount) genQuestionCount.value = totalQuestions;
  },

  render() {
    const container = document.getElementById('paperStructureContainer');
    if (!container) return;

    container.innerHTML = this.currentStructure.map((part, pIdx) => {
      const sectionsHtml = (part.sections || []).map((sec, sIdx) => `
        <div class="section-builder-row">
          <div>
            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 2px;">Section Title</label>
            <input type="text" class="form-control form-control-sm" value="${this.escapeHtml(sec.section_name || '')}" 
                   placeholder="e.g. Mandatory Bits"
                   onchange="StructureBuilder.updateSection(${pIdx}, ${sIdx}, 'section_name', this.value)">
          </div>

          <div>
            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 2px;">Questions</label>
            <input type="number" class="form-control form-control-sm" min="1" max="100" value="${sec.question_count}"
                   onchange="StructureBuilder.updateSection(${pIdx}, ${sIdx}, 'question_count', this.value)">
          </div>

          <div>
            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 2px;">Marks / Q</label>
            <input type="number" class="form-control form-control-sm" min="1" max="50" value="${sec.marks_per_question}"
                   onchange="StructureBuilder.updateSection(${pIdx}, ${sIdx}, 'marks_per_question', this.value)">
          </div>

          <div>
            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 2px;">Type</label>
            <select class="form-control form-control-sm form-select"
                    onchange="StructureBuilder.updateSection(${pIdx}, ${sIdx}, 'question_type', this.value)">
              <option value="Theory" ${sec.question_type === 'Theory' ? 'selected' : ''}>Theory</option>
              <option value="Bits" ${sec.question_type === 'Bits' ? 'selected' : ''}>Bits (Short)</option>
              <option value="Short Answer" ${sec.question_type === 'Short Answer' ? 'selected' : ''}>Short Answer</option>
              <option value="Long Answer" ${sec.question_type === 'Long Answer' ? 'selected' : ''}>Long Answer</option>
              <option value="MCQ" ${sec.question_type === 'MCQ' ? 'selected' : ''}>MCQ (4 Options)</option>
            </select>
          </div>

          <div>
            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 2px;">Choice Pattern</label>
            <label class="form-check" style="font-size: 12px; margin-top: 4px;">
              <input type="checkbox" ${sec.internal_choice ? 'checked' : ''}
                     onchange="StructureBuilder.updateSection(${pIdx}, ${sIdx}, 'internal_choice', this.checked)">
              <span>Internal OR Choice</span>
            </label>
          </div>

          <div style="display: flex; align-items: flex-end; padding-bottom: 2px;">
            <button class="btn btn-outline btn-sm" onclick="StructureBuilder.removeSection(${pIdx}, ${sIdx})" title="Remove Section" style="color: var(--danger); padding: 5px 8px;">
              ✕
            </button>
          </div>
        </div>
      `).join('');

      return `
        <div class="structure-part-card">
          <div class="structure-part-header">
            <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
              <span class="badge badge-unit">Part ${pIdx + 1}</span>
              <input type="text" class="form-control" value="${this.escapeHtml(part.part_name)}" 
                     placeholder="Part Name" style="font-weight: 700; max-width: 420px;"
                     onchange="StructureBuilder.updatePartName(${pIdx}, this.value)">
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-outline btn-sm" onclick="StructureBuilder.addSection(${pIdx})">
                + Add Section
              </button>
              <button class="btn btn-outline btn-sm" onclick="StructureBuilder.removePart(${pIdx})" style="color: var(--danger); border-color: rgba(239,68,68,0.3);">
                Delete Part
              </button>
            </div>
          </div>

          <div class="sections-list-container">
            ${sectionsHtml}
          </div>
        </div>
      `;
    }).join('');

    this.updateSummary();
  },

  getStructureConfig() {
    return this.currentStructure;
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
};

window.StructureBuilder = StructureBuilder;
