/* ============================================================================
   Cadence — le coach.

   C'est la seule fonction qui coûte de l'argent : chaque réponse est facturée
   au fournisseur d'IA. Tout ici est donc écrit pour que ça coûte le moins
   possible, et pour que ce que ça coûte soit visible.

   Ce qui sort d'ici vers Anthropic : la consigne de départ, ce que l'app a
   assemblé comme contexte (si et seulement si le téléphone l'a joint), et la
   question. Rien n'est lu dans la base pour fabriquer ce contexte : c'est
   l'app qui l'envoie, ce qui veut dire qu'elle peut le montrer tel quel avant
   l'envoi. La clé, elle, ne quitte jamais le serveur.

   Ce qui est gardé ici : un compteur de messages par compte et par jour, et
   rien d'autre. Aucune conversation n'est conservée.
   ========================================================================== */

var Anthropic = require('@anthropic-ai/sdk');
var S = require('./_store.js');
var redis = S.redis, hasStore = S.hasStore, readBody = S.readBody, send = S.send;
var cleanTxt = S.cleanTxt, cleanNum = S.cleanNum;

/* Le modèle par défaut est le plus capable ; les deux autres sont là parce
   que c'est une dépense réelle et que le choix revient à celui qui paie. */
var MODELES = {
  'claude-opus-5':   { n:'Opus 5',    e:5.00, s:25.00 },   /* $ par million de jetons */
  'claude-sonnet-5': { n:'Sonnet 5',  e:2.00, s:10.00 },
  'claude-haiku-4-5':{ n:'Haiku 4.5', e:1.00, s: 5.00 }
};
var DEFAUT = 'claude-opus-5';

var MAX_JOUR   = 40;      /* messages par compte et par jour */
/* Le plafond de sortie est un filet, pas un budget : on ne paie que ce qui est
   réellement écrit. Il doit laisser de la place à la réflexion du modèle, qui
   se compte dedans — trop bas, elle rognerait la réponse. La brièveté se
   demande dans la consigne, pas avec des ciseaux. */
var MAX_SORTIE = 2000;
var MAX_Q      = 600;     /* longueur d'une question */
var MAX_TOURS  = 6;       /* on ne renvoie que la fin de la conversation */
var TTL_QUOTA  = 60 * 60 * 48;

/* La consigne ne bouge jamais d'un appel à l'autre : c'est ce qui permet de
   la mettre en cache et de ne la payer qu'une fois toutes les cinq minutes. */
var SYSTEME =
  "Tu es le coach de Cadence, une application française d'habitudes et d'entraînement.\n\n" +
  "Comment tu réponds :\n" +
  "- En français, en tutoyant, direct et concret. Pas de flatterie, pas de préambule.\n" +
  "- Court : trois à six phrases, ou une liste de trois à cinq points. On te lit sur un téléphone.\n" +
  "- Une réponse utile tout de suite plutôt qu'une liste de questions en retour. Si une précision " +
  "change vraiment la réponse, donne d'abord le conseil le plus probable, puis pose la question.\n" +
  "- Quand on te donne des chiffres (séances, séries, récupération, calories), appuie-toi dessus " +
  "et cite-les. Quand tu n'as pas la donnée, dis-le au lieu de l'inventer.\n\n" +
  "Ce que tu ne fais pas :\n" +
  "- Aucun diagnostic, aucun avis médical, aucun conseil sur des médicaments ou des dosages. " +
  "Devant une douleur qui dure, une blessure, un malaise, un trouble alimentaire ou une question " +
  "de santé, dis-le franchement et renvoie vers un médecin, un kiné ou un diététicien. " +
  "Tu peux ensuite proposer d'adapter la séance pour éviter la zone concernée.\n" +
  "- Aucun régime très restrictif, aucun encouragement à s'entraîner malgré la douleur, " +
  "aucun objectif de poids présenté comme une valeur morale.\n" +
  "- Tu ne prétends pas connaître ce qui n'est pas dans le contexte fourni.";

/* --------------------------------------------------------------- contexte */
/* On ne fait jamais confiance à ce que le téléphone envoie : chaque champ est
   borné avant d'entrer dans la conversation. */
function ligne(l, v){ return (v === null || v === undefined || v === '') ? '' : (l + ' : ' + v + '\n'); }
function rendreContexte(c){
  if(!c || typeof c !== 'object') return '';
  var t = '';
  t += ligne('Profil', cleanTxt(c.profil, 160));
  t += ligne('Objectif', cleanTxt(c.objectif, 60));
  t += ligne('Contraintes déclarées', cleanTxt(c.contraintes, 400));
  t += ligne('Zones sensibles', cleanTxt(c.zones, 160));
  t += ligne('Cette semaine', cleanTxt(c.semaine, 200));
  t += ligne('Récupération', cleanTxt(c.recup, 300));
  t += ligne('Prochaine séance', cleanTxt(c.seance, 400));
  t += ligne('Nutrition du jour', cleanTxt(c.nutrition, 200));
  t += ligne('Habitudes du jour', cleanTxt(c.jour, 300));
  return t ? ('Contexte, fourni par son application :\n' + t) : '';
}
function rendreTours(l){
  if(!Array.isArray(l)) return [];
  return l.slice(-MAX_TOURS).map(function(m){
    var r = (m && m.r === 'a') ? 'assistant' : 'user';
    var t = cleanTxt(m && m.t, MAX_Q);
    return t ? { role:r, content:t } : null;
  }).filter(Boolean);
}

