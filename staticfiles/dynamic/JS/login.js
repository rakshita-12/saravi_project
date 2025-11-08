document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");

  // Apply stored theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light");
    themeToggle.textContent = "☀️";
  }

  // Toggle theme
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    themeToggle.textContent = isLight ? "☀️" : "🌙";
    localStorage.setItem("theme", isLight ? "light" : "dark");
  });

  // Form redirects (simulate backend until connected)
  const studentForm = document.getElementById("studentLoginForm");
  const facultyForm = document.getElementById("facultyLoginForm");

  if (studentForm) {
    studentForm.addEventListener("submit", (e) => {
      e.preventDefault();
      window.location.href = "../student/student-dashboard.html";
    });
  }

  if (facultyForm) {
    facultyForm.addEventListener("submit", (e) => {
      e.preventDefault();
      window.location.href = "../faculty/faculty-dashboard.html";
    });
  }
});
