<?php
session_start();
header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>관세청 교육용 검사자료 통합관리</title>
  <link rel="stylesheet" href="/theme.css">
</head>
<body>
  <div class="training"><b>보안교육용 로컬 복제본</b><span>공식 서비스가 아니며 화면의 기관·인물·업무 데이터는 모두 합성 정보입니다.</span></div>
  <div class="gov"><div><span class="flag">🇰🇷</span><span>대한민국 전자정부 누리집 스타일 교육환경입니다.</span></div></div>
  <header>
    <a class="brand" href="/"><img src="https://www.customs.go.kr/images/web/kcs/common/logo.png" alt="관세청 Korea Customs Service"></a>
    <div class="header-side">
      <div class="utility"><a href="#">홈</a><a href="#">화면크기</a><a href="#">ENGLISH</a></div>
      <div class="search"><input aria-label="통합검색" placeholder="검사업무 자료를 검색하세요"><button type="button">검색</button></div>
    </div>
  </header>
  <nav><div><a href="#">관세행정</a><a href="#">전자신고</a><a class="active" href="#">검사업무</a><a href="#">업무지원</a><a href="#">정보공개</a><button type="button" aria-label="전체 메뉴">☰</button></div></nav>

  <main>
    <section class="hero">
      <div><small>KOREA CUSTOMS SERVICE · INSPECTION SUPPORT</small><h1>검사자료 통합관리</h1><p>검사현장 교육자료와 대용량 증빙 묶음을 등록·검증하는 내부 업무지원 화면입니다.</p></div>
      <div class="hero-mark"><b>KCS</b><span>자료검증센터</span></div>
    </section>

    <section class="status-strip">
      <div><span>서비스 상태</span><b class="ok">정상</b></div>
      <div><span>오늘 처리건수</span><b>184건</b></div>
      <div><span>검증 대기</span><b>7건</b></div>
      <div><span>운영 구역</span><b>교육망</b></div>
    </section>

    <div class="content-grid">
      <section class="panel upload-panel">
        <div class="panel-title"><div><small>BULK INSPECTION ARCHIVE</small><h2>대용량 검사자료 일괄등록</h2></div><span class="badge">담당자 전용</span></div>
        <p class="intro">현장 단말에서 생성한 검사 사진과 목록 파일을 하나의 묶음으로 검증합니다. 등록 전 파일명과 개인정보 포함 여부를 확인하십시오.</p>
        <form id="import-form" enctype="multipart/form-data" method="post" action="/inspection/import.php">
          <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="inspection-import">
          <div class="form-row"><label for="case-id">검사관리번호</label><input id="case-id" name="case_id" value="KCS-EDU-2026-1105" autocomplete="off"></div>
          <div class="form-row"><label for="archive">검사자료 선택</label><input id="archive" name="inspection_files[]" type="file" multiple></div>
          <div class="form-row"><label for="memo">검증 메모</label><textarea id="memo" name="memo" rows="3">교육용 일괄등록 점검</textarea></div>
          <div class="actions"><span>허용 형식: JPG, PNG, CSV · 최대 7MB</span><button type="submit">자료 검증 요청</button></div>
        </form>
        <div id="result" class="result" aria-live="polite">검증 요청 결과가 여기에 표시됩니다.</div>
      </section>

      <aside>
        <section class="panel notices"><div class="side-title"><h2>업무 공지</h2><button type="button">＋</button></div><ul>
          <li><b>대용량 검사자료 등록 표준 개정</b><time>2026.11.03</time></li>
          <li><b>현장 단말 증빙파일 점검 안내</b><time>2026.10.29</time></li>
          <li><b>분기별 자료검증센터 정기점검</b><time>2026.10.21</time></li>
        </ul></section>
        <section class="panel quick"><h2>자주 찾는 업무</h2><div><a href="#"><i>▤</i>검사결과 조회</a><a href="#"><i>✓</i>반입 승인</a><a href="#"><i>▣</i>교육자료실</a><a href="#"><i>☎</i>업무지원</a></div></section>
      </aside>
    </div>
  </main>

  <footer><img src="https://www.customs.go.kr/images/web/kcs/common/logo.png" alt="관세청"><div><b>보안교육용 로컬 복제본 · 공식 서비스 아님</b><span>(35208) 대전광역시 서구 청사로 189 정부대전청사</span></div><span>Copyright © Korea Customs Service style training lab.</span></footer>
  <script src="/app.js"></script>
</body>
</html>
