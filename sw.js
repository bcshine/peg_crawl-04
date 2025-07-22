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
  '/manifest.json'
];

// ==========================================
// Service Worker 설치
// ==========================================
self.addEventListener('install', (event) => {
  console.log('📦 Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('💾 캐시 파일들 저장 중...');
        return cache.addAll(CACHE_URLS);
      })
      .then(() => {
        // 설치 시간 저장 (67일 만료 체크용)
        const installTime = Date.now().toString();
        const installTimeResponse = new Response(installTime);
        return caches.open('pwa-install-info')
          .then(cache => cache.put('install-time', installTimeResponse))
          .then(() => {
            // 알림 권한 확인 후 알림 표시
            if (self.Notification && self.Notification.permission === 'granted') {
              return self.registration.showNotification('나스닥 100 PEG 분석', {
                body: `PWA 설치 완료! ${USAGE_DAYS}일간 사용 가능합니다.`,
                icon: '/bull_logo.png',
                badge: '/bull_logo.png',
                tag: 'install-success',
                requireInteraction: false,
                data: { installTime }
              }).catch(err => {
                console.log('알림 표시 실패:', err);
                return Promise.resolve(); // 오류가 발생해도 설치 진행
              });
            }
            return Promise.resolve(); // 권한이 없으면 알림 없이 진행
          });
      })
      .then(() => {
        console.log('✅ Service Worker 설치 완료');
        self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker 설치 실패:', error);
      })
  );
});

// ==========================================
// Service Worker 활성화
// ==========================================
self.addEventListener('activate', (event) => {
  console.log('🔄 Service Worker 활성화 중...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        // 오래된 캐시 삭제
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ 오래된 캐시 삭제:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker 활성화 완료');
        return self.clients.claim();
      })
  );
});

// ==========================================
// 네트워크 요청 처리 (캐시 우선 전략)
// ==========================================
self.addEventListener('fetch', (event) => {
  // 67일 만료 체크
  event.respondWith(
    isExpired()
      .then(expired => {
        if (expired) {
          return createExpiredResponse();
        }
        
        return caches.match(event.request)
          .then((response) => {
            // 캐시에서 찾으면 반환
            if (response) {
              console.log('💾 캐시에서 제공:', event.request.url);
              return response;
            }

            // 네트워크에서 가져오기
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
              .catch(() => {
                // 네트워크 실패 시 오프라인 페이지 제공
                if (event.request.destination === 'document') {
                  return caches.match('/');
                }
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