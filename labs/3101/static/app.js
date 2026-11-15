const elements = {
  form: document.querySelector('#search-form'),
  date: document.querySelector('#schedule-date'),
  query: document.querySelector('#schedule-query'),
  body: document.querySelector('#schedule-body'),
  message: document.querySelector('#result-message'),
  reset: document.querySelector('#reset-button'),
};

async function getJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `요청 처리에 실패했습니다. (${response.status})`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function statusClass(status) {
  if (status === '대기') return 'wait';
  if (status === '변경검토') return 'review';
  return '';
}

async function loadSchedules() {
  elements.body.innerHTML = '<tr><td colspan="8" class="loading">일정을 조회하는 중입니다.</td></tr>';
  elements.message.className = 'result-message';
  elements.message.textContent = '';

  const parameters = new URLSearchParams({
    date: elements.date.value,
    query: elements.query.value,
  });

  try {
    const data = await getJson(`/api/schedules?${parameters}`);
    elements.message.textContent = `조회 결과 ${data.count}건 · 기준일 ${data.date}`;
    if (!data.items.length) {
      elements.body.innerHTML = '<tr><td colspan="8" class="empty">조건에 맞는 승무일정이 없습니다.</td></tr>';
      return;
    }
    elements.body.innerHTML = data.items.map((item) => `
      <tr>
        <td><strong>${escapeHtml(item.report_time)}</strong><small>${escapeHtml(item.depot)}</small></td>
        <td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.employee_no)}</small></td>
        <td>${escapeHtml(item.role)}</td>
        <td><strong>${escapeHtml(item.train_no)}</strong></td>
        <td>${escapeHtml(item.route)}</td>
        <td>${escapeHtml(item.release_time)}</td>
        <td>${escapeHtml(item.platform)}</td>
        <td><span class="status ${statusClass(item.duty_status)}">${escapeHtml(item.duty_status)}</span></td>
      </tr>
    `).join('');
  } catch (error) {
    elements.message.className = 'result-message error';
    elements.message.textContent = error.message;
    elements.body.innerHTML = '<tr><td colspan="8" class="empty">일정 정보를 표시할 수 없습니다.</td></tr>';
  }
}

elements.form.addEventListener('submit', (event) => {
  event.preventDefault();
  loadSchedules();
});

elements.reset.addEventListener('click', () => {
  elements.query.value = '';
  elements.date.value = '2026-11-05';
  loadSchedules();
});

loadSchedules();
