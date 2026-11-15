const form = document.querySelector('#search-form');
const query = document.querySelector('#query');
const results = document.querySelector('#results');
const summary = document.querySelector('#search-summary');
const proof = document.querySelector('#xss-proof');

function escapeText(value) { const node = document.createElement('span'); node.textContent = value; return node.innerHTML; }
function renderRows(items) {
  results.innerHTML = items.map(item => `<tr><td>${escapeText(item.id)}</td><td><strong>${escapeText(item.title)}</strong></td><td>${escapeText(item.agency)}</td><td>${escapeText(item.deadline)}</td><td><span class="status${item.status === '마감임박' ? ' warn' : ''}">${escapeText(item.status)}</span></td></tr>`).join('') || '<tr><td colspan="5">검색 결과가 없습니다.</td></tr>';
}
async function search() {
  const response = await fetch(`/api/research/search?q=${encodeURIComponent(query.value)}`);
  const data = await response.json();
  summary.innerHTML = data.query ? `<strong>${data.query}</strong> 검색 결과 <b>${data.count}</b>건` : `전체 공고 <b>${data.count}</b>건`;
  renderRows(data.items);
}
form.addEventListener('submit', event => {
  event.preventDefault();
  const url = new URL(window.location.href);
  if (query.value) url.searchParams.set('q', query.value); else url.searchParams.delete('q');
  history.replaceState(null, '', url);
  search();
});
document.querySelector('#reset').addEventListener('click', () => {
  query.value = '';
  const url = new URL(window.location.href);
  url.searchParams.delete('q');
  history.replaceState(null, '', url);
  proof.textContent = '검색 결과 안내 영역';
  proof.dataset.state = 'idle';
  search();
});
query.value = new URLSearchParams(window.location.search).get('q') || '';
search();
