// Theme Toggle Logic
const themeToggle = document.getElementById("themeToggle");
const body = document.body;

// Load saved theme
if (localStorage.getItem("theme") === "light") {
  body.classList.add("light-mode");
  themeToggle.textContent = "☀️";
}

themeToggle.addEventListener("click", () => {
  body.classList.toggle("light-mode");
  const isLight = body.classList.contains("light-mode");
  themeToggle.textContent = isLight ? "☀️" : "🌙";
  localStorage.setItem("theme", isLight ? "light" : "dark");
});

// Group Management Logic
const createGroupBtn = document.getElementById("createGroupBtn");
const groupNameInput = document.getElementById("groupNameInput");
const groupList = document.getElementById("groupList");

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

async function loadGroups() {
  try {
    const response = await fetch('/faculty/groups/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });

    if (response.ok) {
      const data = await response.json();
      allGroups = data.groups;
      displayGroups(data.groups);
    } else {
      console.error('Failed to load groups');
    }
  } catch (error) {
    console.error('Error loading groups:', error);
  }
}

function displayGroups(groups) {
  if (groups.length === 0) {
    groupList.innerHTML = '<p class="empty-state">No groups yet. Create one above.</p>';
    return;
  }

  groupList.innerHTML = groups.map(group => `
    <div class="group-card">
      <h4>${group.name}</h4>
      <p>${group.student_count} student${group.student_count !== 1 ? 's' : ''}</p>
      ${group.students.length > 0 ? `
        <ul>
          ${group.students.map(student => `<li>${student.username}</li>`).join('')}
        </ul>
      ` : '<p class="empty-state">No students in this group yet.</p>'}
    </div>
  `).join('');
}

async function createGroup() {
  const groupName = groupNameInput.value.trim();

  if (!groupName) {
    alert('Please enter a group name');
    return;
  }

  try {
    const response = await fetch('/faculty/groups/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ name: groupName })
    });

    const data = await response.json();

    if (response.ok) {
      groupNameInput.value = '';
      await loadGroups();
      alert(data.message || 'Group created successfully!');
    } else {
      alert(data.error || 'Failed to create group');
    }
  } catch (error) {
    console.error('Error creating group:', error);
    alert('An error occurred while creating the group');
  }
}

createGroupBtn.addEventListener('click', createGroup);

groupNameInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    createGroup();
  }
});

let allGroups = [];
let allStudents = [];

async function loadAllData() {
  await loadGroups();
  await loadStudents();
}

async function loadStudents() {
  try {
    const response = await fetch('/faculty/students/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });

    if (response.ok) {
      const data = await response.json();
      allStudents = data.students;
      displayStudents(data.students);
    } else {
      console.error('Failed to load students');
    }
  } catch (error) {
    console.error('Error loading students:', error);
  }
}

function displayStudents(students) {
  const studentList = document.getElementById('studentList');
  
  if (students.length === 0) {
    studentList.innerHTML = '<p class="empty-state">No students found.</p>';
    return;
  }

  studentList.innerHTML = `
    <table style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr style="background: rgba(255, 255, 255, 0.05); text-align: left;">
          <th style="padding: 0.7rem; border-bottom: 2px solid rgba(255, 255, 255, 0.1);">Student Name</th>
          <th style="padding: 0.7rem; border-bottom: 2px solid rgba(255, 255, 255, 0.1);">Current Group</th>
          <th style="padding: 0.7rem; border-bottom: 2px solid rgba(255, 255, 255, 0.1);">Assign to Group</th>
        </tr>
      </thead>
      <tbody>
        ${students.map(student => `
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <td style="padding: 0.7rem;">${student.username}</td>
            <td style="padding: 0.7rem;">${student.group_name || '<em style="color: #999;">No group</em>'}</td>
            <td style="padding: 0.7rem;">
              <select 
                id="student-${student.id}" 
                data-student-id="${student.id}"
                style="padding: 0.5rem; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(0, 0, 0, 0.3); color: white; cursor: pointer;"
                onchange="assignStudentToGroup(${student.id}, this.value)"
              >
                <option value="">-- Select Group --</option>
                ${allGroups.map(group => `
                  <option value="${group.id}" ${student.group_id === group.id ? 'selected' : ''}>
                    ${group.name}
                  </option>
                `).join('')}
              </select>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

async function assignStudentToGroup(studentId, groupId) {
  try {
    const response = await fetch('/faculty/students/assign/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ 
        student_id: studentId, 
        group_id: groupId || null 
      })
    });

    const data = await response.json();

    if (response.ok) {
      await loadAllData();
      alert(data.message || 'Student assigned successfully!');
    } else {
      alert(data.error || 'Failed to assign student');
      await loadStudents();
    }
  } catch (error) {
    console.error('Error assigning student:', error);
    alert('An error occurred while assigning the student');
  }
}

window.assignStudentToGroup = assignStudentToGroup;

loadAllData();
