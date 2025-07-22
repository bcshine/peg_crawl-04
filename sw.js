// 나스닥 100 PEG 분석 PWA - Service Worker
// 67일 만료 시스템 포함

const CACHE_NAME = 'nasdaq-peg-v1.2.0';
const USAGE_DAYS = 67; // 67일 사용 기간
const USAGE_MS = USAGE_DAYS * 24 * 60 * 60 * 1000;
const WARNING_DAYS = 7; // 7일 전 경고

// 캐시할 리소스 목록
const CACHE_URLS = [
  '/',
  '/bull_logo.png',
  '/logo2.png',
  '/bnb.jpg',
  '/manifest.json',
  '/index.html',
  '/?source=pwa',
  '/?shortcut=analysis'
];

// iOS 및 Android 호환성을 위한 추가 설정
const APP_SHELL_CACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/bull_logo.png'
];

// ==========================================
// Service Worker 설치
// ==========================================
self.addEventListener('install', (event) => {
  console.log('📦 Service Worker 설치 중...');
  
  event.waitUntil(
    (async () => {
      try {
        // 1. 앱 셸 리소스 캐싱 (중요 리소스, 빠른 로딩 필요)
        const appShellCache = await caches.open(CACHE_NAME + '-appshell');
        console.log('💾 앱 셸 캐시 저장 중...');
        await appShellCache.addAll(APP_SHELL_CACHE_URLS);
        
        // 2. 일반 리소스 캐싱
        const mainCache = await caches.open(CACHE_NAME);
        console.log('💾 일반 리소스 캐시 저장 중...');
        await mainCache.addAll(CACHE_URLS);
        
        // 3. 설치 시간 저장 (67일 만료 체크용)
        const installTime = Date.now().toString();
        const installTimeResponse = new Response(installTime);
        const infoCache = await caches.open('pwa-install-info');
        await infoCache.put('install-time', installTimeResponse);
        
        // 4. 설치 정보 저장 (네이티브 앱 설치 여부 확인용)
        const installInfoResponse = new Response(JSON.stringify({
          installTime: installTime,
          version: CACHE_NAME,
          isNative: true,
          platform: navigator.userAgent
        }));
        await infoCache.put('install-info', installInfoResponse);
        
        // 5. 알림 권한 확인 후 알림 표시
        if (self.Notification && self.Notification.permission === 'granted') {
          await self.registration.showNotification('나스닥 100 PEG 분석', {
            body: `네이티브 앱 설치 완료! ${USAGE_DAYS}일간 사용 가능합니다.`,
            icon: '/bull_logo.png',
            badge: '/bull_logo.png',
            tag: 'install-success',
            requireInteraction: false,
            data: { installTime }
          }).catch(err => {
            console.log('알림 표시 실패:', err);
          });
        }
        
        console.log('✅ 모든 캐시 및 설치 정보 저장 완료');
        return self.skipWaiting(); // 즉시 활성화
      } catch (error) {
        console.error('❌ Service Worker 설치 중 오류:', error);
        throw error;
      }
    })()
  );
});

// ==========================================
// Service Worker 활성화
// ==========================================
self.addEventListener('activate', (event) => {
  console.log('🔄 Service Worker 활성화 중...');
  
  event.waitUntil(
    (async () => {
      try {
        // 현재 캐시 이름 목록
        const currentCaches = [
          CACHE_NAME,
          CACHE_NAME + '-appshell',
          'pwa-install-info'
        ];
        
        // 모든 캐시 키 가져오기
        const cacheNames = await caches.keys();
        
        // 오래된 캐시 삭제
        const cacheDeletionPromises = cacheNames.map(cacheName => {
          // 현재 캐시 목록에 없는 캐시는 삭제
          if (!currentCaches.includes(cacheName)) {
            console.log('🗑️ 오래된 캐시 삭제:', cacheName);
            return caches.delete(cacheName);
          }
          return Promise.resolve();
        });
        
        await Promise.all(cacheDeletionPromises);
        console.log('✅ Service Worker 활성화 완료');
        
        // 모든 클라이언트에 대한 제어권 획득 (네이티브 앱 경험 향상)
        await self.clients.claim();
        
        // 활성화 후 모든 클라이언트에 메시지 전송
        const allClients = await self.clients.matchAll();
        allClients.forEach(client => {
          client.postMessage({
            type: 'SW_ACTIVATED',
            version: CACHE_NAME,
            isNative: true
          });
        });
        
        return true;
      } catch (error) {
        console.error('❌ Service Worker 활성화 중 오류:', error);
        throw error;
      }
    })()
  );
});

