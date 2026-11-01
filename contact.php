<?php
/*
 * Recibe las solicitudes de la web y las envía por correo a la empresa.
 * Se usa tanto para "Enviar por correo" como para la copia que se manda cuando el cliente elige WhatsApp.
 *
 * CONFIGURACIÓN (solo estas dos líneas):
 *   $TO   → correos que reciben las solicitudes.
 *   $FROM → remitente. Debe ser un buzón o alias del propio dominio (SiteGround > Correo) para que no caiga en spam.
 */
declare(strict_types=1);

$TO   = ['info@grupo-urbanisima.com'];
$FROM = 'web@grupo-urbanisima.com';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function out(int $code, array $data): void { http_response_code($code); echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }
function clean($v, int $max): string {
    $v = is_string($v) ? $v : '';
    $v = str_replace(["\0", "\r"], '', $v);
    return mb_substr(trim($v), 0, $max);
}
function oneline($v, int $max): string { return trim((string)preg_replace('/\s+/u', ' ', clean($v, $max))); }

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, ['ok' => false, 'error' => 'method']);

$raw = file_get_contents('php://input');
if ($raw === false || strlen($raw) > 20000) out(413, ['ok' => false, 'error' => 'size']);
$in = json_decode($raw, true);
if (!is_array($in)) $in = $_POST;

/* Trampa para bots: el campo "web" está oculto, una persona nunca lo rellena */
if (!empty($in['web'])) out(200, ['ok' => true]);

$nombre   = oneline($in['nombre'] ?? '', 80);
$telefono = oneline($in['telefono'] ?? '', 30);
$email    = oneline($in['email'] ?? '', 120);
$servicio = oneline($in['servicio'] ?? '', 120);
$perfil   = oneline($in['perfil'] ?? '', 60);
$mensaje  = clean($in['mensaje'] ?? '', 3000);
$canal    = ($in['canal'] ?? '') === 'email' ? 'email' : 'whatsapp';
$origen   = ($in['origen'] ?? '') === 'hero' ? 'hero' : 'contacto';
$pagina   = oneline($in['pagina'] ?? '', 300);

if (mb_strlen($nombre) < 2)                           out(422, ['ok' => false, 'error' => 'nombre']);
if (strlen((string)preg_replace('/\D/', '', $telefono)) < 9) out(422, ['ok' => false, 'error' => 'telefono']);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) out(422, ['ok' => false, 'error' => 'email']);
if ($origen === 'contacto' && mb_strlen($mensaje) < 10) out(422, ['ok' => false, 'error' => 'mensaje']);

/* Límite sencillo: 6 solicitudes cada 10 minutos por IP */
$ip   = $_SERVER['REMOTE_ADDR'] ?? '0';
$file = sys_get_temp_dir() . '/urb_rl_' . md5($ip);
$now  = time();
$hits = [];
if (is_file($file)) { $hits = array_filter(array_map('intval', explode(',', (string)@file_get_contents($file))), fn($t) => $now - $t < 600); }
if (count($hits) >= 6) out(429, ['ok' => false, 'error' => 'rate']);
$hits[] = $now;
@file_put_contents($file, implode(',', $hits));

/* Atribución de Google Ads: qué anuncio trajo a esta persona */
$attrib = '';
foreach (['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'landing', 'referrer'] as $k) {
    $v = oneline($in[$k] ?? '', 250);
    if ($v !== '') $attrib .= str_pad($k, 14) . ': ' . $v . "\n";
}

$canalTxt = $canal === 'email' ? 'por correo' : 'por WhatsApp (copia)';
$asunto   = "[Web] Nueva solicitud de $nombre" . ($servicio !== '' ? " - $servicio" : '') . ' - ' . ($canal === 'email' ? 'correo' : 'WhatsApp');

$cuerpo  = "NUEVA SOLICITUD DESDE LA WEB\n";
$cuerpo .= str_repeat('=', 40) . "\n\n";
$cuerpo .= "Nombre:     $nombre\n";
$cuerpo .= "Teléfono:   $telefono\n";
$cuerpo .= 'Correo:     ' . ($email !== '' ? $email : '(no indicado)') . "\n";
$cuerpo .= 'Perfil:     ' . ($perfil !== '' ? $perfil : '(no indicado)') . "\n";
$cuerpo .= 'Servicio:   ' . ($servicio !== '' ? $servicio : '(no indicado)') . "\n";
$cuerpo .= "Enviado:    $canalTxt (formulario: $origen)\n\n";
$cuerpo .= "DESCRIPCIÓN DEL CLIENTE\n" . str_repeat('-', 40) . "\n";
$cuerpo .= ($mensaje !== '' ? $mensaje : '(sin descripción)') . "\n\n";
if ($attrib !== '') $cuerpo .= "ORIGEN DE LA VISITA (Google Ads)\n" . str_repeat('-', 40) . "\n" . $attrib . "\n";
$cuerpo .= str_repeat('-', 40) . "\nPágina: $pagina\nFecha:  " . date('d/m/Y H:i:s') . "\nIP:     $ip\n";
if ($canal === 'whatsapp') $cuerpo .= "\nNota: el cliente ha abierto WhatsApp con este mismo mensaje; también puede escribir al " . '+34 722 115 251' . ".\n";

$h  = "From: Web Grupo Urbanísima <$FROM>\r\n";
if ($email !== '') $h .= "Reply-To: $nombre <$email>\r\n";
$h .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";

$subjectEnc = mb_encode_mimeheader($asunto, 'UTF-8', 'B', "\r\n");
$ok = false;
foreach ($TO as $dest) {
    $r = @mail($dest, $subjectEnc, $cuerpo, $h, '-f' . $FROM);
    if (!$r) $r = @mail($dest, $subjectEnc, $cuerpo, $h);
    $ok = $ok || $r;
}

if (!$ok) { error_log('contact.php: mail() falló para ' . $nombre); out(500, ['ok' => false, 'error' => 'mail']); }
out(200, ['ok' => true]);
