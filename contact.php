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

$TO   = ['creative.lestudio@gmail.com']; // ⚠ SOLO PARA PRUEBAS. Antes de publicar, cambiar por ['info@grupo-urbanisima.com'] (npm run check:legal avisa si se olvida)
$FROM = 'web@grupo-urbanisima.com';

/* AUTOMATIZACIÓN (opcional): si rellenas estas dos líneas, cada solicitud también se envía a un webhook (n8n, Make, CRM...).
 * La clave nunca va en la web pública: solo vive en este archivo del servidor. Vacío = desactivado.
 * Cada envío lleva la cabecera X-Urbanisima-Signature: sha256=<HMAC del cuerpo con esta clave> para comprobar que viene de la web. */
$WEBHOOK_URL    = '';   // p. ej. https://n8n.tudominio.com/webhook/urbanisima-leads
$WEBHOOK_SECRET = '';   // una clave larga y aleatoria; la misma que se configura en n8n para verificar la firma

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

$isMultipart = stripos((string)($_SERVER['CONTENT_TYPE'] ?? ''), 'multipart/form-data') === 0;
if ($isMultipart) {                      // formulario con fotos: los datos van en el campo "data" (JSON) y las fotos en "fotos[]"
    $in = json_decode((string)($_POST['data'] ?? ''), true);
    if (!is_array($in)) out(400, ['ok' => false, 'error' => 'data']);
} else {
    $raw = file_get_contents('php://input');
    if ($raw === false || strlen($raw) > 20000) out(413, ['ok' => false, 'error' => 'size']);
    $in = json_decode($raw, true);
    if (!is_array($in)) $in = $_POST;
}

/* Trampa para bots: el campo "web" está oculto, una persona nunca lo rellena */
if (!empty($in['web'])) out(200, ['ok' => true]);

$nombre   = oneline($in['nombre'] ?? '', 80);
$telefono = oneline($in['telefono'] ?? '', 30);
$email    = oneline($in['email'] ?? '', 120);
$servicio = oneline($in['servicio'] ?? '', 120);
$perfil   = oneline($in['perfil'] ?? '', 60);
$localidad = oneline($in['localidad'] ?? '', 80);
$urgencia  = oneline($in['urgencia'] ?? '', 40);
$leadId    = 'UR-' . date('ymd') . '-' . strtoupper(bin2hex(random_bytes(3)));   // identificador único del lead
$estado    = 'Nuevo';                                                              // Nuevo > Contactado > Visita pendiente > Presupuesto enviado > Aceptado > Perdido
$mensaje  = clean($in['mensaje'] ?? '', 3000);
$canal    = ($in['canal'] ?? '') === 'email' ? 'email' : 'whatsapp';
$origen   = ($in['origen'] ?? '') === 'contacto' ? 'contacto' : 'presupuesto';   // 'presupuesto' = formulario único de 3 pasos
$pagina   = oneline($in['pagina'] ?? '', 300);
$acepta   = !empty($in['privacidad']);
$polVer   = oneline($in['politica_version'] ?? '', 20);

if (mb_strlen($nombre) < 2)                           out(422, ['ok' => false, 'error' => 'nombre']);
if (strlen((string)preg_replace('/\D/', '', $telefono)) < 9) out(422, ['ok' => false, 'error' => 'telefono']);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) out(422, ['ok' => false, 'error' => 'email']);
if ($origen === 'contacto' && mb_strlen($mensaje) < 10) out(422, ['ok' => false, 'error' => 'mensaje']);
if (!$acepta) out(422, ['ok' => false, 'error' => 'privacidad']);

/* Límite sencillo: 6 solicitudes cada 10 minutos por IP */
$ip   = $_SERVER['REMOTE_ADDR'] ?? '0';
$file = sys_get_temp_dir() . '/urb_rl_' . md5($ip);
$now  = time();
$hits = [];
if (is_file($file)) { $hits = array_filter(array_map('intval', explode(',', (string)@file_get_contents($file))), fn($t) => $now - $t < 600); }
if (count($hits) >= 6) out(429, ['ok' => false, 'error' => 'rate']);
$hits[] = $now;
@file_put_contents($file, implode(',', $hits));

