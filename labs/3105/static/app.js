const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = value => { const node = document.createElement('span'); node.textContent = String(value ?? ''); return node.innerHTML; };
const money = value => `${Number(value).toLocaleString('ko-KR')}원`;
const state = { programs: [], notices: [], projects: [], archive: [] };
const publicPages = new Set(['home', 'intro', 'programs', 'news', 'communication', 'manuals', 'rnd-info']);
const workLabels = { 'work-dashboard': '업무 홈', 'work-projects': '과제관리 > 수행과제 현황', 'work-analytics': '성과관리 > 연구성과 조회', 'work-evaluation': '평가관리 > 연구수행문의', 'work-archive': '자료·보고서 > 업무자료실', 'work-reports': '통계·내보내기 > 연구데이터' };

async function api(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...(options.headers || {}) } });
  const data = await response.json().catch(() => ({ error: '응답을 해석할 수 없습니다.' }));
  if (!response.ok) throw Object.assign(new Error(data.error || '요청을 처리하지 못했습니다.'), { data });
  return data;
}
function toast(message) { const box = $('#toast'); box.textContent = message; box.hidden = false; clearTimeout(toast.timer); toast.timer = setTimeout(() => box.hidden = true, 2500); }
function setHash(route) { if (location.hash.slice(1) !== route) location.hash = route; else routeView(route); }
function routeView(route = 'home') {
  const isPublic = publicPages.has(route);
  $('#public-shell').hidden = !isPublic;
  $('#work-shell').hidden = isPublic;
  if (isPublic) {
    $$('.public-page').forEach(page => page.hidden = page.dataset.publicPage !== route);
    loadPublic(route);
  } else {
    const page = workLabels[route] ? route : 'work-dashboard';
    $$('.work-page').forEach(el => el.hidden = el.dataset.workPage !== page);
    $$('[data-work-route]').forEach(button => button.classList.toggle('active', button.dataset.workRoute === page));
    $('#work-breadcrumb').textContent = workLabels[page];
    loadWork(page);
  }
  window.scrollTo(0, 0);
}
function loadPublic(page) {
  if (page === 'home') Promise.all([loadPublicPrograms(), loadPublicNotices()]);
  if (page === 'programs') loadProgramTable();
  if (page === 'news') loadNoticeTable();
}
function loadWork(page) {
  if (page === 'work-projects') loadProjects();
  if (page === 'work-analytics') loadAnalytics();
  if (page === 'work-evaluation') loadQna();
  if (page === 'work-archive') loadArchive();
}

async function loadProfile() {
  const data = await api('/api/v1/profile');
  $('#user-name').textContent = data.user.name;
  $('#user-org').textContent = data.user.org;
}
async function fetchPrograms(q = '', status = 'all') { return api(`/api/v1/programs?q=${encodeURIComponent(q)}&status=${encodeURIComponent(status)}`); }
async function loadPublicPrograms() {
  const q = $('#public-program-q').value;
  const data = await fetchPrograms(q, 'all');
  const agency = $('#public-agency').value;
  const items = agency === 'all' ? data.items : data.items.filter(item => agency === '한국연구재단');
  $('#public-program-list').innerHTML = items.map(item => `<div class="business-row"><span><i class="status-pill ${item.status === '접수중' ? 'open' : item.status === '마감' ? 'closed' : ''}">${esc(item.status)}</i></span><span>과학기술정보통신부</span><b>${esc(item.name)}</b><span>한국연구재단</span><span>2026.11.01 ~ ${esc(item.deadline)}</span><span class="d-day">${item.status === '마감' ? '마감' : 'D-20'}</span></div>`).join('') || '<div class="business-row"><b>조건에 맞는 사업공고가 없습니다.</b></div>';
}
async function loadProgramTable() {
  const data = await fetchPrograms($('#program-q').value, $('#program-status').value);
  state.programs = data.items; $('#program-count').textContent = data.count;
  $('#program-rows').innerHTML = data.items.map(item => `<tr><td><span class="status-pill ${item.status === '접수중' ? 'open' : item.status === '마감' ? 'closed' : ''}">${esc(item.status)}</span></td><td>${esc(item.id)}</td><td><b>${esc(item.name)}</b></td><td>${esc(item.division)}</td><td>${esc(item.deadline)}</td><td>${esc(item.budget)}</td></tr>`).join('') || '<tr><td colspan="6">검색 결과가 없습니다.</td></tr>';
}
async function fetchNotices(category = 'all') { return api(`/api/v1/notices?category=${encodeURIComponent(category)}`); }
async function loadPublicNotices() {
  const data = await fetchNotices();
  $('#public-notice-list').innerHTML = data.items.slice(0, 3).map(item => `<div class="public-notice-row"><b>${esc(item.title)}</b><span>${esc(item.date)}</span></div>`).join('');
}
async function loadNoticeTable() {
  const data = await fetchNotices($('#notice-category').value);
  const term = $('#notice-q').value.trim().toLowerCase();
  const items = data.items.filter(item => !term || item.title.toLowerCase().includes(term));
  $('#notice-rows').innerHTML = items.map((item, index) => `<tr><td>${data.count - index}</td><td>${esc(item.category)}</td><td><b>${esc(item.title)}</b></td><td>${esc(item.date)}</td><td>${Number(item.views).toLocaleString()}</td></tr>`).join('') || '<tr><td colspan="5">검색 결과가 없습니다.</td></tr>';
}

