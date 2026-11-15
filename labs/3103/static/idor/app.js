const form = document.querySelector('#lookup-form');
const input = document.querySelector('#order-id');
const message = document.querySelector('#message');
const detail = document.querySelector('#detail');
function text(value) { const node = document.createElement('span'); node.textContent = value ?? '-'; return node.innerHTML; }
function field(label, value, wide = false) { return `<div class="field${wide ? ' wide' : ''}"><span>${text(label)}</span><strong>${text(value)}</strong></div>`; }
async function lookup() {
  const response = await fetch(`/api/work-orders?id=${encodeURIComponent(input.value.trim())}`);
  const data = await response.json();
  if (!response.ok) { message.textContent = data.error; detail.innerHTML = ''; return; }
  const item = data.work_order;
  message.textContent = `${item.id} · ${item.classification} · ${item.status}`;
  detail.innerHTML = field('작업지시번호', item.id) + field('상태', item.status) + field('보안등급', item.classification) + field('작업명', item.title, true) + field('대상시설', item.site) + field('담당부서', item.division) + field('담당자', item.assignee) + field('작업시간', item.window) + field('위험도', item.risk) + field('검증표식', item.evidence || '해당 없음') + field('작업범위', item.scope, true);
}
form.addEventListener('submit', event => { event.preventDefault(); lookup(); });
lookup();
