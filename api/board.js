/* ============================================================================
   Cadence — classement partagé.
   Une seule route, trois actions. Aucune dépendance : on parle à Redis par son
   API REST. Les identifiants sont injectés par Vercel quand une base Redis est
   attachée au projet (Storage → Redis) ; sans base, la route répond 501 et
   l'app retombe proprement sur l'échange de codes à la main.

   Ce qui est stocké, et rien d'autre :
     p:<id>     le joueur { id, blaze, avatar, points jour/semaine/mois, XP }
     link:<id>  l'ensemble des joueurs reliés à celui-ci
   Les deux expirent au bout de 90 jours sans activité.
   ========================================================================== */

var RURL   = process.env.KV_REST_API_URL   || process.env.UPSTASH_REDIS_REST_URL   || '';
var RTOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || '';

var TTL      = 60 * 60 * 24 * 90;   /* 90 jours */
var MAXLINKS = 60;                  /* garde-fou : taille max d'un classement */

/* ------------------------------------------------------------------ Redis */
function redis(cmds){
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

/* ------------------------------------------------------- nettoyage entrées */
var ID_RE = /^[A-Za-z0-9_-]{4,40}$/;
function cleanId(v){ v = String(v == null ? '' : v); return ID_RE.test(v) ? v : ''; }
function cleanTxt(v, max){ return String(v == null ? '' : v).slice(0, max); }
function cleanNum(v, max){ var n = Math.round(Number(v)); return isFinite(n) && n >= 0 && n <= max ? n : 0; }
function cleanKey(v){ return /^[0-9]{4}-[0-9]{2}(-[0-9]{2})?$/.test(String(v)) ? String(v) : ''; }

/* on ne fait jamais confiance à ce que le client envoie */
function cleanPlayer(o){
  if(!o || typeof o !== 'object') return null;
  var id = cleanId(o.id);
  if(!id) return null;
  return {
    id: id,
    name:   cleanTxt(o.name, 20) || 'Anonyme',
    avatar: cleanTxt(o.avatar, 8) || '💪',
    day:    cleanNum(o.day,   1000000), dayK:   cleanKey(o.dayK),   dayP:   cleanNum(o.dayP,   100),
    week:   cleanNum(o.week,  1000000), weekK:  cleanKey(o.weekK),  weekP:  cleanNum(o.weekP,  100),
    month:  cleanNum(o.month, 1000000), monthK: cleanKey(o.monthK), monthP: cleanNum(o.monthP, 100),
    xp:     cleanNum(o.xp,   10000000),
    at:     cleanKey(o.at),
    ts:     cleanNum(o.ts, 4102444800000)   /* horodatage : départage deux fiches du même joueur */
  };
}

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

/* --------------------------------------------------------------- actions */

/* Les points de chacun sont écrits par lui-même ; on rend ceux de ses reliés. */
function doSync(res, body){
  var me = cleanPlayer(body.me);
  if(!me) return send(res, 400, { error: 'bad_player' });

  /* retraits demandés hors ligne, rejoués ici */
  var drop = (Array.isArray(body.drop) ? body.drop : []).map(cleanId).filter(Boolean).slice(0, 20);

  var cmds = [
    ['SET', 'p:' + me.id, JSON.stringify(me), 'EX', TTL],
    ['EXPIRE', 'link:' + me.id, TTL]
  ];
  drop.forEach(function(id){ cmds.push(['SREM', 'link:' + me.id, id]); });
  cmds.push(['SMEMBERS', 'link:' + me.id]);

  return redis(cmds).then(function(out){
    var ids = (out[out.length - 1] || []).filter(function(x){ return cleanId(x); }).slice(0, MAXLINKS);
    if(!ids.length) return send(res, 200, { ok: true, friends: [], dropped: drop });
    return redis([['MGET'].concat(ids.map(function(i){ return 'p:' + i; }))]).then(function(r){
      var friends = (r[0] || []).map(function(v){
        if(!v) return null;
        try{ return cleanPlayer(typeof v === 'string' ? JSON.parse(v) : v); }catch(e){ return null; }
      }).filter(Boolean);
      send(res, 200, { ok: true, friends: friends, dropped: drop });
    });
  });
}

/* B colle le code de A : on relie les deux sens d'un coup, c'est ce qui fait
   que A verra B apparaître sans avoir rien collé de son côté. */
function doLink(res, body){
  var me = cleanId(body.me), target = cleanId(body.target);
  if(!me || !target) return send(res, 400, { error: 'bad_id' });
  if(me === target)  return send(res, 400, { error: 'self' });
  return redis([
    ['SADD', 'link:' + target, me],
    ['SADD', 'link:' + me, target],
    ['EXPIRE', 'link:' + target, TTL],
    ['EXPIRE', 'link:' + me, TTL]
  ]).then(function(){ send(res, 200, { ok: true }); });
}

/* Un retrait n'agit que sur son propre classement. */
function doUnlink(res, body){
  var me = cleanId(body.me), target = cleanId(body.target);
  if(!me || !target) return send(res, 400, { error: 'bad_id' });
  return redis([['SREM', 'link:' + me, target]])
    .then(function(){ send(res, 200, { ok: true }); });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }

  /* sert aussi de vérification d'installation, à ouvrir dans un navigateur */
  if(req.method === 'GET'){
    return send(res, 200, { ok: true, store: !!(RURL && RTOKEN), version: 1 });
  }
  if(req.method !== 'POST') return send(res, 405, { error: 'method' });
  if(!RURL || !RTOKEN)      return send(res, 501, { error: 'no_store' });

  return readBody(req).then(function(body){
    var a = body && body.action;
    if(a === 'sync')   return doSync(res, body);
    if(a === 'link')   return doLink(res, body);
    if(a === 'unlink') return doUnlink(res, body);
    return send(res, 400, { error: 'bad_action' });
  }).catch(function(e){
    send(res, 502, { error: 'store_unreachable', detail: String(e && e.message || e).slice(0, 120) });
  });
};
