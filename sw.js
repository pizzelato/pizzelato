/* ════════════════════════════════════════════════
   PIZZELATO — Service Worker
   Versão: 1.0.0
   Responsabilidades:
   • Cache de assets para funcionar offline
   • Notificações push em segundo plano
   • Sincronização ao voltar online
   ════════════════════════════════════════════════ */

const SW_VERSION = '1.0.0';
const CACHE_NAME = 'pizzelato-v1';

// Assets para cache offline (apenas os essenciais)
const CACHE_ASSETS = [
  './',
  './index.html',
  'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap'
];

// ── INSTALL: cacheia assets essenciais ──
self.addEventListener('install', event => {
  console.log('[SW] Instalando versão', SW_VERSION);
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return Promise.allSettled(
          CACHE_ASSETS.map(url => cache.add(url).catch(() => {}))
        );
      })
      .then(() => self.skipWaiting()) // ativa imediatamente sem esperar reload
  );
});

// ── ACTIVATE: limpa caches antigos ──
self.addEventListener('activate', event => {
  console.log('[SW] Ativando versão', SW_VERSION);
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => {
            console.log('[SW] Removendo cache antigo:', key);
            return caches.delete(key);
          })
      )
    ).then(() => self.clients.claim()) // assume controle de todas as abas
  );
});

// ── FETCH: estratégia Network First com fallback de cache ──
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ignora requests do Firebase (sempre precisam de rede)
  if (
    url.hostname.includes('firebase') ||
    url.hostname.includes('googleapis.com') ||
    url.hostname.includes('anthropic.com') ||
    event.request.method !== 'GET'
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Atualiza cache com resposta fresca
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        // Sem rede — retorna do cache
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          // Fallback para index.html em rotas desconhecidas
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html');
          }
        });
      })
  );
});

// ── PUSH: recebe notificações do servidor ──
self.addEventListener('push', event => {
  let data = { title: '🍕 Pizzelato', body: 'Nova notificação', tag: 'pizzelato' };

  try {
    if (event.data) data = { ...data, ...event.data.json() };
  } catch (e) {}

  const options = {
    body: data.body,
    icon: data.icon || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🍕</text></svg>',
    badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🍕</text></svg>',
    tag: data.tag || 'pizzelato',
    requireInteraction: true,
    vibrate: [300, 100, 300, 100, 300],
    actions: [
      { action: 'ver', title: '👀 Ver Pedido' },
      { action: 'fechar', title: '✕ Fechar' }
    ],
    data: data
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// ── NOTIFICATIONCLICK: abre o app na página certa ──
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'fechar') return;

  // Determina para qual página navegar
  const targetPage = event.notification.data?.page || 'entregas';
  const targetUrl = './?page=' + targetPage;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Se o app já está aberto, foca e navega
        for (const client of clientList) {
          if (client.url.includes('pizzelato') || client.url.includes('index.html') || client.url.endsWith('/')) {
            client.focus();
            client.postMessage({ type: 'NAVIGATE', page: targetPage });
            return;
          }
        }
        // App fechado — abre uma nova janela
        return clients.openWindow(targetUrl);
      })
  );
});

// ── MESSAGE: recebe mensagens do app principal ──
self.addEventListener('message', event => {
  if (!event.data) return;

  switch (event.data.type) {

    // App pedindo para exibir notificação via SW (funciona com browser fechado)
    case 'SHOW_NOTIFICATION':
      const { title, body, tag, page } = event.data;
      self.registration.showNotification(title || '🛵 Novo Pedido!', {
        body: body || 'Toque para ver',
        icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🍕</text></svg>',
        badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🍕</text></svg>',
        tag: tag || 'pedido-' + Date.now(),
        requireInteraction: true,
        vibrate: [300, 100, 300, 100, 300],
        data: { page: page || 'entregas' },
        actions: [
          { action: 'ver', title: '👀 Ver Pedido' },
          { action: 'fechar', title: '✕ Fechar' }
        ]
      });
      break;

    // App pedindo para limpar notificações antigas
    case 'CLEAR_NOTIFICATIONS':
      self.registration.getNotifications().then(notifs => {
        notifs.forEach(n => n.close());
      });
      break;

    // Verificar versão do SW
    case 'GET_VERSION':
      event.source?.postMessage({ type: 'SW_VERSION', version: SW_VERSION });
      break;
  }
});

// ── SYNC: executa tarefas quando volta online ──
self.addEventListener('sync', event => {
  if (event.tag === 'sync-pedidos') {
    console.log('[SW] Background sync: pedidos');
    // Firebase já faz sync automático via onSnapshot
    // Esta tag é para futuras implementações
  }
});

console.log('[SW] Pizzelato Service Worker', SW_VERSION, 'carregado');
