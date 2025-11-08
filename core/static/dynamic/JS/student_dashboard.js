// Student dashboard JS - full features + exam-level focus protections
document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const languageSection = document.getElementById('languageSection');
  const languageGrid = document.getElementById('languageGrid');
  const workspace = document.getElementById('workspace');
  const workspaceTitle = document.getElementById('workspaceTitle');
  const backToLang = document.getElementById('backToLang');
  const langSelect = document.getElementById('langSelect');
  const codeEditor = document.getElementById('codeEditor');
  const runBtn = document.getElementById('runBtn');
  const submitBtn = document.getElementById('submitBtn');
  const saveBtn = document.getElementById('saveBtn');
  const scoreEl = document.getElementById('score');
  const testsEl = document.getElementById('tests');
  const logicEl = document.getElementById('logic');
  const aiFeedback = document.getElementById('aiFeedback');
  const enterFocus = document.getElementById('enterFocus');
  const exitFocusBtn = document.getElementById('exitFocusBtn');
  const focusWarning = document.getElementById('focusWarning');
  const themeToggle = document.getElementById('themeToggle');

  // Theme persistence key
  const THEME_KEY = 'cq_theme';

  // Init theme from localStorage
  function applySavedTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'light') document.body.classList.add('light');
    updateThemeButton();
    applyEditorColors();
  }
  function updateThemeButton() {
    themeToggle.textContent = document.body.classList.contains('light') ? '☀️' : '🌙';
  }
  function applyEditorColors(){
    // Editor colors are controlled via CSS variables; ensure textarea colors updated
    if (document.body.classList.contains('light')) {
      codeEditor.style.background = getComputedStyle(document.documentElement).getPropertyValue('--editor-bg-dark') || '';
      codeEditor.style.color = getComputedStyle(document.documentElement).getPropertyValue('--editor-text-dark') || '';
    } else {
      codeEditor.style.background = getComputedStyle(document.documentElement).getPropertyValue('--editor-bg-dark') || '';
      codeEditor.style.color = getComputedStyle(document.documentElement).getPropertyValue('--editor-text-dark') || '';
    }
  }

  applySavedTheme();

  themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light');
    localStorage.setItem(THEME_KEY, document.body.classList.contains('light') ? 'light' : 'dark');
    updateThemeButton();
    applyEditorColors();
  });

  // LANGUAGE selection -> show workspace
  languageGrid.addEventListener('click', (e) => {
    const btn = e.target.closest('.lang-card');
    if (!btn) return;
    const lang = btn.dataset.lang;
    // set UI
    languageSection.classList.add('hidden');
    workspace.classList.remove('hidden');
    workspaceTitle.textContent = `Language: ${lang}`;
    // set select value if available
    Array.from(langSelect.options).forEach(opt => {
      if (opt.text.toLowerCase() === lang.toLowerCase()) opt.selected = true;
    });
    setTimeout(()=> codeEditor.focus(), 120);
  });

  backToLang.addEventListener('click', () => {
    workspace.classList.add('hidden');
    languageSection.classList.remove('hidden');
    // clear warning / focus if any
    if (document.body.classList.contains('focus-mode')) exitFocus();
  });

  // Mock run & submit
  runBtn.addEventListener('click', () => {
    runCodeMock();
  });
  submitBtn.addEventListener('click', () => {
    submitMock();
  });
  saveBtn.addEventListener('click', () => {
    localStorage.setItem('cq_draft', codeEditor.value);
    showToast('Draft saved locally');
  });

  // Ctrl/Cmd + Enter -> Run
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runBtn.click();
    }
  });

  // Toast helper
  function showToast(text, t=2000){
    // small temporary unobtrusive toast
    const el = document.createElement('div');
    el.textContent = text;
    el.style.position = 'fixed';
    el.style.bottom = '18px';
    el.style.left = '50%';
    el.style.transform = 'translateX(-50%)';
    el.style.background = 'linear-gradient(90deg,#a855f7,#06b6d4)';
    el.style.color = '#fff';
    el.style.padding = '8px 14px';
    el.style.borderRadius = '999px';
    el.style.zIndex = 9999;
    document.body.appendChild(el);
    setTimeout(()=> el.remove(), t);
  }

  // MOCK evaluation helpers
  function runCodeMock(){
    showToast('Running...', 900);
    setTimeout(()=> {
      aiFeedback.textContent = 'Output: (mock) Program executed.';
    }, 700);
  }
  function submitMock(){
    showToast('Submitting for AI evaluation...', 900);
    setTimeout(()=> {
      const txt = codeEditor.value || '';
      const hasReturn = /return\s+|print\(|console\.log|std::/.test(txt);
      const score = hasReturn ? Math.floor(7 + Math.random()*3) : Math.floor(3 + Math.random()*3);
      scoreEl.textContent = `${score}/10`;
      testsEl.textContent = hasReturn ? '4/5' : '2/5';
      logicEl.textContent = hasReturn ? '4/5' : '2/5';
      aiFeedback.textContent = hasReturn ? 'AI: Good core logic. Check edge cases.' : 'AI: Partial — missing final step.';
      applyRewards(score);
    }, 900);
  }
  // ----------------- FOCUS MODE + Exam protections -----------------
  let focusActive = false;
  // helper: request fullscreen (needs user gesture)
  function enterFullscreen(){
    const el = document.documentElement;
    if (el.requestFullscreen) return el.requestFullscreen();
    if (el.webkitRequestFullscreen) return el.webkitRequestFullscreen();
    if (el.msRequestFullscreen) return el.msRequestFullscreen();
    return Promise.resolve();
  }
  function exitFullscreen(){
    if (document.exitFullscreen) return document.exitFullscreen();
    if (document.webkitExitFullscreen) return document.webkitExitFullscreen();
    if (document.msExitFullscreen) return document.msExitFullscreen();
    return Promise.resolve();
  }

  // Disable actions while in focus-mode
  function disableExamKeys(e){
    // Block F12
    if (e.key === 'F12') { e.preventDefault(); showToast('Disabled in Focus Mode'); return; }
    // Block Ctrl/Cmd + Shift + I / J / C
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && ['I','J','C'].includes(e.key.toUpperCase())) { e.preventDefault(); showToast('Disabled in Focus Mode'); return; }
    // Block Ctrl/Cmd + U, S
    if ((e.ctrlKey || e.metaKey) && ['U','S'].includes(e.key.toUpperCase())) { e.preventDefault(); showToast('Disabled in Focus Mode'); return; }
  }
  function disableRightClick(e){ if (focusActive) { e.preventDefault(); showToast('Right-click disabled in Focus Mode'); } }
  function disableCopyPasteCut(e){ if (focusActive) { e.preventDefault(); showToast('Copy/Paste/Cut disabled in Focus Mode'); } }

  // On visibility change (tab switch)
  function handleVisibilityChange(){
    if (focusActive && document.hidden) {
      // show persistent warning banner
      focusWarning.classList.remove('hidden');
      focusWarning.textContent = '⚠️ You left Focus Mode (switching tabs is disabled). Return immediately.';
      // (Optional) Try to re-enter fullscreen (may be blocked in modern browsers)
      try { enterFullscreen(); } catch(_) {}
    } else {
      focusWarning.classList.add('hidden');
    }
  }

  // Enter Focus Mode (manual)
  enterFocus.addEventListener('click', async () => {
    if (focusActive) return;
    focusActive = true;
    document.body.classList.add('focus-mode');
    exitFocusBtn.classList.remove('hidden');
    // request fullscreen
    try { await enterFullscreen(); } catch(e){ /* may be blocked by browser */ }
    // attach protections
    window.addEventListener('keydown', disableExamKeys, true);
    window.addEventListener('contextmenu', disableRightClick, true);
    window.addEventListener('copy', disableCopyPasteCut, true);
    window.addEventListener('paste', disableCopyPasteCut, true);
    window.addEventListener('cut', disableCopyPasteCut, true);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', () => { if (focusActive) { focusWarning.classList.remove('hidden'); }});
    // focus on editor
    setTimeout(()=> { codeEditor.focus(); codeEditor.scrollIntoView(); }, 150);
    showToast('Entered Focus Mode — good luck!', 1600);
  });

  // Exit Focus Mode: restore everything
  async function exitFocus(){
    focusActive = false;
    document.body.classList.remove('focus-mode');
    exitFocusBtn.classList.add('hidden');
    focusWarning.classList.add('hidden');
    // remove protections
    window.removeEventListener('keydown', disableExamKeys, true);
    window.removeEventListener('contextmenu', disableRightClick, true);
    window.removeEventListener('copy', disableCopyPasteCut, true);
    window.removeEventListener('paste', disableCopyPasteCut, true);
    window.removeEventListener('cut', disableCopyPasteCut, true);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    // exit fullscreen
    try { await exitFullscreen(); } catch(e){}
    showToast('Exited Focus Mode', 1200);
    setTimeout(()=> codeEditor.focus(), 200);
  }

  exitFocusBtn.addEventListener('click', () => {
    // Ask for confirmation to exit an exam-like mode
    const ok = confirm('Exit Focus Mode? This will allow copy/paste and switching tabs.');
    if (ok) exitFocus();
  });

  // Also exit on Esc (only when focus is active)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && focusActive) {
      const ok = confirm('Exit Focus Mode?');
      if (ok) exitFocus();
    }
  });

  // Protect against right-click globally when focus active
  window.addEventListener('contextmenu', (e) => { if (focusActive) e.preventDefault(); }, true);

  // Prevent common devtools shortcuts outside focus too? only active in focus
  // Already handled in disableExamKeys

  // Save/load draft
  const draftKey = 'cq_draft';
  const savedDraft = localStorage.getItem(draftKey);
  if (savedDraft) codeEditor.value = savedDraft;

  // Basic autosave every 8s (not blocking)
  setInterval(()=> { localStorage.setItem(draftKey, codeEditor.value); }, 8000);

  // Initial small UI polish
  applyEditorColors();

  // Done
  console.log('Student dashboard loaded');
});
document.getElementById("runBtn").addEventListener("click", async () => {
  const code = document.getElementById("codeEditor").value;
  const language = document.getElementById("langSelect").value;

  // Optional: Get the example input/output from the current question
  const input = document.querySelector(".example").innerText.split("→")[0].replace("Input:", "").trim();
  const expected = document.querySelector(".example").innerText.split("→")[1].replace("Output:", "").trim();

  const formData = new FormData();
  formData.append("code", code);
  formData.append("language", language);
  formData.append("input", input);
  formData.append("expected", expected);

  const response = await fetch("/run_code/", {
    method: "POST",
    body: formData,
    headers: { "X-CSRFToken": getCookie("csrftoken") } // CSRF token for Django
  });

  const result = await response.json();
  document.getElementById("score").innerText = result.is_correct ? "✅ Correct" : "❌ Wrong";
  document.getElementById("logic").innerText = result.is_correct ? "Logic OK" : "Check Logic";
  document.getElementById("aiFeedback").innerText = result.ai_feedback;
});

// Helper function to read CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
