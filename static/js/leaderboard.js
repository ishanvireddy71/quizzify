// leaderboard.js
(function () {
    // Animate rank numbers on load
    document.querySelectorAll('.lb-score').forEach(el => {
      const target = parseInt(el.textContent.replace(/,/g, ''), 10);
      if (isNaN(target)) return;
      let current = 0;
      const step = Math.ceil(target / 40);
      const interval = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString();
        if (current >= target) clearInterval(interval);
      }, 30);
    });
  })();