/* ------------------------------------------------------------- identité -- */
function uidOf(token){
  var t = String(token || '');
  if(!/^[a-z0-9]{20,40}$/.test(t)) return Promise.resolve('');
  return redis([['GET', 'sess:' + t]]).then(function(o){ return o[0] ? String(o[0]) : ''; });
}
function jourKey(){
  var d = new Date();
  return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' +
         String(d.getUTCDate()).padStart(2, '0');
}

/* -------------------------------------------------------------- réponse -- */
function doAsk(res, body, uid){
  var question = cleanTxt(body.q, MAX_Q).trim();
  if(!question) return send(res, 400, { error:'question_vide' });

  var modele = MODELES[body.model] ? body.model : DEFAUT;
  var cle = 'coach:' + uid + ':' + jourKey();

  return redis([['INCR', cle], ['EXPIRE', cle, TTL_QUOTA]]).then(function(o){
    var n = +o[0] || 1;
    if(n > MAX_JOUR){
      return send(res, 429, { error:'quota', message:'Tu as atteint les ' + MAX_JOUR +
        ' messages du jour. Ça repart demain.' });
    }

    var contexte = rendreContexte(body.ctx);
    var tours = rendreTours(body.hist);
    var dernier = contexte ? (contexte + '\nSa question : ' + question) : question;
    tours.push({ role:'user', content: dernier });

    var client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    return client.messages.create({
      model: modele,
      max_tokens: MAX_SORTIE,
      /* effort bas : une réponse de coach tient en cinq phrases, la profondeur
         de raisonnement ne change rien à la qualité et coûte des jetons. */
      output_config: { effort: 'low' },
      /* la consigne ne bouge pas : mise en cache, elle n'est payée plein tarif
         qu'une fois toutes les cinq minutes, tous utilisateurs confondus. */
      system: [{ type:'text', text:SYSTEME, cache_control:{ type:'ephemeral' } }],
      messages: tours
    }).then(function(r){
      if(r.stop_reason === 'refusal'){
        return send(res, 200, { ok:false, cause:'refus',
          message:'Le coach a préféré ne pas répondre à ça.' });
      }
      var texte = (r.content || []).filter(function(b){ return b.type === 'text'; })
                                   .map(function(b){ return b.text; }).join('\n').trim();
      var u = r.usage || {}, m = MODELES[modele];
      var entree = (+u.input_tokens || 0) + (+u.cache_creation_input_tokens || 0) +
                   (+u.cache_read_input_tokens || 0);
      var cout = ((+u.input_tokens || 0) * m.e + (+u.cache_creation_input_tokens || 0) * m.e * 1.25 +
                  (+u.cache_read_input_tokens || 0) * m.e * 0.1 +
                  (+u.output_tokens || 0) * m.s) / 1000000;
      send(res, 200, {
        ok: true,
        texte: texte || "Je n'ai rien à ajouter là-dessus.",
        tronque: r.stop_reason === 'max_tokens',
        modele: modele,
        reste: Math.max(0, MAX_JOUR - n),
        usage: { entree:entree, cache:(+u.cache_read_input_tokens || 0), sortie:(+u.output_tokens || 0) },
        cout: Math.round(cout * 1000000) / 1000000        /* en dollars */
      });
    });
  }).catch(function(e){
    /* On ne remonte jamais le détail brut d'une erreur d'API au téléphone :
       il peut contenir des bribes de la requête. */
    var st = e && e.status;
    if(st === 401 || st === 403) return send(res, 200, { ok:false, cause:'cle',
      message:'La clé du coach est refusée. Vérifie ANTHROPIC_API_KEY sur l\'hébergeur.' });
    if(st === 429) return send(res, 200, { ok:false, cause:'charge',
      message:'Trop de demandes en même temps. Réessaie dans un instant.' });
    if(st === 400) return send(res, 200, { ok:false, cause:'requete',
      message:'La demande a été refusée par l\'API. Réessaie avec une question plus courte.' });
    return send(res, 200, { ok:false, cause:'reseau',
      message:'Le coach ne répond pas. Réessaie dans un instant.' });
  });
}

/* ------------------------------------------------------------- entrée ---- */
module.exports = function(req, res){
  if(req.method === 'OPTIONS'){ res.statusCode = 204; return res.end(); }

  if(req.method === 'GET'){
    return send(res, 200, {
      ok: true, version: 1,
      pret: !!process.env.ANTHROPIC_API_KEY,
      store: hasStore(),
      defaut: DEFAUT,
      maxJour: MAX_JOUR,
      modeles: Object.keys(MODELES).map(function(k){
        return { id:k, n:MODELES[k].n, e:MODELES[k].e, s:MODELES[k].s };
      })
    });
  }
  if(req.method !== 'POST') return send(res, 405, { error:'method' });
  if(!hasStore())           return send(res, 501, { error:'no_store' });
  if(!process.env.ANTHROPIC_API_KEY)
    return send(res, 200, { ok:false, cause:'non_configure',
      message:'Le coach n\'est pas branché sur ce déploiement.' });

  return readBody(req).then(function(body){
    if(!body || body.action !== 'ask') return send(res, 400, { error:'bad_action' });
    return uidOf(body.token).then(function(uid){
      if(!uid) return send(res, 401, { error:'session_invalide' });
      return doAsk(res, body, uid);
    });
  }).catch(function(e){
    send(res, 502, { error:'erreur', detail:String(e && e.message || e).slice(0, 160) });
  });
};
