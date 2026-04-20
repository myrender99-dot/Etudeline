// Service Worker Registration + Push Subscription
// Enregistre le SW ET souscrit aux push notifications hors-app

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
}

async function subscribeToPush(registration) {
  try {
    if (!('PushManager' in window)) return;

    // Vérifier si déjà souscrit
    const existing = await registration.pushManager.getSubscription();
    if (existing) {
      // Ré-envoyer au backend au cas où ce navigateur n'est pas encore enregistré
      const j = existing.toJSON();
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: j.endpoint, p256dh: j.keys.p256dh, auth: j.keys.auth })
      });
      return;
    }

    // Récupérer la clé VAPID publique
    const resp = await fetch('/api/push/vapid-key');
    if (!resp.ok) return;
    const { publicKey } = await resp.json();

    // Créer l'abonnement push
    const sub = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey)
    });

    const j = sub.toJSON();
    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: j.endpoint, p256dh: j.keys.p256dh, auth: j.keys.auth })
    });

    console.log('✅ Notifications push activées');
  } catch (err) {
    console.log('⚠️ Push subscription échouée:', err.message);
  }
}

async function requestAndSubscribe(registration) {
  if (!('Notification' in window) || !('PushManager' in window)) return;

  const permission = Notification.permission;

  if (permission === 'granted') {
    await subscribeToPush(registration);
  } else if (permission === 'default') {
    // Demander la permission — déclenché par l'utilisateur via bouton
    // On stocke la registration pour que le bouton puisse l'utiliser
    window._swRegistration = registration;
  }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', async function () {
    try {
      // Désinstaller l'ancien SW qui avait la mauvaise portée (/static/)
      const allRegs = await navigator.serviceWorker.getRegistrations();
      for (const reg of allRegs) {
        if (reg.scope && reg.scope.includes('/static')) {
          await reg.unregister();
          console.log('🗑️ Ancien service worker /static/ désinstallé');
        }
      }

      const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      console.log('✅ Service Worker enregistré avec succès:', registration.scope);

      // Vérifier les mises à jour périodiquement
      setInterval(() => registration.update(), 60000);

      // Tenter la souscription push
      await requestAndSubscribe(registration);

    } catch (error) {
      console.log('❌ Échec Service Worker:', error);
    }
  });

  navigator.serviceWorker.addEventListener('controllerchange', function () {
    console.log('🔄 Service Worker mis à jour');
  });
}

// Fonction globale appelée par le bouton "Activer les notifications" du dashboard
window.activerNotifications = async function () {
  if (!('Notification' in window)) {
    alert('Votre navigateur ne supporte pas les notifications.');
    return;
  }

  const permission = await Notification.requestPermission();

  if (permission === 'granted') {
    const reg = window._swRegistration ||
      (await navigator.serviceWorker.ready);
    await subscribeToPush(reg);
    // Mettre à jour le bouton
    const btn = document.getElementById('btn-notif');
    if (btn) {
      btn.textContent = '🔔 Notifications activées';
      btn.disabled = true;
      btn.style.opacity = '0.7';
    }
  } else {
    alert('Notifications refusées. Vous pouvez les activer dans les paramètres de votre navigateur.');
  }
};
