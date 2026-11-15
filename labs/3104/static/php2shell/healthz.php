<?php
header('Content-Type: application/json; charset=utf-8');
echo json_encode([
    'status' => 'ok',
    'mode' => 'inspection-archive',
    'runtime' => PHP_VERSION,
    'sapi' => PHP_SAPI,
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
