(function () {
  'use strict';

  // Client-side live search on tables
  const searchInputs = document.querySelectorAll('[data-table-search]');

  searchInputs.forEach((input) => {
    const tableId = input.dataset.tableSearch;
    const table = document.getElementById(tableId);
    if (!table) return;
    const rows = table.querySelectorAll('tbody tr');

    input.addEventListener('input', () => {
      const query = input.value.toLowerCase().trim();
      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      });

      const empty = table.querySelector('.no-results');
      const anyVisible = [...rows].some((r) => r.style.display !== 'none');
      if (empty) empty.style.display = anyVisible ? 'none' : '';
    });
  });

  // Select-all checkbox
  const selectAll = document.getElementById('select-all');
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      document.querySelectorAll('.row-select').forEach((cb) => {
        cb.checked = selectAll.checked;
      });
    });
  }

  // Session timeout warning (30 min = 1800s; warn at 1740s = 29 min)
  const SESSION_TIMEOUT = 1800 * 1000;
  const WARN_BEFORE = 60 * 1000;

  let lastActivity = Date.now();

  ['click', 'keypress', 'mousemove', 'scroll'].forEach((event) => {
    document.addEventListener(event, () => { lastActivity = Date.now(); }, { passive: true });
  });

  setInterval(() => {
    const idle = Date.now() - lastActivity;
    const warnEl = document.getElementById('session-warning');
    if (idle >= SESSION_TIMEOUT - WARN_BEFORE && warnEl) {
      warnEl.classList.add('open');
    }
    if (idle >= SESSION_TIMEOUT) {
      window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
    }
  }, 10000);
})();
