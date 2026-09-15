/* Service worker de Cadence.

   Il ne sert qu'aux notifications. Volontairement AUCUNE mise en cache : une
   app servie depuis un cache local finit par afficher une vieille version
   pendant des jours, et c'est exactement le genre de panne qu'on ne peut plus
   diagnostiquer à distance. Chaque ouverture va chercher la page sur le réseau.
*/
self.addEventListener('install',  function(){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()); });

self.addEventListener('push', function(e){
  var d = {};
  try { d = e.data ? e.data.json() : {}; }
  catch(err) { d = { body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || 'Cadence', {
    body:  d.body || '',
    icon:  '/icon-192.png',
    badge: '/icon-192.png',
    tag:   d.tag || 'cadence',
    data:  { url: d.url || '/' }
  }));
});

self.addEventListener('notificationclick', function(e){
  e.notification.close();
  var url = (e.notification.data && e.notification.data.url) || '/';
  e.waitUntil(self.clients.matchAll({ type:'window', includeUncontrolled:true }).then(function(list){
    for(var i = 0; i < list.length; i++){
      if('focus' in list[i]) return list[i].focus();      /* l'app est déjà ouverte */
    }
    if(self.clients.openWindow) return self.clients.openWindow(url);
  }));
});
