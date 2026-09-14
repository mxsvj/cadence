/* ============================================================================
   Compte Google et sauvegarde des données.

   Identité : le client obtient un jeton d'identité auprès de Google, on le
   fait valider par Google, et on rend en échange un jeton de session à nous —
   ainsi on ne redemande pas Google à chaque appel, et le jeton Google, qui
   expire en une heure, n'a pas à être conservé.

   Données : l'état de l'application est rangé tel quel sous u:<compte>. Le
   serveur ne l'inspecte pas, il l'horodate et le rend.
   ========================================================================== */

var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;

var CLIENT_ID  = process.env.GOOGLE_CLIENT_ID || '';
var TTL_SESSION = 60 * 60 * 24 * 90;          /* 90 jours */
var MAX_STATE   = 700 * 1024;                 /* un état déraisonnable est refusé */

/* ------------------------------------------------------- identité Google */
/* On s'adresse au point de contrôle officiel de Google plutôt que de vérifier
   la signature à la main : moins de code cryptographique à se tromper. */
function verifyGoogle(idToken){
  return fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(idToken))
    .then(function(r){
      if(!r.ok) throw new Error('jeton refusé par Google (' + r.status + ')');
      return r.json();
    })
    .then(function(t){
      if(!t || !t.sub) throw new Error('jeton sans identifiant');
      if(CLIENT_ID && t.aud !== CLIENT_ID) throw new Error('jeton émis pour une autre application');
      if(t.exp && (Number(t.exp) * 1000) < Date.now()) throw new Error('jeton expiré');
      return {
        uid:     'g' + String(t.sub).replace(/[^0-9]/g, '').slice(0, 30),
        name:    String(t.name || t.given_name || '').slice(0, 40),
        picture: /^https:\/\//.test(t.picture || '') ? String(t.picture).slice(0, 300) : ''
      };
    });
}

function newToken(){
  var a = '';
  for(var i = 0; i < 4; i++) a += Math.random().toString(36).slice(2, 12);
  return a.slice(0, 40);
}

/* Un jeton de session vaut identité : on le relit à chaque appel. */
function uidOf(token){
  var t = String(token || '');
  if(!/^[a-z0-9]{20,40}$/.test(t)) return Promise.resolve('');
  return redis([['GET', 'sess:' + t]]).then(function(o){
    return o[0] ? String(o[0]) : '';
  });
}

/* ------------------------------------------------------------- actions -- */
function doLogin(res, body){
  if(!CLIENT_ID){
    return send(res, 200, { ok:false, cause:'non_configure',
      message:'La connexion Google n\'est pas configurée sur ce déploiement.' });
  }
  var idToken = String(body.idToken || '');
  if(!idToken) return send(res, 400, { error:'jeton_manquant' });

  return verifyGoogle(idToken).then(function(u){
    var token = newToken();
    return redis([
      ['SET', 'sess:' + token, u.uid, 'EX', TTL_SESSION],
      ['SET', 'who:' + u.uid, JSON.stringify({ name:u.name, picture:u.picture }), 'EX', TTL_SESSION],
      ['GET', 'u:' + u.uid]
    ]).then(function(o){
      var raw = o[2], remote = null;
      if(raw){ try{ remote = JSON.parse(raw); }catch(e){ remote = null; } }
      send(res, 200, { ok:true, token:token, uid:u.uid, name:u.name, picture:u.picture,
        remote: remote ? { updatedAt: remote.updatedAt || 0, size: String(raw).length } : null });
    });
  }).catch(function(e){
    send(res, 200, { ok:false, cause:'refuse', message:String(e && e.message || e).slice(0, 160) });
  });
}

function doPull(res, body){
  return uidOf(body.token).then(function(uid){
    if(!uid) return send(res, 401, { error:'session_invalide' });
    return redis([['GET', 'u:' + uid]]).then(function(o){
      var raw = o[0];
      if(!raw) return send(res, 200, { ok:true, state:null, updatedAt:0 });
      var box;
      try{ box = JSON.parse(raw); }catch(e){ return send(res, 200, { ok:true, state:null, updatedAt:0 }); }
      send(res, 200, { ok:true, state: box.state || null, updatedAt: box.updatedAt || 0 });
    });
  });
}

function doPush(res, body){
  return uidOf(body.token).then(function(uid){
    if(!uid) return send(res, 401, { error:'session_invalide' });
    if(!body.state || typeof body.state !== 'object') return send(res, 400, { error:'etat_manquant' });
    var box = JSON.stringify({ updatedAt: Date.now(), state: body.state });
    if(box.length > MAX_STATE) return send(res, 413, { error:'etat_trop_gros', taille:box.length });
    return redis([['SET', 'u:' + uid, box]]).then(function(){
      send(res, 200, { ok:true, updatedAt: JSON.parse(box).updatedAt, taille: box.length });
    });
  });
}

function doLogout(res, body){
  var t = String(body.token || '');
  if(!/^[a-z0-9]{20,40}$/.test(t)) return send(res, 200, { ok:true });
  return redis([['DEL', 'sess:' + t]]).then(function(){ send(res, 200, { ok:true }); });
}

/* ------------------------------------------------------------- entrée --- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }

  if(req.method === 'GET'){
    return send(res, 200, { ok:true, version:1,
      google: !!CLIENT_ID, clientId: CLIENT_ID || null, store: hasStore() });
  }
  if(req.method !== 'POST') return send(res, 405, { error:'method' });
  if(!hasStore())           return send(res, 501, { error:'no_store' });

  return readBody(req).then(function(body){
    var a = body && body.action;
    if(a === 'login')  return doLogin(res, body);
    if(a === 'pull')   return doPull(res, body);
    if(a === 'push')   return doPush(res, body);
    if(a === 'logout') return doLogout(res, body);
    return send(res, 400, { error:'bad_action' });
  }).catch(function(e){
    send(res, 502, { error:'erreur', detail:String(e && e.message || e).slice(0, 140) });
  });
};
