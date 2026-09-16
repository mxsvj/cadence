/* ============================================================================
   Cadence — les groupes.

   Le classement entre amis existait déjà : chacun colle le code de l'autre et
   les deux se voient. Un groupe, c'est autre chose — un endroit où tout le
   monde voit tout le monde d'un coup, et où l'on peut se lancer un défi
   commun. D'où un code unique par groupe plutôt qu'un code par personne.

   Ce qui est stocké, et rien d'autre :
     crew:<code>   { nom, créé le }
     crewm:<code>  l'ensemble des identifiants de joueur du groupe
     crewd:<code>  les défis en cours, en JSON
   Les fiches des joueurs (p:<id>) sont celles du classement : le groupe ne
   duplique rien, il ne fait que les rassembler.

   Tout expire au bout de six mois sans activité.
   ========================================================================== */

var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;
var cleanId = S.cleanId, cleanTxt = S.cleanTxt, cleanNum = S.cleanNum;

var TTL_CREW = 60 * 60 * 24 * 180;   /* six mois */
var MAX_MEMBRES = 30;
var MAX_GROUPES = 8;                 /* par joueur, côté app */
var MAX_DEFIS   = 6;

/* Un alphabet sans 0/O ni 1/I/L : un code se lit à voix haute ou se recopie
   d'une capture d'écran, il ne doit pas prêter à confusion. */
