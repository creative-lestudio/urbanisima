// Comprueba que los datos legales obligatorios están rellenados en config.js antes de publicar.
//   npm run check:legal
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(readFileSync(new URL('../config.js', import.meta.url), 'utf8'), ctx);
const L = (ctx.window.URBANISIMA_CONFIG || {}).LEGAL || {};
const required = { CIF: 'NIF/CIF de la empresa', REGISTRO_MERCANTIL: 'Datos del Registro Mercantil', DOMICILIO: 'Domicilio', CODIGO_POSTAL: 'Código postal', MUNICIPIO: 'Municipio' };
let bad = 0;
for (const [k, label] of Object.entries(required)) if (!String(L[k] || '').trim()) { console.error(`✗ Falta ${label} (LEGAL.${k} en config.js)`); bad++; }
const php = readFileSync(new URL('../contact.php', import.meta.url), 'utf8');
const to = (php.match(/^\$TO\s*=\s*\[(.*?)\]/m) || [,''])[1];
if (/creative\.lestudio@gmail\.com/.test(to)) { console.error('✗ contact.php sigue enviando las solicitudes al correo de PRUEBAS (creative.lestudio@gmail.com). Cámbialo por el de la empresa antes de publicar.'); bad++; }
const wa = String((ctx.window.URBANISIMA_CONFIG || {}).WHATSAPP || '');
if (wa !== '34722115251') { console.error(`✗ config.js tiene un WhatsApp de PRUEBAS (${wa}). El del cliente es 34722115251. Cámbialo antes de publicar.`); bad++; }
const cp = String(L.CODIGO_POSTAL || '');
if (/valencia/i.test(L.MUNICIPIO || '') && cp && !cp.startsWith('46')) { console.warn(`⚠ El código postal ${cp} no parece de Valencia (empiezan por 46). Verifícalo con el cliente.`); bad++; }
if (bad) { console.error(`\n${bad} problema(s). Corrígelos antes de publicar.`); process.exit(1); }
console.log('✓ Datos legales completos.');
