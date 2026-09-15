/* ============================================================================
   Notifications push.

   Trois choses à savoir sur la façon dont c'est monté :

   1. Les clés de signature sont fabriquées au premier besoin et rangées dans
      Redis. Pas de secret à déclarer à la main, et la clé privée ne se trouve
      nulle part dans le dépôt.
   2. Envoyer au bon moment demande de connaître les habitudes, leurs horaires,
      ce qui est déjà fait, et le décalage horaire de l'appareil. Tout cela vit
      dans les données du compte : les notifications supposent donc d'être
      connecté.
   3. Le déclencheur (tick) est sans effet s'il est appelé trop souvent : une
      notification déjà envoyée aujourd'hui ne repart pas. Il n'a donc pas
      besoin d'être protégé par un secret, seulement bridé pour ne pas gaspiller
      d'appels.
   ========================================================================== */

var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;

var FENETRE   = 45;               /* minutes après l'horaire pendant lesquelles on prévient */
var MAX_USERS = 200;              /* garde-fou sur la durée d'un tick */
var TTL_NOTIF = 60 * 60 * 24 * 3;
/* Le « sub » de la signature : les services de notification veulent une adresse
   qui identifie l'expéditeur, et celui d'Apple refuse ce qui n'est pas une vraie
   adresse mail ou une vraie URL. On prend donc l'adresse du déploiement, que
   l'hébergeur fournit lui-même. */
var CONTACT = process.env.PUSH_CONTACT ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL ? 'https://' + process.env.VERCEL_PROJECT_PRODUCTION_URL : '') ||
  (process.env.VERCEL_URL ? 'https://' + process.env.VERCEL_URL : '') ||
  'https://cadence-ten-theta.vercel.app';

/* ------------------------------------------------------------- outils --- */
function pad(n){ return String(n).padStart(2, '0'); }
function toMin(t){ var a = String(t || '').split(':'); return (+a[0]) * 60 + (+a[1] || 0); }

/* L'heure locale de l'appareil, reconstituée depuis son décalage.

   Le décalage est celui que le navigateur donne (getTimezoneOffset : positif
   à l'ouest de Greenwich). On décale l'instant de façon à ce que les champs
   UTC de la date obtenue soient exactement l'heure affichée sur le téléphone.
   D'où les lecteurs UTC partout en dessous : le résultat ne dépend alors plus
   du fuseau de la machine qui exécute ce code. */
function localNow(tzOffset){
  var off = Number(tzOffset);
  if(!isFinite(off)) off = 0;
  return new Date(Date.now() - off * 60000);
}
function keyOf(d){ return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); }

/* ------------------------------------------------- clés de signature ----- */
var _vapid = null;
function vapid(){
  if(_vapid) return Promise.resolve(_vapid);
  return redis([['GET', 'vapid']]).then(function(o){
    if(o[0]){
      try { _vapid = JSON.parse(o[0]); return _vapid; } catch(e){ /* on régénère */ }
    }
    var k = require('web-push').generateVAPIDKeys();
    _vapid = { publicKey: k.publicKey, privateKey: k.privateKey };
    /* NX : si deux appels tombent en même temps, le premier gagne et l'autre relit */
    return redis([['SET', 'vapid', JSON.stringify(_vapid), 'NX'], ['GET', 'vapid']])
      .then(function(r){
        try { _vapid = JSON.parse(r[1]); } catch(e){}
        return _vapid;
      });
  });
}

/* ------------------------------------------------------- abonnements ----- */
function getSubs(uid){
  return redis([['GET', 'subs:' + uid]]).then(function(o){
    if(!o[0]) return [];
    try { var a = JSON.parse(o[0]); return Array.isArray(a) ? a : []; } catch(e){ return []; }
  });
}
function setSubs(uid, list){
  if(!list.length) return redis([['DEL', 'subs:' + uid], ['SREM', 'pushusers', uid]]);
  return redis([['SET', 'subs:' + uid, JSON.stringify(list.slice(0, 10))],
                ['SADD', 'pushusers', uid]]);
}

