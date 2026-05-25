const userId = localStorage.getItem('user_id');

// Профиль ученика
const profileForm = document.getElementById('profileForm');
if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorDiv = document.getElementById('error');

        const response = await fetch('/api/students/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: parseInt(userId),
                last_name: document.getElementById('last_name').value,
                first_name: document.getElementById('first_name').value,
                middle_name: document.getElementById('middle_name').value,
                age: parseInt(document.getElementById('age').value),
                phone: document.getElementById('phone').value,
                about: document.getElementById('about').value
            })
        });

        const data = await response.json();
        if (response.ok) {
            window.location.href = '/student/tutors.html';
        } else {
            errorDiv.textContent = data.detail;
            errorDiv.classList.remove('d-none');
        }
    });
}

// Загрузка репетиторов
async function loadTutors() {
    const subjectId = document.getElementById('subjectFilter')?.value;
    const url = subjectId
        ? `/api/students/tutors?subject_id=${subjectId}`
        : '/api/students/tutors';

    const response = await fetch(url);
    const tutors = await response.json();
    const container = document.getElementById('tutorsList');
    if (!container) return;

    if (tutors.length === 0) {
        container.innerHTML = '<p class="text-muted">Репетиторы не найдены</p>';
        return;
    }

    container.innerHTML = tutors.map(t => `
        <div class="col-md-4 mb-3">
            <div class="card h-100">
                <div class="card-body">
                    <h5>${t.last_name} ${t.first_name} ${t.middle_name || ''}</h5>
                    <p class="text-muted">Опыт: ${t.experience} лет</p>
                    <p>${t.subjects.map(s =>
                        `<span class="badge bg-primary">${s.name}</span>`
                    ).join(' ')}</p>
                    <p>${t.about || ''}</p>
                    <a href="/student/apply.html?tutor_id=${t.id}"
                       class="btn btn-outline-primary">Отправить заявку</a>
                </div>
            </div>
        </div>
    `).join('');
}

// Загрузка фильтра предметов
async function loadSubjectFilter() {
    const filter = document.getElementById('subjectFilter');
    if (!filter) return;

    const response = await fetch('/api/students/subjects');
    const subjects = await response.json();
    subjects.forEach(s => {
        const option = document.createElement('option');
        option.value = s.id;
        option.textContent = s.name;
        filter.appendChild(option);
    });
}

// Страница заявки
async function loadApplyPage() {
    const form = document.getElementById('applyForm');
    if (!form) return;

    const params = new URLSearchParams(window.location.search);
    const tutorId = params.get('tutor_id');

    const response = await fetch(`/api/students/tutor-subjects/${tutorId}`);
    const subjects = await response.json();
    const select = document.getElementById('subject_id');
    const customSubjectDiv = document.getElementById('customSubjectDiv');
    const customSubjectInput = document.getElementById('custom_subject');

    subjects.forEach(s => {
        const option = document.createElement('option');
        option.value = s.id;
        option.textContent = s.name;
        select.appendChild(option);
    });

    const customOption = document.createElement('option');
    customOption.value = 'custom';
    customOption.textContent = 'Свой предмет';
    select.appendChild(customOption);

    select.addEventListener('change', () => {
        if (select.value === 'custom') {
            customSubjectDiv.style.display = 'block';
            customSubjectInput.required = true;
        } else {
            customSubjectDiv.style.display = 'none';
            customSubjectInput.required = false;
            customSubjectInput.value = '';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorDiv = document.getElementById('error');
        const successDiv = document.getElementById('success');

        if (!select.value) {
            errorDiv.textContent = 'Пожалуйста выберите предмет';
            errorDiv.classList.remove('d-none');
            return;
        }

        if (select.value === 'custom' && !customSubjectInput.value.trim()) {
            errorDiv.textContent = 'Пожалуйста укажите свой предмет';
            errorDiv.classList.remove('d-none');
            return;
        }

        errorDiv.classList.add('d-none');

        const studentResponse = await fetch(`/api/students/profile/${userId}`);
        const studentData = await studentResponse.json();

        const subjectId = select.value !== 'custom' ? parseInt(select.value) : null;
        const customSubject = select.value === 'custom' ? customSubjectInput.value.trim() : null;

        const applyResponse = await fetch('/api/students/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentData.id,
                tutor_id: parseInt(tutorId),
                subject_id: subjectId,
                custom_subject: customSubject
            })
        });

        if (applyResponse.ok) {
            successDiv.textContent = 'Заявка отправлена!';
            successDiv.classList.remove('d-none');
            setTimeout(() => window.location.href = '/student/tutors.html', 1500);
        } else {
            const data = await applyResponse.json();
            errorDiv.textContent = data.detail;
            errorDiv.classList.remove('d-none');
        }
    });
}

// Выход
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.clear();
        window.location.href = '/';
    });
}

// Инициализация
loadSubjectFilter();
if (!document.getElementById('expMin')) {
    loadTutors();
}
loadApplyPage();