// ==========================================
// 네트워크 요청 처리 (캐시 우선 전략)
// ==========================================
self.addEventListener('fetch', (event) => {
  // 네비게이션 요청인지 확인 (HTML 페이지 요청)
  const isNavigationRequest = event.request.mode === 'navigate';
  
  // 앱 셸 리소스인지 확인 (중요 리소스)
  const isAppShellResource = APP_SHELL_CACHE_URLS.some(url => 
    event.request.url.endsWith(url) || 
    event.request.url.includes(url + '?')
  );
  
  // 67일 만료 체크
  event.respondWith(
    isExpired()
      .then(expired => {
        if (expired) {
          return createExpiredResponse();
        }
        
        // 네비게이션 요청이나 앱 셸 리소스는 캐시 우선 전략 사용
        if (isNavigationRequest || isAppShellResource) {
          return caches.match(event.request)
            .then((response) => {
              if (response) {
                console.log('💾 앱 셸/네비게이션 캐시에서 제공:', event.request.url);
                return response;
              }
              
              // 캐시에 없으면 네트워크에서 가져오고 캐시에 저장
              return fetch(event.request)
                .then((networkResponse) => {
                  // 유효한 응답인지 확인
                  if (!networkResponse || networkResponse.status !== 200) {
                    return networkResponse;
                  }
                  
                  // 응답을 캐시에 저장
                  const responseToCache = networkResponse.clone();
                  caches.open(CACHE_NAME)
                    .then((cache) => {
                      cache.put(event.request, responseToCache);
                    });
                  
                  return networkResponse;
                });
            });
        }
        
        // 일반 리소스는 네트워크 우선, 실패시 캐시 전략 사용
        return fetch(event.request)
          .then((response) => {
            // 유효한 응답인지 확인
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 응답을 캐시에 저장
            const responseToCache = response.clone();
                caches.open(CACHE_NAME)
                  .then((cache) => {
                    cache.put(event.request, responseToCache);
                  });

                return response;
              })
              .catch((error) => {
                console.log('🔴 네트워크 요청 실패:', error);
                
                // 네트워크 실패 시 캐시에서 찾기
                return caches.match(event.request).then(cachedResponse => {
                  if (cachedResponse) {
                    console.log('💾 오프라인 모드: 캐시에서 제공', event.request.url);
                    return cachedResponse;
                  }
                  
                  // 문서 요청인 경우 홈페이지 제공
                  if (event.request.destination === 'document') {
                    console.log('📄 오프라인 모드: 홈페이지 제공');
                    return caches.match('/');
                  }
                  
                  // 이미지인 경우 기본 이미지 제공
                  if (event.request.destination === 'image') {
                    return caches.match('/bull_logo.png');
                  }
                  
                  // 그 외의 경우 오류 응답
                  return new Response('네트워크 연결이 없습니다.', {
                    status: 503,
                    statusText: 'Service Unavailable',
                    headers: new Headers({
                      'Content-Type': 'text/plain'
                    })
                  });
                });
              });
          });
      })
  );
});

// ==========================================
// 67일 만료 체크 시스템
// ==========================================
function isExpired() {
  return caches.open('pwa-install-info')
    .then(cache => cache.match('install-time'))
    .then(response => {
      if (!response) {
        // 설치 시간이 없으면 지금 시간으로 설정
        const now = Date.now().toString();
        const installTimeResponse = new Response(now);
        caches.open('pwa-install-info')
          .then(cache => cache.put('install-time', installTimeResponse));
        return false;
      }
      
      return response.text()
        .then(installTime => {
          const elapsedTime = Date.now() - parseInt(installTime);
          return elapsedTime > USAGE_MS;
        });
    })
    .catch(() => false); // 오류 발생 시 만료되지 않은 것으로 처리
}