/* --------------------------------------------- qui doit être prévenu ----- */
/* On refait ici le raisonnement de l'application : une habitude est due si
   elle tombe aujourd'hui, n'a pas été retirée de la journée, n'est pas déjà
   faite, et si son horaire vient de passer. */
function dues(st, maintenant){
  var jour = keyOf(maintenant), mn = maintenant.getUTCHours() * 60 + maintenant.getUTCMinutes();
  var off = (st.off && st.off[jour]) || [];
  var log = (st.log && st.log[jour]) || {};
  /* triées par horaire : si deux rendez-vous sont en retard, on rappelle
     d'abord le plus ancien, pas celui qui a été créé en premier. */
  return (st.habits || []).slice().sort(function(a, b){ return toMin(a && a.time) - toMin(b && b.time); })
   .filter(function(h){
    if(!h || !h.time) return false;
    if(h.createdAt && jour < h.createdAt) return false;
    if(h.type === 'once' ? (h.date !== jour)
                         : ((h.days || []).indexOf(maintenant.getUTCDay()) < 0)) return false;
    if(off.indexOf(h.id) > -1) return false;
    if(log[h.id] && log[h.id].done) return false;
    var d = mn - toMin(h.time);
    return d >= 0 && d <= FENETRE;
  });
}

function envoyer(sub, payload, keys){
  var wp = require('web-push');
  wp.setVapidDetails(CONTACT, keys.publicKey, keys.privateKey);
  return wp.sendNotification(
    { endpoint: sub.endpoint, keys: sub.keys },
    JSON.stringify(payload),
    /* urgency : un rappel à l'heure dite mérite de réveiller l'écran.
       timeout : un service qui ne répond pas ne doit pas manger tout le temps
       accordé à la fonction, il y a d'autres comptes à servir derrière. */
    { TTL: 3600, urgency: 'high', timeout: 8000 }
  ).then(function(){ return 'ok'; })
   .catch(function(e){
     var code = e && e.statusCode;
     return (code === 404 || code === 410) ? 'perime' : 'erreur';
   });
}

/* Envoie à tous les appareils d'un compte, et oublie ceux qui ne répondent plus. */
function envoyerAu(uid, payload, keys){
  return getSubs(uid).then(function(subs){
    if(!subs.length) return { envoyes: 0, retires: 0 };
    return Promise.all(subs.map(function(s){ return envoyer(s, payload, keys); }))
      .then(function(res){
        var vivants = subs.filter(function(_, i){ return res[i] !== 'perime'; });
        var envoyes = res.filter(function(r){ return r === 'ok'; }).length;
        var retires = subs.length - vivants.length;
        if(retires) return setSubs(uid, vivants).then(function(){ return { envoyes:envoyes, retires:retires }; });
        return { envoyes: envoyes, retires: 0 };
      });
  });
}