async function loadProjects() {
  const data = await api('/api/v1/projects/mine'); state.projects = data.items; $('#project-count').textContent = data.count;
  $('#project-rows').innerHTML = data.items.map(item => `<tr><td>${esc(item.id)}</td><td><b>${esc(item.title)}</b></td><td>${esc(item.pi)}</td><td>${esc(item.period)}</td><td><span class="status-pill open">${esc(item.stage)}</span></td><td>${money(item.budget)}</td><td><button class="outline" data-settlement="${esc(item.id)}">정산 현황</button></td></tr>`).join('');
  $$('[data-settlement]').forEach(button => button.addEventListener('click', () => loadSettlement(button.dataset.settlement)));
}
async function loadSettlement(id) {
  const data = await api(`/api/v1/projects/${encodeURIComponent(id)}/settlement`); const item = data.settlement; const box = $('#settlement-view'); box.hidden = false;
  box.innerHTML = `<header><b>연구비 집행 상세</b><span>${esc(item.id)}</span></header><dl><div><dt>과제명</dt><dd>${esc(item.title)}</dd></div><div><dt>총 연구비</dt><dd>${money(item.budget)}</dd></div><div><dt>집행액</dt><dd>${money(item.spent)}</dd></div><div><dt>집행률</dt><dd>${(item.spent / item.budget * 100).toFixed(1)}%</dd></div></dl>${data.evidence ? `<div class="access-proof"><b>권한 검증 실패</b><span>로그인 기관 ${esc(data.viewer.org_id)} → 조회된 과제 기관 ${esc(item.org_id)}</span><code>${esc(data.evidence)}</code></div>` : ''}`;
}
async function loadAnalytics() {
  const error = $('#analytics-error'); error.hidden = true;
  try {
    const data = await api(`/api/v1/analytics/publications?q=${encodeURIComponent($('#analytics-q').value)}&year=${encodeURIComponent($('#analytics-year').value)}`);
    $('#analytics-count').textContent = data.count;
    $('#analytics-rows').innerHTML = data.items.map(item => `<tr><td><input type="checkbox" aria-label="${esc(item.id)} 선택"></td><td>${esc(item.id)}</td><td><b>${esc(item.title)}</b></td><td>${esc(item.field)}</td><td>${esc(item.year)}</td><td>${esc(item.lead_org)}</td><td><span class="status-pill open">공개</span></td></tr>`).join('') || '<tr><td colspan="7">조회된 성과가 없습니다.</td></tr>';
  } catch (err) { error.hidden = false; error.textContent = `${err.message}${err.data?.database_error ? ` · ${err.data.database_error}` : ''}`; $('#analytics-rows').innerHTML = ''; }
}
async function loadQna() {
  const data = await api('/api/v1/qna'); $('#qna-count').textContent = data.count;
  // Stored messages are deliberately rendered as HTML in this training view.
  $('#qna-list').innerHTML = data.items.map(item => `<article class="qna-item"><span>처리중</span><div><b>${esc(item.subject)}</b><p class="qna-message">${item.message}</p></div><span>${esc(item.author)} · ${esc(item.date)}</span></article>`).join('');
}
async function loadArchive() { const data = await api('/api/v1/archive/list'); state.archive = data.items; renderArchive(); }
function renderArchive() {
  const term = $('#archive-filter').value.trim().toLowerCase(); const items = state.archive.filter(item => !term || item.name.toLowerCase().includes(term));
  $('#archive-rows').innerHTML = items.map((item, index) => `<tr><td>${items.length - index}</td><td><b>${esc(item.name)}</b></td><td>${esc(item.file)}</td><td>${esc(item.size)}</td><td>2026.11.01</td><td><button class="outline" data-file="${esc(item.file)}">미리보기</button></td></tr>`).join('');
  $$('[data-file]').forEach(button => button.addEventListener('click', () => previewDocument(button.dataset.file)));
}
async function previewDocument(file) { try { const data = await api(`/api/v1/archive/download?file=${encodeURIComponent(file)}`); $('#archive-preview').textContent = `[${data.classification}] ${data.resolved}\n\n${data.content}`; } catch (err) { $('#archive-preview').textContent = err.message; } }

