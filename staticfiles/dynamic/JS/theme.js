const toggle = document.getElementById('theme-toggle');
const saved = localStorage.getItem('cq_theme'); // 'light' or 'dark'

function setTheme(theme){
  if(theme === 'light') {
    document.body.classList.add('light-theme');
    toggle.textContent = '☀️';
    localStorage.setItem('cq_theme','light');
  } else {
    document.body.classList.remove('light-theme');
    toggle.textContent = '🌙';
    localStorage.setItem('cq_theme','dark');
  }
}

// apply saved or default
if(saved === 'light') setTheme('light'); else setTheme('dark');

// toggle
toggle.addEventListener('click', ()=>{
  const isLight = document.body.classList.toggle('light-theme');
  setTheme(isLight ? 'light' : 'dark');
});
