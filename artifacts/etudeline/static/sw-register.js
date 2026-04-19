// Service Worker Registration for Progressive Web App
// Gère l'enregistrement du service worker pour les notifications push

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/sw.js')
      .then(function(registration) {
        console.log('✅ Service Worker enregistré avec succès:', registration.scope);
        
        // Vérifier les mises à jour du service worker périodiquement
        setInterval(function() {
          registration.update();
        }, 60000); // Vérifier toutes les minutes
      })
      .catch(function(error) {
        console.log('❌ Échec de l\'enregistrement du Service Worker:', error);
      });
  });
  
  // Gérer les mises à jour du service worker
  navigator.serviceWorker.addEventListener('controllerchange', function() {
    console.log('🔄 Service Worker mis à jour - rechargement...');
    window.location.reload();
  });
}
