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

/* Deux façons d'atteindre Redis, selon ce que l'hébergeur fournit :
     - en HTTP, si la base expose une API REST (Upstash) ;
     - en TCP, si elle ne donne qu'une chaîne de connexion (REDIS_URL).
   Les commandes envoyées sont les mêmes, seul le transport change. */
var S = require('./_store.js');
var redis=S.redis, hasStore=S.hasStore, transport=S.transport, envNames=S.envNames;
var readBody=S.readBody, send=S.send;
var cleanId=S.cleanId, cleanTxt=S.cleanTxt, cleanNum=S.cleanNum, cleanKey=S.cleanKey;
var TTL=S.TTL, MAXLINKS=S.MAXLINKS;

/* Les répétitions de la semaine, exercice par exercice : au plus vingt
   entrées, des identifiants sobres, des nombres bornés. */
function cleanExo(o){
  if(!o || typeof o !== 'object') return {};
  var out = {}, n = 0;
  for(var k in o){
    if(n >= 20) break;
    if(!/^[a-z0-9]{1,24}$/.test(k)) continue;
    var v = cleanNum(o[k], 100000);
    if(v > 0){ out[k] = v; n++; }
  }
  return out;
}

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
    /* la semaine d'entraînement : elle sert au Crew (classement et défis).
       Le détail par exercice est borné, on ne recopie pas un catalogue. */
    sea:    cleanNum(o.sea, 200), ser: cleanNum(o.ser, 5000), rep: cleanNum(o.rep, 100000),
    exo:    cleanExo(o.exo),
    at:     cleanKey(o.at),
    ts:     cleanNum(o.ts, 4102444800000)   /* horodatage : départage deux fiches du même joueur */
  };
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


/* Vérification de bout en bout : on écrit une clé, on la relit, on l'efface.
   Répond franchement — présence des identifiants ET base réellement joignable. */
function doCheck(res){
  var vars = envNames();
  if(!hasStore()){
    return send(res, 200, { ok:true, version:1, store:false, redis:'absente',
      cause:'aucune_variable', variables: vars, transport:'aucun',
      message:'Aucune variable Redis dans ce déploiement. Relie la base au projet, puis redéploie.' });
  }
  var k = 'diag:' + Math.random().toString(36).slice(2, 10);
  return redis([['SET', k, 'ok', 'EX', 30], ['GET', k], ['DEL', k], ['DBSIZE']])
    .then(function(o){
      var relu = o[1], ok = (relu === 'ok');
      send(res, 200, { ok:true, version:1, store:true,
        redis: ok ? 'ok' : 'reponse_inattendue',
        transport: transport(), variables: vars,
        cles: (typeof o[3] === 'number') ? o[3] : null,
        message: ok ? 'Base joignable : ecriture, relecture et effacement reussis.'
                    : 'La base repond mais pas ce qu on a ecrit.' });
    })
    .catch(function(e){
      send(res, 200, { ok:true, version:1, store:true, redis:'injoignable',
        transport: transport(), variables: vars,
        detail: String(e && e.message || e).slice(0, 140),
        message:'Identifiants presents mais la base ne repond pas.' });
    });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }

  /* sert aussi de vérification d'installation, à ouvrir dans un navigateur.
     ?check=1 va plus loin : il teste vraiment la base. */
  if(req.method === 'GET'){
    if(/[?&]check=1/.test(req.url || '')) return doCheck(res);
    return send(res, 200, { ok: true, store: hasStore(), version: 1 });
  }
  if(req.method !== 'POST') return send(res, 405, { error: 'method' });
  if(!hasStore())           return send(res, 501, { error: 'no_store' });

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
