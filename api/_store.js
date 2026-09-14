/* ============================================================================
   Couche commune aux fonctions de l'API : accès à Redis, lecture du corps des
   requêtes, réponses JSON, nettoyage des entrées. Le préfixe « _ » empêche
   l'hébergeur d'en faire une route publique.
   ========================================================================== */

var RURL   = process.env.KV_REST_API_URL   || process.env.UPSTASH_REDIS_REST_URL   || '';
var RTOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || '';
var TCPURL = process.env.REDIS_URL || process.env.KV_URL || '';

function hasStore(){ return !!((RURL && RTOKEN) || TCPURL); }
function transport(){ return (RURL && RTOKEN) ? 'rest' : (TCPURL ? 'tcp' : 'aucun'); }

var TTL      = 60 * 60 * 24 * 90;   /* 90 jours */
var MAXLINKS = 60;                  /* garde-fou : taille max d'un classement */

/* ------------------------------------------------------------------ Redis */
function redisRest(cmds){
  return fetch(RURL.replace(/\/+$/,'') + '/pipeline', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + RTOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds)
  }).then(function(r){
    if(!r.ok) throw new Error('redis ' + r.status);
    return r.json();
  }).then(function(out){
    return (out || []).map(function(x){ return x && x.result; });
  });
}

/* Connexion TCP réutilisée entre deux appels de la fonction : ouvrir un socket
   par requête coûterait un aller-retour TLS à chaque fois. */
var _tcp = null;
function tcpClient(){
  if(_tcp) return _tcp;
  var Redis = require('ioredis');
  _tcp = new Redis(TCPURL, {
    connectTimeout: 8000,
    maxRetriesPerRequest: 2,
    enableReadyCheck: true
  });
  _tcp.on('error', function(){});   /* sans écouteur, une coupure ferait tomber la fonction */
  return _tcp;
}
function redisTcp(cmds){
  /* le client TCP n'accepte que des noms de commande en minuscules,
     alors que l'API REST tolère les deux : on normalise ici. */
  var norm = (cmds || []).map(function(c){
    var out = c.slice(); out[0] = String(out[0]).toLowerCase(); return out;
  });
  return Promise.resolve().then(function(){
    return tcpClient().pipeline(norm).exec();
  }).then(function(rows){
    (rows || []).forEach(function(r){ if(r && r[0]) throw r[0]; });
    return (rows || []).map(function(r){ return r && r[1]; });
  });
}

function redis(cmds){
  if(RURL && RTOKEN) return redisRest(cmds);
  if(TCPURL)         return redisTcp(cmds);
  return Promise.reject(new Error('aucune base'));
}

var ID_RE = /^[A-Za-z0-9_-]{4,40}$/;
function cleanId(v){ v = String(v == null ? '' : v); return ID_RE.test(v) ? v : ''; }
function cleanTxt(v, max){ return String(v == null ? '' : v).slice(0, max); }
function cleanNum(v, max){ var n = Math.round(Number(v)); return isFinite(n) && n >= 0 && n <= max ? n : 0; }
function cleanKey(v){ return /^[0-9]{4}-[0-9]{2}(-[0-9]{2})?$/.test(String(v)) ? String(v) : ''; }

/* ------------------------------------------------------------------ corps */
function readBody(req){
  if(req.body && typeof req.body === 'object') return Promise.resolve(req.body);
  if(typeof req.body === 'string'){
    try{ return Promise.resolve(JSON.parse(req.body)); }catch(e){ return Promise.resolve({}); }
  }
  return new Promise(function(resolve){
    var raw = '', over = false;
    req.on('data', function(c){
      raw += c;
      if(raw.length > 16384){ over = true; req.destroy(); }   /* corps déraisonnable */
    });
    req.on('end', function(){
      if(over) return resolve({});
      try{ resolve(JSON.parse(raw || '{}')); }catch(e){ resolve({}); }
    });
    req.on('error', function(){ resolve({}); });
  });
}

function send(res, code, obj){
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(obj));
}


/* Quelles variables liées à Redis ce déploiement voit-il ?
   On ne renvoie que les NOMS : une valeur est un secret, un nom ne l'est pas. */
function envNames(){
  return Object.keys(process.env)
    .filter(function(k){ return /^(KV_|UPSTASH_|REDIS_)/.test(k); })
    .filter(function(k){ return String(process.env[k] || '').length > 0; })
    .sort();
}

module.exports = {
  redis: redis, hasStore: hasStore, transport: transport, envNames: envNames,
  readBody: readBody, send: send,
  cleanId: cleanId, cleanTxt: cleanTxt, cleanNum: cleanNum, cleanKey: cleanKey,
  TTL: TTL, MAXLINKS: MAXLINKS
};
