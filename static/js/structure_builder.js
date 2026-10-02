/**
 * Dynamic Paper Structure Builder Controller
 * CoreAlgorithm PROBLEM95 - Syllabus-Driven Paper Generator
 * Supports client-defined Questions Displayed (N_disp), Questions to Answer (N_attempt),
 * Section Marks = N_attempt * Marks_per_Q, Total Paper Marks = sum(Section Marks),
 * Section Instructions, and Continuous Question Numbering.
 * 
 * Provides robust, non-destructive real-time editing of Marks / Question and counts
 * with instant section marks and blueprint recalculation.
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
              questions_to_answer: 10,
              marks_per_question: 2,
              question_type: 'Bits',
              internal_choice: false,
              section_instructions: 'Answer all 10 questions.'
            }
          ]
        },
        {
          part_name: 'PART B (Descriptive Theory & Problems)',
          sections: [
            {
              section_name: 'Unit-wise Analytical Questions (With Internal Choice)',
              question_count: 5,
              questions_to_answer: 5,
              marks_per_question: 16,
              question_type: 'Theory',
              internal_choice: true,
              section_instructions: 'Answer either (a) or (b) from each question.'
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
              questions_to_answer: 5,
              marks_per_question: 2,
              question_type: 'Short Answer',
              internal_choice: false,
              section_instructions: 'Answer all 5 questions.'
            }
          ]
        },
        {
          part_name: 'PART B',
          sections: [
            {
              section_name: 'Descriptive Questions',
              question_count: 5,
              questions_to_answer: 4,
              marks_per_question: 10,
              question_type: 'Theory',
              internal_choice: false,
              section_instructions: 'Answer any 4 questions out of 5.'
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
              question_count: 7,
              questions_to_answer: 5,
              marks_per_question: 14,
              question_type: 'Theory',
              internal_choice: false,
              section_instructions: 'Answer any 5 questions out of 7.'
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
              questions_to_answer: 50,
              marks_per_question: 1,
              question_type: 'MCQ',
              internal_choice: false,
              section_instructions: 'Answer all 50 multiple choice questions.'
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
          questions_to_answer: 3,
          marks_per_question: 5,
          question_type: 'Theory',
          internal_choice: false,
          section_instructions: 'Answer any 3 questions out of 5.'
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
      questions_to_answer: 3,
      marks_per_question: 5,
      question_type: 'Theory',
      internal_choice: false,
      section_instructions: 'Answer any 3 questions out of 5.'
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

  updateSectionName(pIdx, sIdx, val) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (sec) {
      sec.section_name = val.trim();
    }
  },

  updateSectionInstruction(pIdx, sIdx, val) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (sec) {
      sec.section_instructions = val;
    }
  },

  updateSectionType(pIdx, sIdx, val) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (sec) {
      sec.question_type = val;
    }
  },

  toggleInternalChoice(pIdx, sIdx, isChecked) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec) return;

    sec.internal_choice = Boolean(isChecked);
    if (sec.internal_choice) {
      sec.questions_to_answer = sec.question_count;
      sec.section_instructions = 'Answer either (a) or (b) from each question.';
    } else {
      this.autoUpdateInstruction(sec);
    }
    this.render();
  },

  /**
   * Real-time Marks / Question input handler.
   * Does NOT destroy or re-render the DOM, preserving active element focus,
   * cursor position, selection, backspace, and rapid typing.
   */
  onMarksInput(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    const rawVal = inputEl.value;
    // Allow empty string while user is deleting or typing new number
    if (rawVal.trim() === '') return;

    const parsed = parseInt(rawVal, 10);
    if (!isNaN(parsed) && parsed > 0) {
      sec.marks_per_question = parsed;
      this.updateSectionMarksDisplay(pIdx, sIdx);
      this.updateSummary();
    }
  },

  /**
   * Sanitizes Marks / Question upon focus loss (blur).
   */
  onMarksBlur(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    let val = parseInt(inputEl.value, 10);
    if (isNaN(val) || val < 1) {
      val = 1;
    } else if (val > 100) {
      val = 100;
    }

    sec.marks_per_question = val;
    inputEl.value = val;

    this.updateSectionMarksDisplay(pIdx, sIdx);
    this.updateSummary();
  },

  /**
   * Real-time Questions to Answer (N_attempt) input handler.
   */
  onToAnswerInput(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    const rawVal = inputEl.value;
    if (rawVal.trim() === '') return;

    const qDisp = parseInt(sec.question_count) || 1;
    const parsed = parseInt(rawVal, 10);
    if (!isNaN(parsed) && parsed > 0) {
      const qAtt = Math.min(qDisp, parsed);
      sec.questions_to_answer = qAtt;
      this.autoUpdateInstruction(sec, pIdx, sIdx);
      this.updateSectionMarksDisplay(pIdx, sIdx);
      this.updateSummary();
    }
  },

  onToAnswerBlur(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    const qDisp = parseInt(sec.question_count) || 1;
    let val = parseInt(inputEl.value, 10);
    if (isNaN(val) || val < 1) {
      val = 1;
    } else if (val > qDisp) {
      val = qDisp;
      if (window.App) {
        App.showToast(`Questions to answer cannot exceed ${qDisp} displayed questions.`, 'warning');
      }
    }

    sec.questions_to_answer = val;
    inputEl.value = val;
    this.autoUpdateInstruction(sec, pIdx, sIdx);
    this.updateSectionMarksDisplay(pIdx, sIdx);
    this.updateSummary();
  },

  /**
   * Real-time Questions Displayed (N_disp) input handler.
   */
  onDispCountInput(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    const rawVal = inputEl.value;
    if (rawVal.trim() === '') return;

    const parsed = parseInt(rawVal, 10);
    if (!isNaN(parsed) && parsed > 0) {
      sec.question_count = parsed;
      const toAnswerInput = document.getElementById(`secToAnswerInput_${pIdx}_${sIdx}`);
      if (toAnswerInput) {
        toAnswerInput.max = parsed;
        if (sec.questions_to_answer > parsed) {
          sec.questions_to_answer = parsed;
          toAnswerInput.value = parsed;
        }
      }
      this.updateQuestionNumberRanges();
      this.autoUpdateInstruction(sec, pIdx, sIdx);
      this.updateSectionMarksDisplay(pIdx, sIdx);
      this.updateSummary();
    }
  },

  onDispCountBlur(pIdx, sIdx, inputEl) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec || !inputEl) return;

    let val = parseInt(inputEl.value, 10);
    if (isNaN(val) || val < 1) val = 1;
    else if (val > 100) val = 100;

    sec.question_count = val;
    inputEl.value = val;

    const toAnswerInput = document.getElementById(`secToAnswerInput_${pIdx}_${sIdx}`);
    if (toAnswerInput) {
      toAnswerInput.max = val;
      if (sec.questions_to_answer > val) {
        sec.questions_to_answer = val;
        toAnswerInput.value = val;
      }
    }

    this.updateQuestionNumberRanges();
    this.autoUpdateInstruction(sec, pIdx, sIdx);
    this.updateSectionMarksDisplay(pIdx, sIdx);
    this.updateSummary();
  },

  /**
   * Updates the displayed Section Maximum Marks badge in-place.
   * Strictly calculated as: section_max_marks = questions_to_answer * marks_per_question.
   * NEVER calculated as: displayed * marks_per_question.
   */
  updateSectionMarksDisplay(pIdx, sIdx) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec) return;

    const qDisp = parseInt(sec.question_count) || 1;
    const qAtt = Math.min(qDisp, Math.max(1, parseInt(sec.questions_to_answer) || qDisp));
    const mPerQ = Math.max(1, parseInt(sec.marks_per_question) || 1);

    // Section Maximum Marks = N_attempt * Marks_per_Q
    const sectionMarks = qAtt * mPerQ;

    const badgeEl = document.getElementById(`secMarksBadge_${pIdx}_${sIdx}`);
    if (badgeEl) {
      badgeEl.innerHTML = `${sectionMarks} Marks (${qAtt} &times; ${mPerQ}M)`;
      badgeEl.setAttribute('title', `Section Max Marks = ${qAtt} to answer × ${mPerQ}M`);
    }
  },

  /**
   * Updates question number range badges across all sections (e.g. Q1-Q5, Q6-Q10).
   */
  updateQuestionNumberRanges() {
    let counter = 1;
    this.currentStructure.forEach((part, pIdx) => {
      (part.sections || []).forEach((sec, sIdx) => {
        const qDisp = parseInt(sec.question_count) || 1;
        const startQ = counter;
        const endQ = counter + qDisp - 1;
        counter += qDisp;

        const badge = document.getElementById(`secQRangeBadge_${pIdx}_${sIdx}`);
        if (badge) {
          badge.textContent = `Q${startQ}–Q${endQ}`;
        }
      });
    });
  },

  /**
   * Legacy wrapper for backward compatibility.
   */
  updateSection(pIdx, sIdx, field, val) {
    const sec = this.currentStructure[pIdx]?.sections?.[sIdx];
    if (!sec) return;

    if (field === 'question_count') {
      sec.question_count = Math.max(1, parseInt(val) || 1);
      if (!sec.questions_to_answer || sec.questions_to_answer > sec.question_count) {
        sec.questions_to_answer = sec.question_count;
      }
      this.autoUpdateInstruction(sec);
    } else if (field === 'questions_to_answer') {
      const qDisp = sec.question_count || 1;
      let qAtt = Math.max(1, parseInt(val) || 1);
      if (qAtt > qDisp) qAtt = qDisp;
      sec.questions_to_answer = qAtt;
      this.autoUpdateInstruction(sec);
    } else if (field === 'marks_per_question') {
      sec.marks_per_question = Math.max(1, parseInt(val) || 1);
    } else if (field === 'internal_choice') {
      this.toggleInternalChoice(pIdx, sIdx, val);
      return;
    } else if (field === 'section_instructions') {
      sec.section_instructions = val;
    } else {
      sec[field] = val;
    }

    this.render();
  },

  autoUpdateInstruction(sec, pIdx = null, sIdx = null) {
    const qDisp = parseInt(sec.question_count) || 1;
    const qAtt = parseInt(sec.questions_to_answer) || qDisp;
    let instText = '';
    if (sec.internal_choice) {
      instText = 'Answer either (a) or (b) from each question.';
    } else if (qAtt < qDisp) {
      instText = `Answer any ${qAtt} question${qAtt > 1 ? 's' : ''} out of ${qDisp}.`;
    } else {
      instText = `Answer all ${qDisp} questions.`;
    }
    sec.section_instructions = instText;

    if (pIdx !== null && sIdx !== null) {
      const instInput = document.getElementById(`secInstInput_${pIdx}_${sIdx}`);
      if (instInput) {
        instInput.value = instText;
      }
    }
  },

  calculateTotals() {
    let totalMarks = 0;
    let totalQuestions = 0;

    this.currentStructure.forEach(part => {
      (part.sections || []).forEach(sec => {
        const qDisp = parseInt(sec.question_count) || 0;
        const qAtt = Math.min(qDisp, Math.max(1, parseInt(sec.questions_to_answer) || qDisp));
        const marks = parseInt(sec.marks_per_question) || 0;
        // Section Marks = N_attempt * Marks_per_Q
        totalMarks += qAtt * marks;
        totalQuestions += qDisp;
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
    if (countEl) countEl.textContent = `${totalQuestions} Questions Displayed`;

    let duration = '3 Hours';
    if (totalMarks <= 30) duration = '1 Hour';
    else if (totalMarks <= 50) duration = '2 Hours';
    else if (totalMarks <= 75) duration = '2.5 Hours';
    if (durationEl) durationEl.textContent = duration;

    // Sync with hidden generator inputs
    const genTotalMarks = document.getElementById('genTotalMarks');
    const genQuestionCount = document.getElementById('genQuestionCount');
    if (genTotalMarks) genTotalMarks.value = totalMarks;
    if (genQuestionCount) genQuestionCount.value = totalQuestions;

    // Also update header config max marks
    const headerMaxMarks = document.getElementById('hdrMaxMarks');
    if (headerMaxMarks) headerMaxMarks.value = totalMarks;
  },

  render() {
    const container = document.getElementById('paperStructureContainer');
    if (!container) return;

    let questionSequenceCounter = 1;

    container.innerHTML = this.currentStructure.map((part, pIdx) => {
      const sectionsHtml = (part.sections || []).map((sec, sIdx) => {
        const qDisp = parseInt(sec.question_count) || 1;
        const qAtt = Math.min(qDisp, Math.max(1, parseInt(sec.questions_to_answer) || qDisp));
        const mPerQ = parseInt(sec.marks_per_question) || 1;
        const sectionMarks = qAtt * mPerQ;
        const startQ = questionSequenceCounter;
        const endQ = questionSequenceCounter + qDisp - 1;
        questionSequenceCounter += qDisp;

        return `
        <div class="section-builder-row">
          <div class="section-inputs-grid">
            <div>
              <label for="secTitleInput_${pIdx}_${sIdx}" style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Section Title</label>
              <input type="text" id="secTitleInput_${pIdx}_${sIdx}" class="form-control form-control-sm" 
                     value="${this.escapeHtml(sec.section_name || '')}" 
                     placeholder="e.g. Short Answer / Mandatory Bits"
                     oninput="StructureBuilder.updateSectionName(${pIdx}, ${sIdx}, this.value)">
            </div>

            <div>
              <label for="secDispInput_${pIdx}_${sIdx}" style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;" title="Total questions printed on paper">
                Displayed (N<sub>disp</sub>)
              </label>
              <input type="number" id="secDispInput_${pIdx}_${sIdx}" class="form-control form-control-sm" 
                     min="1" max="100" step="1" value="${qDisp}"
                     oninput="StructureBuilder.onDispCountInput(${pIdx}, ${sIdx}, this)"
                     onblur="StructureBuilder.onDispCountBlur(${pIdx}, ${sIdx}, this)">
            </div>

            <div>
              <label for="secToAnswerInput_${pIdx}_${sIdx}" style="font-size: 11px; font-weight: 600; color: var(--primary); display: block; margin-bottom: 3px;" title="Questions student must answer">
                To Answer (N<sub>attempt</sub>)
              </label>
              <input type="number" id="secToAnswerInput_${pIdx}_${sIdx}" class="form-control form-control-sm" 
                     min="1" max="${qDisp}" step="1" value="${qAtt}"
                     style="border-color: var(--primary); font-weight: 700;"
                     oninput="StructureBuilder.onToAnswerInput(${pIdx}, ${sIdx}, this)"
                     onblur="StructureBuilder.onToAnswerBlur(${pIdx}, ${sIdx}, this)">
            </div>

            <div>
              <label for="secMarksInput_${pIdx}_${sIdx}" style="font-size: 11px; font-weight: 600; color: var(--primary); display: block; margin-bottom: 3px;" title="Manually enter marks per question">
                Marks / Q
              </label>
              <input type="number" id="secMarksInput_${pIdx}_${sIdx}" class="form-control form-control-sm section-marks-input" 
                     min="1" max="100" step="1" value="${mPerQ}"
                     placeholder="e.g. 5"
                     oninput="StructureBuilder.onMarksInput(${pIdx}, ${sIdx}, this)"
                     onblur="StructureBuilder.onMarksBlur(${pIdx}, ${sIdx}, this)">
            </div>

            <div>
              <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Question Type</label>
              <select class="form-control form-control-sm form-select"
                      onchange="StructureBuilder.updateSectionType(${pIdx}, ${sIdx}, this.value)">
                <option value="Theory" ${sec.question_type === 'Theory' ? 'selected' : ''}>Theory</option>
                <option value="Bits" ${sec.question_type === 'Bits' ? 'selected' : ''}>Bits (Short)</option>
                <option value="Short Answer" ${sec.question_type === 'Short Answer' ? 'selected' : ''}>Short Answer</option>
                <option value="Long Answer" ${sec.question_type === 'Long Answer' ? 'selected' : ''}>Long Answer</option>
                <option value="MCQ" ${sec.question_type === 'MCQ' ? 'selected' : ''}>MCQ (4 Options)</option>
              </select>
            </div>

            <div>
              <button type="button" class="btn btn-outline btn-sm" onclick="StructureBuilder.removeSection(${pIdx}, ${sIdx})" title="Remove Section" style="color: var(--danger); border-color: rgba(239,68,68,0.3); padding: 5px 9px;">
                ✕
              </button>
            </div>
          </div>

          <!-- Section Calculation & Instruction Bar -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding-top: 10px; border-top: 1px dashed var(--border-color); font-size: 12px;">
            <div style="display: flex; gap: 8px; align-items: center; flex: 1; max-width: 65%;">
              <label for="secInstInput_${pIdx}_${sIdx}" style="font-size: 11px; color: var(--text-muted); white-space: nowrap;">Instructions:</label>
              <input type="text" id="secInstInput_${pIdx}_${sIdx}" class="form-control form-control-sm" style="font-size: 12px; padding: 3px 8px;"
                     value="${this.escapeHtml(sec.section_instructions || '')}"
                     placeholder="e.g. Answer any 3 questions out of 5."
                     oninput="StructureBuilder.updateSectionInstruction(${pIdx}, ${sIdx}, this.value)">
            </div>

            <div style="display: flex; align-items: center; gap: 10px;">
              <label class="form-check" style="font-size: 11.5px; margin: 0; white-space: nowrap; cursor: pointer;">
                <input type="checkbox" ${sec.internal_choice ? 'checked' : ''}
                       onchange="StructureBuilder.toggleInternalChoice(${pIdx}, ${sIdx}, this.checked)">
                <span>Internal (a)/(b) Choice</span>
              </label>

              <span id="secQRangeBadge_${pIdx}_${sIdx}" class="badge badge-unit" style="font-size: 11.5px; padding: 4px 8px;" title="Continuous Question Numbering">
                Q${startQ}–Q${endQ}
              </span>

              <span id="secMarksBadge_${pIdx}_${sIdx}" class="badge badge-success" style="font-size: 12px; font-weight: 700; padding: 4px 10px;" title="Section Max Marks = ${qAtt} to answer × ${mPerQ}M">
                ${sectionMarks} Marks (${qAtt} &times; ${mPerQ}M)
              </span>
            </div>
          </div>
        </div>
        `;
      }).join('');

      return `
        <div class="structure-part-card">
          <div class="structure-part-header">
            <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
              <span class="badge badge-unit" style="font-size: 13px; padding: 5px 10px;">Part ${pIdx + 1}</span>
              <input type="text" class="form-control" value="${this.escapeHtml(part.part_name)}" 
                     placeholder="Part Name" style="font-weight: 700; max-width: 420px;"
                     oninput="StructureBuilder.updatePartName(${pIdx}, this.value)">
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="button" class="btn btn-outline btn-sm" onclick="StructureBuilder.addSection(${pIdx})">
                + Add Section
              </button>
              <button type="button" class="btn btn-outline btn-sm" onclick="StructureBuilder.removePart(${pIdx})" style="color: var(--danger); border-color: rgba(239,68,68,0.3);">
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