/* ---------- Origen de la visita (solo existe si el visitante aceptó las cookies de publicidad) ---------- */
$A = [];
foreach (['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'landing', 'referrer'] as $k) {
    $v = oneline($in[$k] ?? '', 250);
    if ($v !== '') $A[$k] = $v;
}
$hasAds  = isset($A['gclid']) || isset($A['gbraid']) || isset($A['wbraid']) || (isset($A['utm_source']) && stripos($A['utm_source'], 'google') !== false);
$siteHost = preg_replace('/^www\./', '', (string)($_SERVER['HTTP_HOST'] ?? ''));
$refHost = !empty($A['referrer']) ? preg_replace('/^www\./', '', (string)parse_url($A['referrer'], PHP_URL_HOST)) : '';
$extRef  = ($refHost !== '' && $refHost !== $siteHost && stripos($refHost, 'grupo-urbanisima.com') === false) ? $refHost : '';
if ($hasAds)        $origenTxt = 'Anuncio de Google Ads';
elseif ($A)         $origenTxt = $extRef !== '' ? 'Visita desde ' . $extRef : 'Visita directa o búsqueda en Google';
else                $origenTxt = 'No disponible (el visitante no aceptó las cookies de publicidad)';

/* Pista automática de urgencia, para priorizar a quién llamar primero */
$urgente = stripos($urgencia, 'urgente') !== false || (bool)preg_match('/urgen|cuanto antes|lo antes posible|inmediat|inund|se cae|desprend|peligro|hoy mismo|ya mismo/iu', $mensaje);

/* ---------- Fotos adjuntas (opcionales): máx. 3, 5 MB cada una, solo JPG/PNG/WebP reales ---------- */
$adjuntos = [];
if ($isMultipart && !empty($_FILES['fotos']) && is_array($_FILES['fotos']['tmp_name'])) {
    $fi = function_exists('finfo_open') ? finfo_open(FILEINFO_MIME_TYPE) : null;
    $exts = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp'];
    foreach ($_FILES['fotos']['tmp_name'] as $i => $tmp) {
        if (count($adjuntos) >= 3) break;
        if (($_FILES['fotos']['error'][$i] ?? 1) !== UPLOAD_ERR_OK || !is_uploaded_file($tmp)) continue;
        if (($_FILES['fotos']['size'][$i] ?? 0) > 5 * 1024 * 1024) continue;
        $mime = $fi ? (string)finfo_file($fi, $tmp) : (string)(@getimagesize($tmp)['mime'] ?? '');
        if (!isset($exts[$mime]) || @getimagesize($tmp) === false) continue;
        $adjuntos[] = ['name' => 'foto-' . (count($adjuntos) + 1) . '.' . $exts[$mime], 'mime' => $mime, 'data' => (string)file_get_contents($tmp)];
    }
}
$nFotos = count($adjuntos);

/* Teléfono para WhatsApp (España por defecto) */
$digits = (string)preg_replace('/\D/', '', $telefono);
if (strpos($digits, '0034') === 0) $digits = substr($digits, 2);
if (strlen($digits) === 9) $digits = '34' . $digits;

$canalTxt = $canal === 'email' ? 'por correo' : 'por WhatsApp (copia)';
$asunto   = ($urgente ? '⚠ ' : '') . "[Web] Nueva solicitud de $nombre" . ($servicio !== '' ? " - $servicio" : '') . ' - ' . ($canal === 'email' ? 'correo' : 'WhatsApp');

/* ---------- Versión de texto (para clientes de correo sin HTML) ---------- */
$cuerpo  = "NUEVA SOLICITUD DESDE LA WEB" . ($urgente ? "  (⚠ menciona urgencia)" : '') . "\n";
$cuerpo .= str_repeat('=', 40) . "\n\n";
$cuerpo .= "Nombre:     $nombre\n";
$cuerpo .= "Teléfono:   $telefono\n";
$cuerpo .= 'Correo:     ' . ($email !== '' ? $email : '(no indicado)') . "\n";
$cuerpo .= 'Perfil:     ' . ($perfil !== '' ? $perfil : '(no indicado)') . "\n";
$cuerpo .= 'Servicio:   ' . ($servicio !== '' ? $servicio : '(no indicado)') . "\n";
$cuerpo .= 'Localidad:  ' . ($localidad !== '' ? $localidad : '(no indicada)') . "\n";
$cuerpo .= 'Urgencia:   ' . ($urgencia !== '' ? $urgencia : '(no indicada)') . "\n";
$cuerpo .= "Lead:       $leadId  (estado: $estado)\n";
$cuerpo .= 'Fotos:      ' . ($nFotos > 0 ? "$nFotos adjunta(s) a este correo" : 'ninguna') . "\n";
$cuerpo .= "Enviado:    $canalTxt\n\n";
$cuerpo .= "DESCRIPCIÓN DEL CLIENTE\n" . str_repeat('-', 40) . "\n";
$cuerpo .= ($mensaje !== '' ? $mensaje : '(sin descripción)') . "\n\n";
$cuerpo .= "ORIGEN DE LA VISITA\n" . str_repeat('-', 40) . "\n$origenTxt\n";
foreach (['utm_campaign' => 'Campaña', 'utm_term' => 'Palabra clave', 'gclid' => 'gclid'] as $k => $lab) if (isset($A[$k])) $cuerpo .= "$lab: {$A[$k]}\n";
$cuerpo .= "\n" . str_repeat('-', 40) . "\nPágina: $pagina\nFecha:  " . date('d/m/Y H:i:s') . "\n";
$cuerpo .= 'Consentimiento: política de privacidad aceptada' . ($polVer !== '' ? " (versión $polVer)" : '') . ".\n";
$cuerpo .= "Conservación: eliminar este mensaje a los 30 días del último contacto si no se contrata el servicio.\n";
if ($canal === 'whatsapp') $cuerpo .= "\nNota: el cliente ha abierto WhatsApp con este mismo mensaje.\n";

/* ---------- Versión HTML con la imagen de Urbanísima ---------- */
function hx(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
$logoPath = __DIR__ . '/assets/logo-blanco.png';
$logoB64  = is_file($logoPath) ? chunk_split(base64_encode((string)file_get_contents($logoPath))) : '';
$logoHtml = $logoB64 !== ''
    ? '<img src="cid:logo@grupo-urbanisima" width="190" alt="Grupo Urbanísima" style="display:block;border:0;outline:none;height:auto;max-width:190px">'
    : '<span style="font:800 20px Arial,Helvetica,sans-serif;color:#ffffff;letter-spacing:1px">GRUPO URBAN&Iacute;SIMA</span>';

$F  = "font-family:Montserrat,'Segoe UI',Arial,Helvetica,sans-serif;";   // títulos
$B  = "font-family:'Segoe UI',Arial,Helvetica,sans-serif;";               // texto
$btn = function (string $href, string $label, string $bg, string $fg, string $border = '') use ($F) {
    $bd = $border !== '' ? "border:2px solid $border;" : 'border:2px solid ' . $bg . ';';
    return '<a href="' . hx($href) . '" style="display:inline-block;margin:0 8px 8px 0;' . $bd . 'background:' . $bg . ';color:' . $fg . ';' . $F . 'font-weight:800;font-size:14px;line-height:20px;text-decoration:none;padding:9px 20px;border-radius:999px">' . hx($label) . '</a>';
};
$row = function (string $label, string $valueHtml) use ($B) {
    return '<tr><td style="padding:9px 0;border-bottom:1px solid #e6edf5;' . $B . 'font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#6b7a8a;width:132px;vertical-align:top">' . $label . '</td>'
         . '<td style="padding:9px 0;border-bottom:1px solid #e6edf5;' . $B . 'font-size:15px;color:#16202b;vertical-align:top">' . $valueHtml . '</td></tr>';
};
$pill = fn(string $t, string $bg, string $fg) => '<span style="display:inline-block;background:' . $bg . ';color:' . $fg . ';' . 'font-family:Arial,Helvetica,sans-serif;font-weight:700;font-size:11px;letter-spacing:.06em;text-transform:uppercase;padding:5px 11px;border-radius:999px;margin:0 6px 6px 0">' . $t . '</span>';

$badges  = $pill('Nueva solicitud', '#fff3c4', '#022440');
$badges .= $pill($canal === 'email' ? 'Enviada por correo' : 'Enviada por WhatsApp', '#e8f1fb', '#01477f');
if ($urgente) $badges .= $pill('⚠ Menciona urgencia', '#fde8e6', '#b3261e');

$btns = $btn('tel:+' . $digits, 'Llamar ahora', '#fec200', '#022440') . $btn('https://wa.me/' . $digits, 'WhatsApp', '#1fa855', '#ffffff');
if ($email !== '') $btns .= $btn('mailto:' . $email, 'Responder por correo', '#ffffff', '#01477f', '#01477f');

$datos  = $row('Nombre', hx($nombre));
$datos .= $row('Teléfono', '<a href="tel:+' . hx($digits) . '" style="color:#01477f;text-decoration:none;font-weight:700">' . hx($telefono) . '</a>');
$datos .= $row('Correo', $email !== '' ? '<a href="mailto:' . hx($email) . '" style="color:#01477f">' . hx($email) . '</a>' : '<span style="color:#8a97a5">No indicado</span>');
$datos .= $row('Soy', $perfil !== '' ? hx($perfil) : '<span style="color:#8a97a5">No indicado</span>');
$datos .= $row('Servicio', $servicio !== '' ? '<strong>' . hx($servicio) . '</strong>' : '<span style="color:#8a97a5">No indicado</span>');

$datos .= $row('Localidad', $localidad !== '' ? hx($localidad) : '<span style="color:#8a97a5">No indicada</span>');
$datos .= $row('Urgencia', $urgencia !== '' ? hx($urgencia) : '<span style="color:#8a97a5">No indicada</span>');
$datos .= $row('Fotos', $nFotos > 0 ? $nFotos . ' adjunta(s) a este correo' : '<span style="color:#8a97a5">Ninguna</span>');
$datos .= $row('Lead', '<span style="font-family:Consolas,Menlo,monospace;font-size:13px">' . hx($leadId) . '</span> &middot; ' . hx($estado));

$origenRows = $row('Origen', '<strong>' . hx($origenTxt) . '</strong>');
if (isset($A['utm_campaign'])) $origenRows .= $row('Campaña', hx($A['utm_campaign']));
if (isset($A['utm_term']))     $origenRows .= $row('Palabra clave', hx($A['utm_term']));
if (isset($A['gclid']))        $origenRows .= $row('gclid', '<span style="font-family:Consolas,Menlo,monospace;font-size:12px;color:#566473;word-break:break-all">' . hx(mb_substr($A['gclid'], 0, 60)) . '</span>');
$origenRows .= $row('Página', '<a href="' . hx($pagina) . '" style="color:#01477f;word-break:break-all">' . hx(mb_strlen($pagina) > 70 ? mb_substr($pagina, 0, 70) . '…' : $pagina) . '</a>');

$replyNote = $email !== ''
    ? 'Pulsa <strong>Responder</strong> en tu correo para contestar directamente al cliente.'
    : 'El cliente no indicó correo: llámale o escríbele por WhatsApp.';
$secTitle = fn(string $t) => '<tr><td style="padding:26px 28px 6px;background:#ffffff;' . $F . 'font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#01477f">' . $t . '</td></tr>';

$html = '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Nueva solicitud</title></head>'
  . '<body style="margin:0;padding:0;background:#eef3f8">'
  . '<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#eef3f8;font-size:1px;line-height:1px">' . hx($nombre) . ' pide presupuesto' . ($servicio !== '' ? ' · ' . hx($servicio) : '') . ' · ' . hx($telefono) . '</div>'
  . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef3f8"><tr><td align="center" style="padding:24px 12px">'
  . '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px">'
  /* cabecera */
  . '<tr><td style="background:#022440;border-radius:18px 18px 0 0;padding:24px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
  . '<td>' . $logoHtml . '</td></tr></table></td></tr>'
  . '<tr><td style="background:#fec200;height:5px;line-height:5px;font-size:0">&nbsp;</td></tr>'
  /* título */
  . '<tr><td style="background:#ffffff;padding:28px 28px 8px">' . $badges
  . '<h1 style="margin:10px 0 6px;' . $F . 'font-size:26px;line-height:1.2;font-weight:800;color:#022440">' . hx($nombre) . ' pide presupuesto</h1>'
  . '<p style="margin:0;' . $B . 'font-size:15px;color:#566473">' . ($servicio !== '' ? hx($servicio) : 'Servicio sin especificar') . ($perfil !== '' ? ' &middot; ' . hx($perfil) : '') . '</p></td></tr>'
  /* acciones */
  . '<tr><td style="background:#ffffff;padding:18px 28px 6px;line-height:1">' . $btns . '</td></tr>'
  /* descripción */
  . $secTitle('Lo que necesita')
  . '<tr><td style="background:#ffffff;padding:6px 28px 4px"><div style="background:#f2f6fb;border-left:4px solid #fec200;border-radius:0 12px 12px 0;padding:16px 18px;' . $B . 'font-size:16px;line-height:1.6;color:#16202b">'
  . ($mensaje !== '' ? nl2br(hx($mensaje), false) : '<span style="color:#8a97a5">Sin descripción</span>') . '</div></td></tr>'
  /* datos */
  . $secTitle('Datos de contacto')
  . '<tr><td style="background:#ffffff;padding:0 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">' . $datos . '</table></td></tr>'
  /* origen */
  . $secTitle('Cómo llegó')
  . '<tr><td style="background:#ffffff;padding:0 28px 8px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">' . $origenRows . '</table></td></tr>'
  . '<tr><td style="background:#ffffff;padding:14px 28px 28px;' . $B . 'font-size:13px;line-height:1.5;color:#566473">' . $replyNote . '</td></tr>'
  /* pie */
  . '<tr><td style="background:#022440;border-radius:0 0 18px 18px;padding:20px 28px;' . $B . 'font-size:12px;line-height:1.6;color:#b4c3d3">'
  . 'Recibida el ' . date('d/m/Y \a \l\a\s H:i') . ' desde grupo-urbanisima.com.<br>'
  . 'Consentimiento: política de privacidad aceptada' . ($polVer !== '' ? ' (versión ' . hx($polVer) . ')' : '') . '. '
  . 'Conservación: eliminar este mensaje a los 30 días del último contacto si no se contrata el servicio.<br>'
  . '<span style="color:#7f93a8">Correo automático &middot; Web desarrollada por LE STUDIO</span></td></tr>'
  . '</table></td></tr></table></body></html>';

/* ---------- Montaje MIME: texto + HTML + logo incrustado ---------- */
$bRel = '=_rel_' . md5(uniqid('', true));
$bAlt = '=_alt_' . md5(uniqid('', true));
$cuerpoMime  = "--$bRel\r\nContent-Type: multipart/alternative; boundary=\"$bAlt\"\r\n\r\n";
$cuerpoMime .= "--$bAlt\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($cuerpo)) . "\r\n";
$cuerpoMime .= "--$bAlt\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html)) . "\r\n";
$cuerpoMime .= "--$bAlt--\r\n";
if ($logoB64 !== '') $cuerpoMime .= "--$bRel\r\nContent-Type: image/png; name=\"logo.png\"\r\nContent-Transfer-Encoding: base64\r\nContent-ID: <logo@grupo-urbanisima>\r\nContent-Disposition: inline; filename=\"logo.png\"\r\n\r\n" . $logoB64 . "\r\n";
$cuerpoMime .= "--$bRel--\r\n";
$tipoCab = "multipart/related; boundary=\"$bRel\"; type=\"multipart/alternative\"";
if ($adjuntos) {   // el cuerpo anterior se envuelve en multipart/mixed junto a las fotos
    $bMix = '=_mix_' . md5(uniqid('', true));
    $mix = "--$bMix\r\nContent-Type: $tipoCab\r\n\r\n" . $cuerpoMime . "\r\n";
    foreach ($adjuntos as $a) {
        $mix .= "--$bMix\r\nContent-Type: {$a['mime']}; name=\"{$a['name']}\"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename=\"{$a['name']}\"\r\n\r\n" . chunk_split(base64_encode($a['data'])) . "\r\n";
    }
    $cuerpoMime = $mix . "--$bMix--\r\n";
    $tipoCab = "multipart/mixed; boundary=\"$bMix\"";
}

$h  = "From: Web Grupo Urbanísima <$FROM>\r\n";
if ($email !== '') $h .= "Reply-To: $nombre <$email>\r\n";
$h .= "MIME-Version: 1.0\r\nContent-Type: $tipoCab\r\n";

$subjectEnc = mb_encode_mimeheader($asunto, 'UTF-8', 'B', "\r\n");
$ok = false;
foreach ($TO as $dest) {
    $r = @mail($dest, $subjectEnc, $cuerpoMime, $h, '-f' . $FROM);
    if (!$r) $r = @mail($dest, $subjectEnc, $cuerpoMime, $h);
    $ok = $ok || $r;
}

if (!$ok) { error_log('contact.php: mail() falló para ' . $nombre); out(500, ['ok' => false, 'error' => 'mail']); }
/* ---------- Webhook opcional (CRM / n8n). Un fallo aquí nunca impide que la solicitud llegue por correo ---------- */
if ($WEBHOOK_URL !== '' && function_exists('curl_init')) {
    $evento = json_encode([
        'lead_id' => $leadId, 'fecha' => date('c'), 'estado' => $estado,
        'canal' => $canal, 'formulario' => $origen, 'origen_captacion' => $origenTxt,
        'pagina_entrada' => $A['landing'] ?? $pagina, 'pagina_envio' => $pagina,
        'servicio' => $servicio, 'tipo_cliente' => $perfil, 'localidad' => $localidad, 'urgencia' => $urgencia, 'urgente' => $urgente,
        'nombre' => $nombre, 'telefono' => $telefono, 'email' => $email, 'mensaje' => $mensaje,
        'fotos_adjuntas' => $nFotos, 'utm' => array_intersect_key($A, array_flip(['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid'])),
        'politica_version' => $polVer,
    ], JSON_UNESCAPED_UNICODE);
    $ch = curl_init($WEBHOOK_URL);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $evento, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 4, CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-Urbanisima-Signature: sha256=' . hash_hmac('sha256', (string)$evento, $WEBHOOK_SECRET)]]);
    $res = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    if ($res === false || $code >= 300) error_log("contact.php: webhook falló ($code) para $leadId");
}

out(200, ['ok' => true, 'lead_id' => $leadId]);
