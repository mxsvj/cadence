/* ============================================================================
   Cadence — les aliments, depuis Open Food Facts.

   Pourquoi passer par le serveur plutôt que d'appeler la base depuis le
   téléphone :
     · Open Food Facts demande un en-tête qui identifie l'application, et un
       navigateur ne laisse pas le choisir ;
     · une réponse de la base pèse parfois plusieurs centaines de kilo-octets ;
       ici on n'en garde que cinq champs ;
     · on met en cache. La base est tenue par des bénévoles, la marteler pour
       redemander cent fois le même paquet de pâtes serait malpoli.

   Rien de personnel ne transite : un code-barres ou un mot, rien d'autre. Pas
   de compte, pas de clé d'API — Open Food Facts est ouverte et gratuite, sous
   licence ODbL. C'est précisément pour ça qu'elle est utilisée ici.
   ========================================================================== */

var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;

var UA       = 'Cadence/1.0 (https://cadence-ten-theta.vercel.app)';
var TTL_CODE = 60 * 60 * 24 * 30;   /* un paquet ne change pas de recette tous les mois */
var TTL_Q    = 60 * 60 * 24 * 7;
var MAX_RES  = 12;
var TIMEOUT  = 7000;

var CHAMPS = 'code,product_name,product_name_fr,brands,nutriments,serving_size,quantity';

function cleanCode(c){
  var v = String(c || '').replace(/[^0-9]/g, '');
  return (v.length >= 6 && v.length <= 14) ? v : '';
}
function cleanQ(q){
  /* On garde l'ASCII imprimable et le latin étendu — accents et ç compris,
     c'est une recherche en français. Tout le reste (contrôles, emojis,
     séparateurs invisibles) devient une espace. */
  return String(q || '').replace(/[^\u0020-\u007e\u00a0-\u024f]/g, ' ')
         .replace(/\s+/g, ' ').trim().slice(0, 48);
}

/* fetch avec une limite de temps : la fonction ne doit pas rester pendue si la
   base met dix secondes à répondre. */
function fetchCourt(url){
  var ctl = typeof AbortController === 'function' ? new AbortController() : null;
  var t = ctl ? setTimeout(function(){ ctl.abort(); }, TIMEOUT) : null;
  return fetch(url, { headers: { 'User-Agent': UA, 'Accept': 'application/json' },
                      signal: ctl ? ctl.signal : undefined })
    .then(function(r){
      if(t) clearTimeout(t);
      if(!r.ok) throw new Error('off ' + r.status);
      return r.json();
    }, function(e){ if(t) clearTimeout(t); throw e; });
}

/* Une fiche Open Food Facts contient des centaines de champs. On n'en garde
   que ce qui sert : le nom, la marque, et deux chiffres pour cent grammes.
   Quand l'énergie n'est donnée qu'en kilojoules, on convertit. */
function pourCent(p){
  var n = (p && p.nutriments) || {};
  var kcal = +n['energy-kcal_100g'];
  if(!(kcal > 0)){
    var kj = +n['energy_100g'] || +n['energy-kj_100g'];
    if(kj > 0) kcal = kj / 4.184;
  }
  var prot = +n['proteins_100g'];
  var nom = String(p.product_name_fr || p.product_name || '').trim();
  if(!nom || !(kcal > 0)) return null;           /* sans nom ni calories, inutile */
  return {
    c: String(p.code || ''),
    n: nom.slice(0, 60),
    m: String(p.brands || '').split(',')[0].trim().slice(0, 30),
    kcal: Math.round(kcal),
    prot: prot > 0 ? Math.round(prot * 10) / 10 : 0,
    q: String(p.serving_size || p.quantity || '').slice(0, 20)
  };
}

/* ------------------------------------------------------------------ cache */
function duCache(cle){
  if(!hasStore()) return Promise.resolve(null);
  return redis([['GET', cle]]).then(function(o){
    try{ return o[0] ? JSON.parse(o[0]) : null; }catch(e){ return null; }
  }).catch(function(){ return null; });
}
function auCache(cle, val, ttl){
  if(!hasStore()) return Promise.resolve();
  return redis([['SET', cle, JSON.stringify(val), 'EX', ttl]]).catch(function(){});
}

/* ---------------------------------------------------------------- actions */
function parCode(res, code){
  var cle = 'off:c:' + code;
  return duCache(cle).then(function(hit){
    if(hit) return send(res, 200, { ok: true, cache: true, produit: hit });
    var url = 'https://world.openfoodfacts.org/api/v2/product/' + code + '.json?fields=' + CHAMPS;
    return fetchCourt(url).then(function(j){
      var p = j && j.product && pourCent(j.product);
      if(!p) return send(res, 404, { error: 'inconnu' });
      return auCache(cle, p, TTL_CODE).then(function(){
        send(res, 200, { ok: true, produit: p });
      });
    });
  });
}

/* Le classement d'Open Food Facts cherche dans tous les champs : demander
   « skyr » remonte d'abord des fromages blancs dont la fiche cite le mot
   quelque part. On reclasse donc sur ce que l'utilisateur voit vraiment, le
   nom du produit : d'abord ceux qui commencent par ce qu'il a tapé, puis ceux
   qui le contiennent, puis le reste dans l'ordre d'origine. */
function sansAccent(t){
  /* « pâtes » doit trouver « pates » : les fiches sont saisies à la main par
     des bénévoles, les accents y sont une loterie. */
  return String(t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}
function reclasser(l, q){
  var m = sansAccent(q);
  return l.map(function(x, i){
    var n = sansAccent(x.n), r = 3;
    if(n === m) r = 0;
    else if(n.indexOf(m) === 0) r = 1;
    else if(n.indexOf(m) > -1) r = 2;
    return { x: x, r: r, i: i };
  }).sort(function(a, b){ return a.r - b.r || a.i - b.i; })
    .map(function(o){ return o.x; });
}

function parNom(res, q){
  var cle = 'off:q2:' + sansAccent(q);
  return duCache(cle).then(function(hit){
    if(hit) return send(res, 200, { ok: true, cache: true, produits: hit });
    /* Le sous-domaine français fait remonter les produits d'ici en premier ;
       c'est la même base, seul le classement change. */
    var url = 'https://fr.openfoodfacts.org/cgi/search.pl?search_simple=1&action=process&json=1'
            + '&page_size=' + MAX_RES + '&fields=' + CHAMPS
            + '&search_terms=' + encodeURIComponent(q);
    return fetchCourt(url).then(function(j){
      var l = reclasser(((j && j.products) || []).map(pourCent).filter(Boolean), q).slice(0, MAX_RES);
      return auCache(cle, l, TTL_Q).then(function(){
        send(res, 200, { ok: true, produits: l });
      });
    });
  });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }
  if(req.method === 'GET')     return send(res, 200, { ok: true, version: 1, cache: hasStore() });
  if(req.method !== 'POST')    return send(res, 405, { error: 'method' });

  return readBody(req).then(function(body){
    var a = body && body.action;
    if(a === 'code'){
      var c = cleanCode(body.code);
      return c ? parCode(res, c) : send(res, 400, { error: 'code_invalide' });
    }
    if(a === 'search'){
      var q = cleanQ(body.q);
      return q.length >= 2 ? parNom(res, q) : send(res, 400, { error: 'requete_courte' });
    }
    return send(res, 400, { error: 'bad_action' });
  }).catch(function(e){
    send(res, 502, { error: 'base_injoignable', detail: String(e && e.message || e).slice(0, 120) });
  });
};
