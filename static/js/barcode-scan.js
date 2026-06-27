(function () {
  'use strict';

  const scanInput = document.querySelector('.scan-input');
  if (!scanInput) return;

  let buffer = '';
  let lastKeyTime = 0;

  // Focus scan input on page load
  scanInput.focus();

  document.addEventListener('keypress', (e) => {
    if (document.activeElement !== scanInput) {
      const tag = document.activeElement.tagName.toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;
    }

    const now = Date.now();
    if (now - lastKeyTime > 100) buffer = '';
    lastKeyTime = now;

    if (e.key === 'Enter' && buffer.length > 3) {
      scanInput.value = buffer.trim();
      buffer = '';
      scanInput.dispatchEvent(new Event('change', { bubbles: true }));

      // Auto-submit if a form is a parent or data-scan-form is set
      const formId = scanInput.dataset.scanForm;
      const form = formId ? document.getElementById(formId) : scanInput.closest('form');
      if (form) {
        // Trigger AJAX lookup if endpoint specified
        const endpoint = scanInput.dataset.lookupUrl;
        if (endpoint) {
          fetchAssetInfo(endpoint, scanInput.value);
        } else {
          form.submit();
        }
      }
    } else if (e.key !== 'Enter') {
      buffer += e.key;
    }
  });

  function fetchAssetInfo(endpoint, barcode) {
    const resultEl = document.getElementById('scan-result');
    if (resultEl) {
      resultEl.innerHTML = '<p class="text-secondary" style="padding:16px;">Looking up asset…</p>';
      resultEl.classList.add('visible');
    }

    fetch(`${endpoint}?barcode=${encodeURIComponent(barcode)}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then((r) => r.text())
      .then((html) => {
        if (resultEl) resultEl.innerHTML = html;
      })
      .catch(() => {
        if (resultEl) resultEl.innerHTML = '<p class="text-danger" style="padding:16px;">Error looking up asset.</p>';
      });
  }
})();
