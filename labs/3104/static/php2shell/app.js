const form = document.querySelector('#import-form');
const result = document.querySelector('#result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.className = 'result loading';
  result.textContent = '자료 구조와 파일 메타데이터를 검증하고 있습니다…';
  try {
    const response = await fetch(form.action, { method: 'POST', body: new FormData(form), credentials: 'same-origin' });
    const data = await response.json();
    result.className = response.ok ? 'result success' : 'result error';
    result.textContent = data.message || data.error || `HTTP ${response.status}`;
  } catch (error) {
    result.className = 'result error';
    result.textContent = '자료 검증 요청을 처리하지 못했습니다.';
  }
});
