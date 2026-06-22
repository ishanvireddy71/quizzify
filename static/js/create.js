// create.js — Manual Quiz Creator

(function () {
    const categoriesEl = document.getElementById('categories-data');
    if (!categoriesEl) return;
    const categoriesData = JSON.parse(categoriesEl.textContent);
  
    let questionCount = 1;
  
    // ---- Subcategory update ----
    window.updateSubcategories = function () {
      const catId = document.getElementById('quizCategory').value;
      const subSelect = document.getElementById('quizSubcategory');
      subSelect.innerHTML = '<option value="">Select Subcategory</option>';
      const cat = categoriesData.find(c => c.id === catId);
      if (cat) {
        cat.subcategories.forEach(sub => {
          const opt = document.createElement('option');
          opt.value = sub.id;
          opt.textContent = sub.icon + ' ' + sub.name;
          subSelect.appendChild(opt);
        });
      }
    };
  
    // ---- Add question ----
    window.addQuestion = function () {
      questionCount++;
      const container = document.getElementById('questionsContainer');
      const div = document.createElement('div');
      div.className = 'question-builder animate-fadeIn';
      div.id = `qb_${questionCount}`;
      div.innerHTML = `
        <div class="qb-header">
          <h3>Question ${questionCount}</h3>
          <button type="button" class="btn-remove" onclick="removeQuestion(${questionCount})">✕</button>
        </div>
        <div class="form-group">
          <input type="text" name="q_text_${questionCount}" placeholder="Enter question..." required>
        </div>
        <div class="options-grid" id="opts_${questionCount}">
          ${['A','B','C','D'].map((ltr, i) => `
            <div class="option-input">
              <span class="opt-label">${ltr}</span>
              <input type="text" name="q${questionCount}_opt${i}" placeholder="Option ${ltr}" required>
              <input type="radio" name="q${questionCount}_correct" value="${i}" id="q${questionCount}_r${i}">
              <label for="q${questionCount}_r${i}">Correct</label>
            </div>
          `).join('')}
        </div>
        <div class="form-group" style="margin-top:.75rem">
          <label>Points</label>
          <input type="number" name="q_points_${questionCount}" value="10" min="5" max="50" style="width:100px">
        </div>
      `;
      container.appendChild(div);
    };
  
    window.removeQuestion = function (n) {
      const el = document.getElementById(`qb_${n}`);
      if (el) el.remove();
    };
  
    // ---- Collect form data ----
    function collectQuizData() {
      const title = document.getElementById('quizTitle').value.trim();
      const category = document.getElementById('quizCategory').value;
      const subcategory = document.getElementById('quizSubcategory').value;
      const difficulty = document.getElementById('quizDifficulty').value;
      const timeLimit = parseInt(document.getElementById('quizTimeLimit').value) || 600;
  
      const questions = [];
      document.querySelectorAll('.question-builder').forEach((qb, idx) => {
        const n = qb.id.replace('qb_', '');
        const textEl = qb.querySelector(`[name="q_text_${n}"]`);
        if (!textEl) return;
        const text = textEl.value.trim();
        const options = [];
        for (let i = 0; i < 4; i++) {
          const el = qb.querySelector(`[name="q${n}_opt${i}"]`);
          options.push(el ? el.value.trim() : '');
        }
        const correctEl = qb.querySelector(`[name="q${n}_correct"]:checked`);
        const correct = correctEl ? parseInt(correctEl.value) : 0;
        const pointsEl = qb.querySelector(`[name="q_points_${n}"]`);
        const points = pointsEl ? parseInt(pointsEl.value) : 10;
        questions.push({ id: `q${idx + 1}`, text, options, correct, points });
      });
  
      return { title, category, subcategory, difficulty, time_limit: timeLimit, questions };
    }
  
    // ---- Preview ----
    window.previewQuiz = function () {
      const data = collectQuizData();
      const previewSection = document.getElementById('previewSection');
      if (!previewSection) return;
      previewSection.classList.remove('hidden');
  
      document.getElementById('previewContent').innerHTML = `
        <p style="margin-bottom:1rem;color:var(--text-secondary)"><strong>${data.questions.length} questions</strong> · ${data.difficulty} · ${data.time_limit / 60} min</p>` +
        data.questions.map((q, i) => `
          <div class="preview-question">
            <p><strong>Q${i + 1}:</strong> ${q.text || '<em>empty</em>'}</p>
            <div class="preview-options">
              ${q.options.map((opt, j) => `
                <span class="preview-opt ${j === q.correct ? 'correct' : ''}">${'ABCD'[j]}. ${opt || '—'} ${j === q.correct ? '✓' : ''}</span>
              `).join('')}
            </div>
          </div>`).join('');
  
      previewSection.scrollIntoView({ behavior: 'smooth' });
    };
  
    // ---- Submit ----
    const form = document.getElementById('quizForm');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const data = collectQuizData();
  
        fetch('/api/quiz/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
          .then(r => r.json())
          .then(res => {
            if (res.success) {
              const resultEl = document.getElementById('createResult');
              if (resultEl) {
                resultEl.classList.remove('hidden');
                form.classList.add('hidden');
                const link = document.getElementById('createdQuizLink');
                if (link) link.href = '/quiz/' + res.quiz_id;
              }
            } else {
              alert('Errors:\n' + (res.errors || []).join('\n'));
            }
          })
          .catch(() => alert('Failed to create quiz. Please try again.'));
      });
    }
  })();