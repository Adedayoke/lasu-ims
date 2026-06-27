(function () {
  'use strict';

  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay && overlay.classList.toggle('open');
    });

    overlay && overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    });
  }

  // Dropdown toggles
  document.querySelectorAll('[data-dropdown]').forEach((trigger) => {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const target = document.getElementById(trigger.dataset.dropdown);
      if (!target) return;
      const isOpen = target.classList.contains('open');
      document.querySelectorAll('.dropdown-menu.open').forEach((m) => m.classList.remove('open'));
      if (!isOpen) target.classList.add('open');
    });
  });

  document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown-menu.open').forEach((m) => m.classList.remove('open'));
  });

  // Modal open/close
  document.querySelectorAll('[data-modal-open]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.modalOpen;
      const modal = document.getElementById(id);
      if (modal) modal.classList.add('open');
    });
  });

  document.querySelectorAll('[data-modal-close], .modal-overlay').forEach((el) => {
    el.addEventListener('click', function (e) {
      if (e.target === this || el.dataset.modalClose !== undefined) {
        const overlay = el.closest('.modal-overlay') || document.getElementById(el.dataset.modalClose);
        if (overlay) overlay.classList.remove('open');
      }
    });
  });

  // Django messages auto-dismiss
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
})();
