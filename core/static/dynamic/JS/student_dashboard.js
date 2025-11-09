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
  
  // Store current question ID
  let currentQuestionId = null;

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

  // "Solve Challenge" button handler
  document.querySelectorAll('.btn-solve').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const questionId = btn.getAttribute('data-question-id');
      currentQuestionId = questionId;
      
      try {
        // Fetch question details
        const response = await fetch(`/student/question/${questionId}/`);
        const question = await response.json();
        
        if (question.error) {
          alert(question.error);
          return;
        }
        
        // Hide questions grid, show language selection
        document.querySelector('.questions-section').classList.add('hidden');
        languageSection.classList.remove('hidden');
        
        // Store question data for later use
        window.currentQuestion = question;
        
      } catch (error) {
        console.error('Error fetching question:', error);
        alert('Failed to load question details');
      }
    });
  });

  // LANGUAGE selection -> show workspace
  languageGrid.addEventListener('click', (e) => {
    const btn = e.target.closest('.lang-card');
    if (!btn) return;
    const lang = btn.dataset.lang;
    
    // Load question details if available
    if (window.currentQuestion) {
      const q = window.currentQuestion;
      document.getElementById('challengeTitle').textContent = q.title;
      document.getElementById('challengeDesc').textContent = q.description;
      document.getElementById('questionDifficulty').textContent = q.difficulty;
      document.getElementById('questionMarks').textContent = q.marks;
      document.getElementById('exampleInput').textContent = q.example_input;
      document.getElementById('exampleOutput').textContent = q.example_output;
      document.getElementById('questionConstraints').textContent = q.constraints;
      document.getElementById('questionDetails').style.display = 'block';
    }
    
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
    // Clear code editor when going back
    codeEditor.value = '// Start coding here...';
    localStorage.removeItem('cq_draft');
  });
  
  // Add "Back to Questions" functionality
  const backToQuestions = () => {
    workspace.classList.add('hidden');
    languageSection.classList.add('hidden');
    document.querySelector('.questions-section').classList.remove('hidden');
    currentQuestionId = null;
    window.currentQuestion = null;
  };

  // Run code (real implementation below at line 365)
  submitBtn.addEventListener('click', async () => {
    if (!currentQuestionId) {
      showToast('Please select a question first', 2000);
      return;
    }
    
    const code = codeEditor.value;
    const language = langSelect.value;
    
    if (!code.trim()) {
      showToast('Please write some code first', 2000);
      return;
    }
    
    try {
      showToast('Submitting for evaluation...', 1500);
      
      const response = await fetch(`/student/submit/${currentQuestionId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          code: code,
          language: language
        })
      });
      
      const data = await response.json();
      
      if (data.error) {
        showToast('Submission failed: ' + data.error, 3000);
        return;
      }
      
      // Extract the actual result (nested under 'result' key)
      const result = data.result;
      
      // Display results
      scoreEl.textContent = `${result.score}%`;
      const passedTests = result.results.filter(r => r.is_correct).length;
      testsEl.textContent = `${passedTests}/${result.results.length}`;
      logicEl.textContent = result.score >= 70 ? 'Passed' : result.score >= 40 ? 'Partial' : 'Failed';
      
      // Build comprehensive feedback for all tests
      let feedbackText = '';
      result.results.forEach((test, index) => {
        const testNum = index + 1;
        const status = test.is_correct ? '✓ Passed' : '✗ Failed';
        
        feedbackText += `Test ${testNum}: ${status}\n`;
        
        if (test.error && test.error !== '') {
          feedbackText += `Error: ${test.error}\n`;
        } else {
          if (!test.is_correct) {
            feedbackText += `Expected: ${test.expected}\n`;
            feedbackText += `Got: ${test.output || '(no output)'}\n`;
          } else {
            feedbackText += `Output: ${test.output}\n`;
          }
        }
        
        // Add AI feedback if available and not an error message
        if (test.ai_feedback && !isAIErrorMessage(test.ai_feedback)) {
          feedbackText += `Feedback: ${test.ai_feedback}\n`;
        }
        
        feedbackText += '\n';
      });
      
      aiFeedback.textContent = feedbackText.trim() || 'No feedback available';
      
      showToast(`Submission complete! Score: ${result.score}%`, 3000);
      
    } catch (error) {
      console.error('Submission error:', error);
      showToast('Failed to submit code. Please try again.', 3000);
    }
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

  // Save/load draft - DO NOT load on page load
  const draftKey = 'cq_draft';
  // Clear draft when page loads (fresh start each session)
  localStorage.removeItem(draftKey);

  // Basic autosave every 8s (not blocking)
  setInterval(()=> { localStorage.setItem(draftKey, codeEditor.value); }, 8000);

  // Initial small UI polish
  applyEditorColors();

  // Run button handler
  runBtn.addEventListener("click", async () => {
  const code = document.getElementById("codeEditor").value;
  const language = document.getElementById("langSelect").value;

  // Get example input/output if available, otherwise use empty strings
  let input = "";
  let expected = "";
  
  const exampleInputEl = document.getElementById("exampleInput");
  const exampleOutputEl = document.getElementById("exampleOutput");
  
  if (exampleInputEl && exampleInputEl.textContent) {
    input = exampleInputEl.textContent.trim();
  }
  if (exampleOutputEl && exampleOutputEl.textContent) {
    expected = exampleOutputEl.textContent.trim();
  }

  const formData = new FormData();
  formData.append("code", code);
  formData.append("language", language);
  formData.append("input", input);
  formData.append("expected", expected);

  try {
    showToast('Running code...', 1500);
    const response = await fetch("/student/run_code/", {
      method: "POST",
      body: formData,
      headers: { "X-CSRFToken": getCookie("csrftoken") }
    });

    const result = await response.json();
    
    if (result.error) {
      showToast('Error: ' + result.error, 3000);
      return;
    }
    
    // Display results
    document.getElementById("score").innerText = result.score + '%';
    document.getElementById("logic").innerText = result.is_correct ? "✅ Correct" : "❌ Wrong";
    
    // Build detailed feedback
    let feedbackText = 'Run Test Results:\n\n';
    if (result.error && result.error !== '') {
      feedbackText += `Error: ${result.error}\n`;
    } else {
      feedbackText += `Status: ${result.is_correct ? '✓ Passed' : '✗ Failed'}\n`;
      feedbackText += `Output: ${result.output || '(no output)'}\n`;
      
      if (!result.is_correct) {
        // Get the expected output from the page if available
        const exampleOutputEl = document.getElementById("exampleOutput");
        const expectedOutput = exampleOutputEl ? exampleOutputEl.textContent.trim() : '';
        if (expectedOutput) {
          feedbackText += `Expected: ${expectedOutput}\n`;
        }
      }
      
      feedbackText += '\n';
      
      // Add AI feedback if available and not an error message
      if (result.ai_feedback && !isAIErrorMessage(result.ai_feedback)) {
        feedbackText += `AI Feedback: ${result.ai_feedback}`;
      }
    }
    
    document.getElementById("aiFeedback").innerText = feedbackText.trim();
    
    showToast('Code executed!', 2000);
  } catch (error) {
    console.error('Run error:', error);
    showToast('Failed to run code. Please try again.', 3000);
  }
  });

  // Helper function to check if feedback is an AI error message
  function isAIErrorMessage(feedback) {
    if (!feedback) return true;
    
    const errorPatterns = [
      'Ollama is not running',
      'AI service error',
      'AI service unavailable',
      'AI model loading',
      'AI analysis timed out',
      'Network error during AI',
      'Unexpected error during AI',
      'client_error',
      'server_error',
      'model_loading',
      'timeout',
      'Enable AI for detailed logic analysis'
    ];
    
    return errorPatterns.some(pattern => feedback.includes(pattern));
  }

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

  // Done
  console.log('Student dashboard loaded');
});
