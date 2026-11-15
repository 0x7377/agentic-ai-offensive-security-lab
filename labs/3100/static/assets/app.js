async function loadSummary(){
  const statusTarget=document.querySelector('[data-live-status]');
  const noticeTarget=document.querySelector('[data-notices]');
  try{
    const [status,notices]=await Promise.all([
      fetch('/api/v1/status').then(r=>r.json()),
      fetch('/api/v1/notices?limit=3').then(r=>r.json())
    ]);
    if(statusTarget) statusTarget.textContent=status.overall==='operational'?'전체 서비스 정상':'일부 서비스 점검';
    if(noticeTarget) noticeTarget.innerHTML=notices.items.map(n=>`<article class="notice"><span>${n.category}</span><b>${n.title}</b><time>${n.date}</time></article>`).join('');
  }catch(error){
    if(statusTarget) statusTarget.textContent='상태 확인 지연';
  }
}
loadSummary();
