// ============================================================
// quiz.js — Fixed & Complete Quiz Engine
// Fixes: answer/question index mismatch, hint tracking per question,
//        survival mode, proper submission payload
// ============================================================

(function () {
    const container = document.getElementById('quizContainer');
    if (!container) return;
  
    // --- State ---
    const quizData = JSON.parse(document.getElementById('quiz-data').textContent);
    const mode = container.dataset.mode || 'timed';
    const totalQ = quizData.questions.length;
  
    // answers[i] = selected option index (0-3) or null if unanswered
    const answers = new Array(totalQ).fill(null);
    // hintsUsed[i] = true if hint was used on question i
    const hintsUsedPerQ = new Array(totalQ).fill(false);
  
    let currentIndex = 0;
    let startTime = Date.now();
    let timerInterval = null;
    let timeRemaining = quizData.time_limit || 600;
    let lives = 3;
    let totalHintsUsed = 0;
    const MAX_HINTS = 3;
  
    // --- DOM helpers ---
    const $  = id => document.getElementById(id);
    const qCards = () => document.querySelectorAll('.question-card');
  
    // ----------------------------------------------------------------
    // INIT
    // ----------------------------------------------------------------
    function init() {
      renderQuestion(0);
      updateNav();
      updateProgress();
  
      if (mode === 'timed') startTimer();
      if (mode === 'survival') renderLives();
    }
  
    // ----------------------------------------------------------------
    // RENDER current question card (show/hide)
    // ----------------------------------------------------------------
    function renderQuestion(idx) {
      qCards().forEach((card, i) => {
        card.classList.toggle('active', i === idx);
        card.classList.toggle('hidden', i !== idx);
      });
  
      // Restore previously selected answer visual
      const card = qCards()[idx];
      const opts = card.querySelectorAll('.option-btn');
      opts.forEach(btn => btn.classList.remove('selected'));
      if (answers[idx] !== null) {
        const selected = card.querySelector(`.option-btn[data-index="${answers[idx]}"]`);
        if (selected) selected.classList.add('selected');
      }
  
      // Update hint button state for this question
      const hintBtn = $('hintBtn');
      if (hintBtn) {
        hintBtn.disabled = hintsUsedPerQ[idx] || totalHintsUsed >= MAX_HINTS;
        hintBtn.textContent = `💡 Hint (${MAX_HINTS - totalHintsUsed} left)`;
      }
    }
  
    // ----------------------------------------------------------------
    // OPTION SELECTION — key fix: store option index per question index
    // ----------------------------------------------------------------
    window.selectOption = function (btn) {
      const optionIndex = parseInt(btn.dataset.index, 10);
      const card = qCards()[currentIndex];
  
      // Deselect all options in this card
      card.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
  
      // Store answer keyed to CURRENT question index (not option index)
      answers[currentIndex] = optionIndex;
  
      // Survival mode: validate immediately
      if (mode === 'survival') {
        const q = quizData.questions[currentIndex];
        if (optionIndex !== q.correct) {
          loseLife();
        }
      }
    };
  
    // ----------------------------------------------------------------
    // HINT — eliminate 2 wrong options, one-time per question
    // ----------------------------------------------------------------
    window.useHint = function () {
      if (hintsUsedPerQ[currentIndex] || totalHintsUsed >= MAX_HINTS) return;
  
      const card = qCards()[currentIndex];
      const q = quizData.questions[currentIndex];
      const wrongBtns = [];
  
      card.querySelectorAll('.option-btn').forEach((btn, i) => {
        if (i !== q.correct && !btn.classList.contains('eliminated')) {
          wrongBtns.push(btn);
        }
      });
  
      // Eliminate 2 wrong options
      wrongBtns.slice(0, 2).forEach(btn => btn.classList.add('eliminated'));
  
      hintsUsedPerQ[currentIndex] = true;
      totalHintsUsed++;
  
      const hintBtn = $('hintBtn');
      if (hintBtn) {
        hintBtn.disabled = totalHintsUsed >= MAX_HINTS;
        hintBtn.textContent = `💡 Hint (${MAX_HINTS - totalHintsUsed} left)`;
      }
    };
  
    // ----------------------------------------------------------------
    // NAVIGATION
    // ----------------------------------------------------------------
    window.nextQuestion = function () {
      if (currentIndex < totalQ - 1) {
        currentIndex++;
        renderQuestion(currentIndex);
        updateProgress();
        updateNav();
      }
    };
  
    window.prevQuestion = function () {
      if (currentIndex > 0) {
        currentIndex--;
        renderQuestion(currentIndex);
        updateProgress();
        updateNav();
      }
    };
  
    function updateProgress() {
      const pct = ((currentIndex + 1) / totalQ) * 100;
      const fill = $('progressFill');
      const text = $('progressText');
      if (fill) fill.style.width = pct + '%';
      if (text) text.textContent = `${currentIndex + 1} / ${totalQ}`;
    }
  
    function updateNav() {
      const prevBtn = $('prevBtn');
      const nextBtn = $('nextBtn');
      const submitBtn = $('submitBtn');
  
      if (prevBtn) prevBtn.disabled = currentIndex === 0;
  
      const isLast = currentIndex === totalQ - 1;
      if (nextBtn) nextBtn.classList.toggle('hidden', isLast);
      if (submitBtn) submitBtn.classList.toggle('hidden', !isLast);
    }
  
    // ----------------------------------------------------------------
    // TIMER
    // ----------------------------------------------------------------
    function startTimer() {
      const timerText = $('timerText');
      const timerBar = $('timerBar');
      const total = quizData.time_limit;
  
      timerInterval = setInterval(() => {
        timeRemaining--;
        const mins = Math.floor(timeRemaining / 60);
        const secs = timeRemaining % 60;
        if (timerText) timerText.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
  
        // Update timer bar fill (CSS variable trick)
        if (timerBar) {
          const pct = (timeRemaining / total) * 100;
          timerBar.style.setProperty('--timer-pct', pct + '%');
          // Also set inline for browsers that need it
          const fill = timerBar.querySelector('.timer-fill');
          if (fill) {
            fill.style.width = pct + '%';
            fill.style.background = pct > 50
              ? 'var(--accent-green)'
              : pct > 25
                ? 'var(--accent-orange)'
                : 'var(--accent-red)';
          }
          timerBar.style.color = pct > 50 ? 'var(--accent-green)' : pct > 25 ? 'var(--accent-orange)' : 'var(--accent-red)';
        }
  
        if (timerText) {
          timerText.style.color = timeRemaining <= 30 ? 'var(--accent-red)' : '';
        }
  
        if (timeRemaining <= 0) {
          clearInterval(timerInterval);
          submitQuiz();
        }
      }, 1000);
    }
  
    // ----------------------------------------------------------------
    // SURVIVAL MODE
    // ----------------------------------------------------------------
    function renderLives() {
      const lc = $('livesContainer');
      if (!lc) return;
      const lifeEls = lc.querySelectorAll('.life');
      lifeEls.forEach((el, i) => el.classList.toggle('lost', i >= lives));
    }
  
    function loseLife() {
      lives--;
      renderLives();
      if (lives <= 0) {
        setTimeout(submitQuiz, 800);
      }
    }
  
    // ----------------------------------------------------------------
    // SUBMIT — fixed payload: answers array matches question indices exactly
    // ----------------------------------------------------------------
    window.submitQuiz = function () {
      if (timerInterval) clearInterval(timerInterval);
  
      const timeTaken = Math.floor((Date.now() - startTime) / 1000);
  
      // Build properly indexed answers array
      // Each element: { selected: optionIndex } or { selected: null } for unanswered
      const payload = answers.map(a => ({ selected: a }));
  
      const submitBtn = $('submitBtn');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
      }
  
      fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quiz_id: quizData.id,
          answers: payload,
          time_taken: timeTaken,
          mode: mode,
          hints_used: totalHintsUsed
        })
      })
        .then(r => r.json())
        .then(data => {
          if (data.error) {
            alert('Error: ' + data.error);
            return;
          }
          showResults(data.result, data.new_badges || []);
        })
        .catch(err => {
          console.error('Submit error:', err);
          alert('Failed to submit quiz. Please try again.');
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Quiz';
          }
        });
    };
  
    // ----------------------------------------------------------------
    // SHOW RESULTS
    // ----------------------------------------------------------------
    function showResults(result, newBadges) {
      const qc = $('quizContainer');
      const qr = $('quizResults');
      if (qc) qc.classList.add('hidden');
      if (qr) qr.classList.remove('hidden');
  
      // Grade
      const gradeEl = $('gradeDisplay');
      if (gradeEl) {
        gradeEl.textContent = result.grade;
        gradeEl.className = 'grade-display grade-' + result.grade.replace('+', 'plus');
      }
  
      // Stats
      const set = (id, val) => { const el = $(id); if (el) el.textContent = val; };
      set('resultScore', result.total_score);
      set('resultAccuracy', result.accuracy + '%');
      set('resultStreak', result.max_streak);
      set('resultTime', formatTime(result.time_taken));
  
      // Breakdown — show question text + correct/wrong + points
      const breakdown = $('resultsBreakdown');
      if (breakdown && result.answers_detail) {
        breakdown.innerHTML = result.answers_detail.map((a, i) => {
          const q = quizData.questions[i];
          return `
            <div class="answer-row ${a.is_correct ? 'correct' : 'wrong'}">
              <span class="q-num">${i + 1}</span>
              <span class="q-icon">${a.is_correct ? '✓' : '✗'}</span>
              <span class="q-status">${q ? q.text.substring(0, 50) + (q.text.length > 50 ? '…' : '') : ''}</span>
              <span class="q-points">${a.points} pts</span>
            </div>`;
        }).join('');
      }
  
      // New badges
      if (newBadges && newBadges.length > 0) {
        const badgeDiv = $('newBadges');
        if (badgeDiv) {
          badgeDiv.classList.remove('hidden');
          badgeDiv.innerHTML = '<h3>🏅 New Badges Unlocked!</h3>' +
            newBadges.map(b => `<span class="new-badge">${b}</span>`).join('');
        }
      }
  
      // Confetti for perfect score
      if (result.perfect) {
        triggerConfetti();
      }
  
      // Scroll to results
      if (qr) qr.scrollIntoView({ behavior: 'smooth' });
    }
  
    // ----------------------------------------------------------------
    // SHARE
    // ----------------------------------------------------------------
    window.shareResult = function () {
      const scoreEl = $('resultScore');
      const gradeEl = $('gradeDisplay');
      const score = scoreEl ? scoreEl.textContent : '?';
      const grade = gradeEl ? gradeEl.textContent : '?';
      const text = `🎯 I scored ${score} points (Grade ${grade}) on "${quizData.title}" — Quizzify! Can you beat me?`;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => showToast('Score copied to clipboard! 📋'));
      } else {
        prompt('Copy your score:', text);
      }
    };
  
    // ----------------------------------------------------------------
    // CONFETTI
    // ----------------------------------------------------------------
    function triggerConfetti() {
      const colors = ['#f43f5e', '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ec4899'];
      for (let i = 0; i < 80; i++) {
        const c = document.createElement('div');
        c.className = 'confetti';
        c.style.cssText = `
          left:${Math.random() * 100}vw;
          animation-delay:${Math.random() * 2}s;
          background:${colors[Math.floor(Math.random() * colors.length)]};
          width:${6 + Math.random() * 8}px;
          height:${6 + Math.random() * 8}px;
          border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
        `;
        document.body.appendChild(c);
        setTimeout(() => c.remove(), 3500);
      }
    }
  
    // ----------------------------------------------------------------
    // UTILS
    // ----------------------------------------------------------------
    function formatTime(secs) {
      if (secs < 60) return secs + 's';
      return Math.floor(secs / 60) + 'm ' + (secs % 60) + 's';
    }
  
    function showToast(msg) {
      const t = document.createElement('div');
      t.className = 'toast';
      t.textContent = msg;
      t.style.cssText = `
        position:fixed; bottom:2rem; left:50%; transform:translateX(-50%);
        background:var(--bg-card); border:1px solid var(--border);
        color:var(--text-primary); padding:.75rem 1.5rem;
        border-radius:var(--radius-sm); z-index:9999;
        box-shadow:var(--shadow); font-weight:600;
        animation: fadeIn .3s ease;
      `;
      document.body.appendChild(t);
      setTimeout(() => t.remove(), 3000);
    }
  
    // ----------------------------------------------------------------
    // KEYBOARD SHORTCUTS (A/B/C/D + Enter to go next)
    // ----------------------------------------------------------------
    document.addEventListener('keydown', function (e) {
      const key = e.key.toUpperCase();
      const map = { A: 0, B: 1, C: 2, D: 3 };
      if (map[key] !== undefined) {
        const card = qCards()[currentIndex];
        if (!card) return;
        const btn = card.querySelector(`.option-btn[data-index="${map[key]}"]`);
        if (btn && !btn.classList.contains('eliminated')) window.selectOption(btn);
      }
      if (e.key === 'ArrowRight' || e.key === 'Enter') {
        if (currentIndex < totalQ - 1) window.nextQuestion();
      }
      if (e.key === 'ArrowLeft') window.prevQuestion();
    });
  
    // ----------------------------------------------------------------
    // BOOTSTRAP
    // ----------------------------------------------------------------
    init();
  })();