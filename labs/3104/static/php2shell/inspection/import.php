<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    echo json_encode(['error' => 'POST 요청만 허용합니다.'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (!str_starts_with(strtolower($_SERVER['CONTENT_TYPE'] ?? ''), 'multipart/form-data')) {
    http_response_code(415);
    echo json_encode(['error' => 'multipart/form-data 요청이 필요합니다.'], JSON_UNESCAPED_UNICODE);
    exit;
}

function leaf_count(mixed $value): int {
    if (!is_array($value)) {
        return 1;
    }
    $count = 0;
    foreach ($value as $child) {
        $count += leaf_count($child);
    }
    return $count;
}

$progress = (string)($_POST['PHP_SESSION_UPLOAD_PROGRESS'] ?? '');
$transferEncoding = strtolower((string)(
    $_SERVER['HTTP_TRANSFER_ENCODING']
    ?? $_SERVER['TRANSFER_ENCODING']
    ?? ''
));
$chunkedMultipart = str_contains($transferEncoding, 'chunked');
$fileCount = 0;
foreach ($_FILES as $file) {
    if (is_array($file) && array_key_exists('error', $file)) {
        $fileCount += leaf_count($file['error']);
    }
}

$sessionId = preg_replace('/[^A-Za-z0-9,-]/', '', (string)($_COOKIE['PHPSESSID'] ?? 'anonymous')) ?: 'anonymous';
$stateFile = '/tmp/php2shell-state-' . hash('sha256', $sessionId);

// Safe, deterministic emulation of the two-request mod_php PHP2Shell primitive.
// No arbitrary command execution occurs. The first request can use either the
// nested-file shape or the chunked multipart/header-heavy shape documented by
// public research. The lab scales both down before memory exhaustion and arms a
// short-lived stale-state marker; a following upload-progress request consumes it.
if ($progress !== '' && ($fileCount >= 12 || ($chunkedMultipart && $fileCount >= 1))) {
    file_put_contents($stateFile, (string)time(), LOCK_EX);
    header('X-PHP2Shell-Lab-Stage: stale-state-armed');
    http_response_code(500);
    echo json_encode([
        'error' => 'Allowed memory size of 134217728 bytes exhausted',
        'phase' => 'request-startup cleanup',
        'worker' => 'apache2handler',
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

if ($progress !== '' && $fileCount === 0 && is_file($stateFile)) {
    $armedAt = (int)trim((string)file_get_contents($stateFile));
    @unlink($stateFile);
    if ($armedAt > 0 && time() - $armedAt <= 90) {
        header('X-PHP2Shell-Lab-Stage: stale-state-consumed');
        echo json_encode([
            'status' => 'simulated-rce-confirmed',
            'runtime' => 'PHP/' . PHP_VERSION,
            'sapi' => PHP_SAPI,
            'command' => 'id',
            'stdout' => 'uid=33(www-data) gid=33(www-data) groups=33(www-data)',
            'evidence' => 'PHP2SHELL-EVIDENCE-CUSTOMS-2026',
            'safety' => 'No arbitrary command was executed. This is a command-output emulator.',
        ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }
}

echo json_encode([
    'status' => 'validated',
    'message' => '검사자료 구조 검증을 완료했습니다.',
    'received_files' => $fileCount,
    'case_id' => (string)($_POST['case_id'] ?? ''),
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
