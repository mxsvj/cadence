/* ============================================================================
   Focus : la liste de tâches et l'état d'une séance de concentration.

   Deux lecteurs, et c'est tout le montage :

   1. L'app Focus (focus/index.html), qui lit et écrit l'état complet : la
      liste, le focus en cours, l'historique.
   2. L'automatisation Raccourcis de l'iPhone. À chaque ouverture d'une app
      qui distrait, elle demande GET /api/focus?k=<clé> et reçoit un seul mot,
      « bloque » ou « libre ». Un mot plutôt que du JSON : dans Raccourcis, la
      condition « Contenu de l'URL contient bloque » se règle en deux touches,
      un booléen JSON beaucoup moins.

   Pas de compte : la clé, tirée au hasard par l'app, sert d'identité. Elle ne
   protège qu'une liste de tâches. Quelqu'un qui la connaît peut lire la liste
   ou lancer un focus, rien de plus.

   Dans le doute, on laisse passer. Sans base, avec une clé inconnue, sur une
   erreur, ou pour un focus oublié depuis plus de douze heures, la réponse est
   « libre ». Un garde-fou qui enferme quelqu'un à cause d'une panne serait
   pire que pas de garde-fou du tout.
   ========================================================================== */

var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;

var TTL        = 60 * 60 * 24 * 90;        /* 90 jours sans y toucher et tout s'efface */
var MAX_FOCUS  = 12 * 60 * 60 * 1000;      /* au-delà, un focus oublié ne bloque plus rien */
var MAX_TACHES = 40;
var MAX_HIST   = 60;
var JOUR       = 24 * 60 * 60 * 1000;

var CLE_RE = /^[a-z0-9]{8,24}$/;
function cleOf(v){ v = String(v == null ? '' : v); return CLE_RE.test(v) ? v : ''; }

/* Bloquer veut dire : un focus lancé, de moins de douze heures, et au moins une
   tâche pas encore faite. Une liste entièrement cochée ne retient personne,
   même si l'app n'a pas encore eu le temps de clore le focus. */
function bloque(e, now){
  if(!e || !e.actif || !e.debut) return false;
  if(now - e.debut >= MAX_FOCUS) return false;
  return (e.taches || []).some(function(t){ return !t.ok; });
}

/* Ce qui entre est remis en forme ici. Le serveur ne fait confiance qu'à la
   forme, pas au contenu : une liste reste une liste de textes courts. */
function propre(e, now){
  e = e && typeof e === 'object' ? e : {};
  var taches = (Array.isArray(e.taches) ? e.taches : []).slice(0, MAX_TACHES).map(function(t){
    t = t && typeof t === 'object' ? t : {};
    return { id: /^[a-z0-9]{1,16}$/.test(String(t.id)) ? String(t.id) : '',
             t:  S.cleanTxt(t.t, 140).trim(),
             ok: !!t.ok };
  }).filter(function(t){ return t.id && t.t; });

  var hist = (Array.isArray(e.hist) ? e.hist : []).slice(-MAX_HIST).map(function(h){
    h = h && typeof h === 'object' ? h : {};
    return { d: S.cleanNum(h.d, now + JOUR), f: S.cleanNum(h.f, now + JOUR),
             n: S.cleanNum(h.n, 99), tenu: !!h.tenu };
  }).filter(function(h){ return h.d && h.f >= h.d; });

  var debut = S.cleanNum(e.debut, now + JOUR);
  var actif = !!e.actif && !!debut;
  return { maj: S.cleanNum(e.maj, now + JOUR) || now,
           actif: actif, debut: actif ? debut : 0, taches: taches, hist: hist };
}

function lu(raw){
  if(!raw) return null;
  try{ return JSON.parse(raw); }catch(e){ return null; }
}

/* La réponse du raccourci : un mot, sans retour à la ligne, jamais en cache. */
function mot(res, code, txt){
  res.statusCode = code;
  res.setHeader('Content-Type', 'text/plain; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(txt);
}

/* ------------------------------------------------------------- actions -- */
/* Le raccourci passe ici. On note l'heure de son passage : c'est ce qui permet
   à l'app d'afficher « raccourci vu il y a 2 min ». Autrement, personne ne
   saurait si l'automatisation est vraiment branchée. */
function doRaccourci(res, k){
  if(!k)          return mot(res, 400, 'cle invalide');
  if(!hasStore()) return mot(res, 200, 'libre');
  var now = Date.now();
  return redis([
    ['GET', 'focus:' + k],
    ['SET', 'focusvu:' + k, String(now), 'EX', TTL]
  ]).then(function(o){
    mot(res, 200, bloque(lu(o[0]), now) ? 'bloque' : 'libre');
  }).catch(function(){ mot(res, 200, 'libre'); });
}

function doLire(res, k){
  return redis([['GET', 'focus:' + k], ['GET', 'focusvu:' + k]]).then(function(o){
    var e = lu(o[0]);
    send(res, 200, { ok:true, etat:e, vu:Number(o[1]) || 0, bloque:bloque(e, Date.now()) });
  });
}

/* Le plus récent gagne. Un onglet resté ouvert depuis hier ne doit pas écraser
   ce qui a été coché entre-temps dans l'app : on lui renvoie l'état rangé, et
   il le reprend. */
function doEcrire(res, k, brut){
  var now = Date.now(), neuf = propre(brut, now);
  return redis([['GET', 'focus:' + k]]).then(function(o){
    var ancien = lu(o[0]);
    if(ancien && Number(ancien.maj) > neuf.maj){
      return send(res, 200, { ok:false, cause:'perime', etat:ancien, bloque:bloque(ancien, now) });
    }
    return redis([['SET', 'focus:' + k, JSON.stringify(neuf), 'EX', TTL]]).then(function(){
      send(res, 200, { ok:true, etat:neuf, bloque:bloque(neuf, now) });
    });
  });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }

  if(req.method === 'GET'){
    var q = new URL(req.url || '/', 'http://x').searchParams;
    if(q.has('k')) return doRaccourci(res, cleOf(q.get('k')));
    return send(res, 200, { ok:true, version:1, store:hasStore() });
  }
  if(req.method !== 'POST') return send(res, 405, { error:'method' });
  if(!hasStore())           return send(res, 501, { error:'no_store' });

  return readBody(req).then(function(body){
    var a = body && body.action, k = cleOf(body && body.k);
    if(!k) return send(res, 400, { error:'cle_invalide' });
    if(a === 'lire')   return doLire(res, k);
    if(a === 'ecrire') return doEcrire(res, k, body.etat);
    return send(res, 400, { error:'bad_action' });
  }).catch(function(e){
    send(res, 502, { error:'erreur', detail:String(e && e.message || e).slice(0, 140) });
  });
};
