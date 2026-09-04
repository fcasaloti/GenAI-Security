/* GenAI App Security Lab — Shared Lab Runner */

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function colorLine(raw) {
  if (!raw) return '';
  const patterns = [
    [/^={3,}/, 'color:#58a6ff;font-weight:bold'],
    [/^─{2,}/, 'color:#30363d'],
    [/(✓|PASS|PASSED|BLOCKED|CLEAN|SUCCEEDED|Normal)/, 'color:#3fb950'],
    [/(✗|FAILED|ATTACK|POISONED|INJECTION|evil\.com|☠)/, 'color:#f85149'],
    [/(⚠|WARNING|PARTIAL|QUARANTINED)/, 'color:#f0883e'],
    [/^(Text:|Tokens:|IDs:|Count:)/, 'color:#58a6ff'],
    [/\[[\d.,\s-]+\]/, 'color:#bc8cff'],
  ];
  for (const [re, style] of patterns) {
    if (re.test(raw)) {
      return `<span style="${style}">${escHtml(raw)}</span>`;
    }
  }
  return escHtml(raw);
}

function runLab(scriptId, termSuffix) {
  const btn    = event.currentTarget || document.querySelector('.run-btn');
  const termEl = document.getElementById('term-' + termSuffix);
  const bodyEl = document.getElementById('body-' + termSuffix);
  const lblEl  = document.getElementById('lbl-' + termSuffix);

  if (!termEl || !bodyEl) return;

  btn.disabled = true;
  const origText = btn.textContent;
  btn.textContent = '⏳ Running…';
  bodyEl.innerHTML = '';
  termEl.classList.add('visible');
  if (lblEl) lblEl.textContent = 'running…';

  const es = new EventSource('/run/' + scriptId);

  es.onmessage = (e) => {
    if (e.data === '__DONE__') {
      es.close();
      btn.disabled = false;
      btn.textContent = origText;
      if (lblEl) lblEl.textContent = 'completed';
      bodyEl.innerHTML += `\n<span class="term-done">✓ script finished</span>`;
      bodyEl.scrollTop = bodyEl.scrollHeight;
      return;
    }
    const line = e.data.replace(/\\n/g, '\n');
    bodyEl.innerHTML += colorLine(line) + '\n';
    bodyEl.scrollTop = bodyEl.scrollHeight;
  };

  es.onerror = () => {
    es.close();
    btn.disabled = false;
    btn.textContent = origText;
    if (lblEl) lblEl.textContent = 'error';
    bodyEl.innerHTML += `\n<span style="color:var(--red)">Connection error — is server.py running?</span>\n`;
  };
}