var ALPHA = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
function codeNeuf(){
  var c = '';
  for(var i = 0; i < 6; i++) c += ALPHA[Math.floor(Math.random() * ALPHA.length)];
  return c;
}
function cleanCode(c){
  var v = String(c || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
  return v.length === 6 ? v : '';
}
function cleanCodes(a){
  return (Array.isArray(a) ? a : []).map(cleanCode).filter(Boolean).slice(0, MAX_GROUPES);
}

/* Un défi porte sur ce que les fiches des joueurs savent déjà dire : des
   répétitions d'un exercice, des séances, des séries ou des points. Rien à
   calculer côté serveur, donc rien à maintenir en double. */
var METRIQUES = ['rep', 'sea', 'ser', 'pts'];
function cleanDefi(o){
  if(!o || typeof o !== 'object') return null;
  var m = METRIQUES.indexOf(String(o.m)) > -1 ? String(o.m) : 'rep';
  var n = cleanTxt(o.n, 34);
  var cible = cleanNum(o.c, 1000000);
  if(!n || cible <= 0) return null;
  var d = { i: cleanTxt(o.i, 12) || String(Date.now()).slice(-8), n: n, m: m, c: cible,
            s: cleanTxt(o.s, 10) || '' };            /* s : la semaine, clé du lundi */
  if(m === 'rep'){
    var x = String(o.x || '');
    if(!/^[a-z0-9]{1,24}$/.test(x)) return null;
    d.x = x;
  }
  return d;
}
function lireDefis(raw){
  var a = [];
  try{ a = JSON.parse(raw || '[]'); }catch(e){ a = []; }
  return (Array.isArray(a) ? a : []).map(cleanDefi).filter(Boolean).slice(0, MAX_DEFIS);
}

/* --------------------------------------------------------------- lecture */
/* Un groupe complet : sa fiche, ses membres, ses défis. Les membres viennent
   de p:<id> — si quelqu'un n'a pas ouvert l'app depuis trois mois, sa fiche a
   expiré et il n'apparaît simplement plus. */
function lireGroupe(code){
  return redis([['GET', 'crew:' + code], ['SMEMBERS', 'crewm:' + code], ['GET', 'crewd:' + code]])
    .then(function(o){
      if(!o[0]) return null;
      var fiche;
      try{ fiche = JSON.parse(o[0]); }catch(e){ return null; }
      var ids = (o[1] || []).map(cleanId).filter(Boolean).slice(0, MAX_MEMBRES);
      var defis = lireDefis(o[2]);
      if(!ids.length) return { code: code, nom: fiche.n || 'Groupe', membres: [], defis: defis };
      return redis([['MGET'].concat(ids.map(function(i){ return 'p:' + i; }))]).then(function(r){
        var membres = (r[0] || []).map(function(v){
          if(!v) return null;
          try{ return typeof v === 'string' ? JSON.parse(v) : v; }catch(e){ return null; }
        }).filter(Boolean);
        return { code: code, nom: fiche.n || 'Groupe', membres: membres, defis: defis };
      });
    });
}

/* --------------------------------------------------------------- actions */
function doCreate(res, body){
  var me = cleanId(body.me), nom = cleanTxt(body.nom, 24) || 'Mon groupe';
  if(!me) return send(res, 400, { error: 'bad_id' });

  /* On tire un code et on ne l'accepte que s'il était libre (NX) : deux
     créations simultanées ne peuvent pas atterrir sur le même. */
  var essais = 0;
  function tenter(){
    var code = codeNeuf();
    return redis([['SET', 'crew:' + code, JSON.stringify({ n: nom, at: Date.now() }), 'EX', TTL_CREW, 'NX']])
      .then(function(o){
        if(!o[0]){
          if(++essais >= 5) return send(res, 503, { error: 'code_indisponible' });
          return tenter();
        }
        return redis([['SADD', 'crewm:' + code, me], ['EXPIRE', 'crewm:' + code, TTL_CREW]])
          .then(function(){
            return lireGroupe(code).then(function(g){ send(res, 200, { ok: true, crew: g }); });
          });
      });
  }
  return tenter();
}

function doJoin(res, body){
  var me = cleanId(body.me), code = cleanCode(body.code);
  if(!me || !code) return send(res, 400, { error: 'bad_id' });
  return redis([['GET', 'crew:' + code], ['SCARD', 'crewm:' + code]]).then(function(o){
    if(!o[0]) return send(res, 404, { error: 'introuvable' });
    if((+o[1] || 0) >= MAX_MEMBRES) return send(res, 409, { error: 'complet' });
    return redis([
      ['SADD', 'crewm:' + code, me],
      ['EXPIRE', 'crewm:' + code, TTL_CREW],
      ['EXPIRE', 'crew:' + code, TTL_CREW]
    ]).then(function(){
      return lireGroupe(code).then(function(g){ send(res, 200, { ok: true, crew: g }); });
    });
  });
}

function doLeave(res, body){
  var me = cleanId(body.me), code = cleanCode(body.code);
  if(!me || !code) return send(res, 400, { error: 'bad_id' });
  return redis([['SREM', 'crewm:' + code, me]]).then(function(){
    send(res, 200, { ok: true });
  });
}

/* Un seul aller-retour pour tous les groupes : c'est appelé à chaque
   ouverture de l'onglet, autant ne pas multiplier les requêtes. */
function doRead(res, body){
  var me = cleanId(body.me), codes = cleanCodes(body.codes);
  if(!me) return send(res, 400, { error: 'bad_id' });
  if(!codes.length) return send(res, 200, { ok: true, crews: [] });
  return Promise.all(codes.map(lireGroupe)).then(function(l){
    send(res, 200, { ok: true, crews: l.filter(Boolean) });
  });
}

/* Les défis sont posés par n'importe quel membre : un groupe entre potes n'a
   pas de chef, et le seul dégât possible est une ligne en trop. */
function doDefi(res, body){
  var me = cleanId(body.me), code = cleanCode(body.code);
  if(!me || !code) return send(res, 400, { error: 'bad_id' });
  var d = cleanDefi(body.defi);
  if(!d) return send(res, 400, { error: 'defi_invalide' });
  return redis([['SISMEMBER', 'crewm:' + code, me], ['GET', 'crewd:' + code]]).then(function(o){
    if(!+o[0]) return send(res, 403, { error: 'pas_membre' });
    var l = lireDefis(o[1]).filter(function(x){ return x.i !== d.i; });
    l.unshift(d);
    return redis([['SET', 'crewd:' + code, JSON.stringify(l.slice(0, MAX_DEFIS)), 'EX', TTL_CREW]])
      .then(function(){ send(res, 200, { ok: true, defis: l.slice(0, MAX_DEFIS) }); });
  });
}

function doUndefi(res, body){
  var me = cleanId(body.me), code = cleanCode(body.code);
  var id = cleanTxt(body.id, 12);
  if(!me || !code || !id) return send(res, 400, { error: 'bad_id' });
  return redis([['SISMEMBER', 'crewm:' + code, me], ['GET', 'crewd:' + code]]).then(function(o){
    if(!+o[0]) return send(res, 403, { error: 'pas_membre' });
    var l = lireDefis(o[1]).filter(function(x){ return x.i !== id; });
    return redis([['SET', 'crewd:' + code, JSON.stringify(l), 'EX', TTL_CREW]])
      .then(function(){ send(res, 200, { ok: true, defis: l }); });
  });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }
  if(req.method === 'GET')     return send(res, 200, { ok: true, version: 1, store: hasStore() });
  if(req.method !== 'POST')    return send(res, 405, { error: 'method' });
  if(!hasStore())              return send(res, 501, { error: 'no_store' });

  return readBody(req).then(function(body){
    var a = body && body.action;
    if(a === 'create') return doCreate(res, body);
    if(a === 'join')   return doJoin(res, body);
    if(a === 'leave')  return doLeave(res, body);
    if(a === 'read')   return doRead(res, body);
    if(a === 'defi')   return doDefi(res, body);
    if(a === 'undefi') return doUndefi(res, body);
    return send(res, 400, { error: 'bad_action' });
  }).catch(function(e){
    send(res, 502, { error: 'erreur', detail: String(e && e.message || e).slice(0, 160) });
  });
};