/* --------------------------------------------------------- le minuteur --- */
function doTick(res){
  return redis([['SET', 'ticklock', String(Date.now()), 'EX', 45, 'NX']]).then(function(lock){
    if(!lock[0]) return send(res, 200, { ok:true, ignore:'trop_rapproche' });
    return vapid().then(function(keys){
      return redis([['SMEMBERS', 'pushusers']]).then(function(o){
        var uids = (o[0] || []).slice(0, MAX_USERS);
        if(!uids.length) return send(res, 200, { ok:true, comptes:0, envoyes:0 });

        var envoyes = 0, examines = 0;
        var suite = uids.reduce(function(chaine, uid){
          return chaine.then(function(){
            return redis([['GET', 'u:' + uid]]).then(function(r){
              if(!r[0]) return;
              var st;
              try { st = JSON.parse(r[0]).state; } catch(e){ return; }
              if(!st) return;
              return getSubs(uid).then(function(subs){
                if(!subs.length) return;
                var maintenant = localNow(subs[0].tz);
                var jour = keyOf(maintenant);
                var aFaire = dues(st, maintenant);
                examines++;
                if(!aFaire.length) return;
                return redis([['GET', 'notif:' + uid + ':' + jour]]).then(function(n){
                  var deja = [];
                  try { deja = JSON.parse(n[0] || '[]'); } catch(e){}
                  var reste = aFaire.filter(function(h){ return deja.indexOf(h.id) < 0; });
                  if(!reste.length) return;
                  var h = reste[0];                       /* une seule à la fois : pas de rafale */
                  return envoyerAu(uid, {
                    title: (h.emoji || '⏰') + ' ' + h.name,
                    body:  "C'est l'heure — " + h.time,
                    tag:   'h_' + h.id,
                    url:   '/'
                  }, keys).then(function(r2){
                    envoyes += r2.envoyes;
                    deja.push(h.id);
                    return redis([['SET', 'notif:' + uid + ':' + jour, JSON.stringify(deja), 'EX', TTL_NOTIF]]);
                  });
                });
              });
            }).catch(function(){ /* un compte en erreur n'arrête pas les autres */ });
          });
        }, Promise.resolve());

        return suite.then(function(){
          send(res, 200, { ok:true, comptes: uids.length, examines: examines, envoyes: envoyes });
        });
      });
    });
  });
}

/* ------------------------------------------------------------- entrée --- */
function uidOf(token){
  var t = String(token || '');
  if(!/^[a-z0-9]{20,40}$/.test(t)) return Promise.resolve('');
  return redis([['GET', 'sess:' + t]]).then(function(o){ return o[0] ? String(o[0]) : ''; });
}

module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }
  if(!hasStore()) return send(res, 501, { error:'no_store' });

  if(req.method === 'GET'){
    return vapid().then(function(k){
      send(res, 200, { ok:true, version:1, vapid:k.publicKey });
    }).catch(function(e){
      send(res, 200, { ok:false, detail:String(e && e.message || e).slice(0, 140) });
    });
  }
  if(req.method !== 'POST') return send(res, 405, { error:'method' });

  return readBody(req).then(function(body){
    var a = body && body.action;

    if(a === 'tick') return doTick(res);

    return uidOf(body.token).then(function(uid){
      if(!uid) return send(res, 401, { error:'session_invalide' });

      if(a === 'subscribe'){
        var sub = body.subscription;
        if(!sub || !sub.endpoint || !sub.keys) return send(res, 400, { error:'abonnement_invalide' });
        return getSubs(uid).then(function(list){
          list = list.filter(function(s){ return s.endpoint !== sub.endpoint; });
          list.push({ endpoint:String(sub.endpoint).slice(0, 600), keys:sub.keys,
                      tz:Number(body.tz) || 0, at:Date.now() });
          return setSubs(uid, list).then(function(){
            send(res, 200, { ok:true, appareils:list.length });
          });
        });
      }
      if(a === 'unsubscribe'){
        return getSubs(uid).then(function(list){
          var reste = list.filter(function(s){ return s.endpoint !== body.endpoint; });
          return setSubs(uid, reste).then(function(){ send(res, 200, { ok:true, appareils:reste.length }); });
        });
      }
      if(a === 'test'){
        return vapid().then(function(keys){
          return envoyerAu(uid, { title:'Cadence', body:'Les notifications fonctionnent 🔥',
                                  tag:'test', url:'/' }, keys)
            .then(function(r){ send(res, 200, { ok:r.envoyes > 0, envoyes:r.envoyes, retires:r.retires }); });
        });
      }
      if(a === 'status'){
        return getSubs(uid).then(function(list){
          send(res, 200, { ok:true, appareils:list.length });
        });
      }
      return send(res, 400, { error:'bad_action' });
    });
  }).catch(function(e){
    send(res, 502, { error:'erreur', detail:String(e && e.message || e).slice(0, 160) });
  });
};