window.addEventListener('hashchange', () => routeView(location.hash.slice(1) || 'home'));
$$('[data-work-route]').forEach(button => button.addEventListener('click', () => setHash(button.dataset.workRoute)));
$$('[data-public-route]').forEach(button => button.addEventListener('click', () => setHash(button.dataset.publicRoute)));
$('#work-home').addEventListener('click', () => setHash('home'));
$('#public-program-search').addEventListener('click', loadPublicPrograms);
$('#public-program-reset').addEventListener('click', () => { $('#public-program-q').value = ''; $('#public-agency').value = 'all'; loadPublicPrograms(); });
$('#program-search').addEventListener('click', loadProgramTable);
$('#notice-search').addEventListener('click', loadNoticeTable);
$('#analytics-form').addEventListener('submit', event => { event.preventDefault(); loadAnalytics(); });
$('#analytics-form').addEventListener('reset', () => setTimeout(loadAnalytics));
$('#archive-filter').addEventListener('input', renderArchive);
$('#qna-form').addEventListener('submit', async event => { event.preventDefault(); try { await api('/api/v1/qna', { method: 'POST', body: JSON.stringify({ subject: $('#qna-subject').value, message: $('#qna-message').value }) }); event.target.reset(); toast('연구수행문의가 등록되었습니다.'); loadQna(); } catch (err) { toast(err.message); } });
$('#contact-form').addEventListener('submit', async event => { event.preventDefault(); try { const data = await api('/api/v1/contact', { method: 'POST', body: JSON.stringify({ type: $('#contact-type').value, title: $('#contact-title').value, message: $('#contact-message').value }) }); $('#contact-result').textContent = `${data.ticket} 번호로 접수되었습니다.`; } catch (err) { $('#contact-result').textContent = err.message; } });
$('#export-mine').addEventListener('click', async () => { const data = await api('/api/v1/exports/research-data', { method: 'POST', body: JSON.stringify({ scope: 'mine', format: 'json' }) }); $('#export-output').textContent = JSON.stringify(data, null, 2); toast('내 연구데이터가 생성되었습니다.'); });
$('#open-search').addEventListener('click', () => { $('#global-search').hidden = false; $('#global-q').focus(); });
$('#global-close').addEventListener('click', () => $('#global-search').hidden = true);
$('#global-search-form').addEventListener('submit', async event => { event.preventDefault(); const data = await api(`/api/v1/search?q=${encodeURIComponent($('#global-q').value)}`); $('#global-results').innerHTML = data.items.map(item => `<article><small>${esc(item.type)}</small><b>${esc(item.title)}</b><span>${esc(item.id)}</span></article>`).join('') || '<article>검색 결과가 없습니다.</article>'; });

loadProfile().then(() => routeView(location.hash.slice(1) || 'home')).catch(err => toast(err.message));