function createExpiredResponse() {
  const expiredHTML = `
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>앱 만료</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                margin: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 400px;
            }
            h1 { font-size: 2em; margin-bottom: 20px; }
            p { font-size: 1.1em; line-height: 1.6; margin-bottom: 30px; }
            .button {
                display: inline-block;
                padding: 15px 30px;
                background: #007aff;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: transform 0.2s;
            }
            .button:hover { transform: translateY(-2px); }
            .icon { font-size: 4em; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⏰</div>
            <h1>앱 사용 기간 만료</h1>
            <p>${USAGE_DAYS}일 사용 기간이 만료되었습니다.<br>
            새로운 버전을 다운로드해주세요!</p>
            <a href="/" class="button" onclick="clearExpiredData()">새로 다운로드</a>
        </div>
        
        <script>
            async function clearExpiredData() {
                // 만료된 데이터 정리
                localStorage.removeItem('pwa-install-time');
                
                // Cache Storage에서도 제거
                try {
                    const cache = await caches.open('pwa-install-info');
                    await cache.delete('install-time');
                } catch (err) {
                    console.error('Cache Storage 삭제 실패:', err);
                }
                
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(registrations => {
                        registrations.forEach(registration => registration.unregister());
                    });
                }
                window.location.reload();
            }
        </script>
    </body>
    </html>
  `;
  
  return new Response(expiredHTML, {
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  });
}

// ==========================================
// 만료 경고 시스템 (7일 전)
// ==========================================
function checkExpirationWarning() {
  caches.open('pwa-install-info')
    .then(cache => cache.match('install-time'))
    .then(response => {
      if (!response) return;
      
      return response.text()
        .then(installTime => {
          const elapsedTime = Date.now() - parseInt(installTime);
          const remainingTime = USAGE_MS - elapsedTime;
          const warningTime = WARNING_DAYS * 24 * 60 * 60 * 1000;

          if (remainingTime <= warningTime && remainingTime > 0) {
            const remainingDays = Math.ceil(remainingTime / (24 * 60 * 60 * 1000));
            
            // 알림 권한 확인 후 알림 표시
            if (self.Notification && self.Notification.permission === 'granted') {
              self.registration.showNotification('나스닥 100 PEG 분석', {
                body: `앱이 ${remainingDays}일 후 만료됩니다. 새 버전 준비를 해주세요.`,
                icon: '/bull_logo.png',
                badge: '/bull_logo.png',
                tag: 'expiration-warning',
                requireInteraction: true,
                actions: [
                  { action: 'dismiss', title: '확인' }
                ]
              }).catch(err => {
                console.log('만료 경고 알림 표시 실패:', err);
              });
            }
          }
        });
    })
    .catch(error => console.error('만료 경고 체크 오류:', error));
}

// 주기적으로 만료 경고 체크 (하루에 한 번)
setInterval(checkExpirationWarning, 24 * 60 * 60 * 1000);

// ==========================================
// 백그라운드 동기화
// ==========================================
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // 백그라운드에서 데이터 동기화 작업
      console.log('🔄 백그라운드 동기화 실행')
    );
  }
});

// ==========================================
// 푸시 알림 처리
// ==========================================
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '새로운 업데이트가 있습니다.',
    icon: '/bull_logo.png',
    badge: '/bull_logo.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    // 알림 권한 확인 후 알림 표시
    (async () => {
      try {
        if (self.Notification && self.Notification.permission === 'granted') {
          await self.registration.showNotification('나스닥 100 PEG 분석', options);
        }
      } catch (err) {
        console.log('푸시 알림 표시 실패:', err);
      }
    })()
  );
});

console.log('🚀 Service Worker 로드 완료 - 67일 사용 기간 시스템 활성화');