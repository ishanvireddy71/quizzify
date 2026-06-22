// main.js — global helpers

function toggleTheme() {
    fetch('/toggle-theme', { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        document.documentElement.setAttribute('data-theme', data.theme);
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = data.theme === 'dark' ? '☀️' : '🌙';
      });
  }
  
  function toggleMobileMenu() {
    document.getElementById('mobileMenu').classList.toggle('active');
  }
  
  document.addEventListener('click', function (e) {
    const menu = document.getElementById('mobileMenu');
    const btn = document.querySelector('.mobile-menu-btn');
    if (menu && btn && !menu.contains(e.target) && !btn.contains(e.target)) {
      menu.classList.remove('active');
    }
  });
  
  // Highlight active nav link
  (function () {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.getAttribute('href') === path) link.classList.add('active-nav');
    });
  })();