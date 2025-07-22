// Service Worker for 나스닥 100 PEG 분석 PWA
// 캐시 버전 및 60일 만료 기능 포함

const CACHE_NAME = 'nasdaq-peg-v1.0.0';
const CACHE_EXPIRY_DAYS = 60; // 60일 후 만료
const CACHE_EXPIRY_MS = CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000;

// 캐시할 리소스들
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/bull_logo.png',
  '/logo2.png',
  '/bnb.jpg'
];

// 설치 이벤트 - 초기 캐시 설정
self.addEventListener('install', (event) => {
  console.log('📦 Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('💾 캐시 파일들을 저장 중...');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // 설치 시간 저장 (60일 만료 체크용)
        const installTime = Date.now();
        return self.registration.sync?.register('saveInstallTime') || 
               localStorage.setItem('pwa-install-time', installTime.toString());
      })
      .then(() => {
        console.log('✅ PWA 설치 완료 - 60일간 사용 가능');
        return self.skipWaiting();
      })
  );
});

// 활성화 이벤트 - 오래된 캐시 정리
self.addEventListener('activate', (event) => {
  console.log('🔄 Service Worker 활성화 중...');
  
  event.waitUntil(
    Promise.all([
      // 오래된 캐시 삭제
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ 오래된 캐시 삭제:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // 클라이언트 제어 시작
      self.clients.claim(),
      // 만료 확인
      checkAppExpiry()
    ])
  );
});

// 네트워크 요청 가로채기 - 캐시 우선 전략
self.addEventListener('fetch', (event) => {
  // 먼저 만료 확인
  if (isAppExpired()) {
    event.respondWith(createExpiredResponse());
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 캐시에서 찾으면 반환, 없으면 네트워크에서 가져오기
        if (response) {
          console.log('📥 캐시에서 반환:', event.request.url);
          return response;
        }

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
            // 네트워크 실패 시 기본 오프라인 페이지 또는 캐시된 페이지 반환
            return caches.match('/index.html');
          });
      })
  );
});

// 60일 만료 확인 함수
function isAppExpired() {
  try {
    const installTimeStr = localStorage.getItem('pwa-install-time');
    if (!installTimeStr) {
      // 설치 시간이 없으면 현재 시간으로 설정
      localStorage.setItem('pwa-install-time', Date.now().toString());
      return false;
    }

    const installTime = parseInt(installTimeStr);
    const currentTime = Date.now();
    const timeDiff = currentTime - installTime;

    console.log(`⏰ PWA 사용 기간: ${Math.floor(timeDiff / (24 * 60 * 60 * 1000))}일`);

    return timeDiff > CACHE_EXPIRY_MS;
  } catch (error) {
    console.error('❌ 만료 확인 중 오류:', error);
    return false;
  }
}

// 앱 만료 확인 및 처리
async function checkAppExpiry() {
  if (isAppExpired()) {
    console.log('⚠️ PWA 사용 기간이 만료되었습니다 (60일)');
    
    // 캐시 삭제
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)));
    
    // 로컬 스토리지 정리
    localStorage.removeItem('pwa-install-time');
    
    // 클라이언트에게 만료 알림
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'APP_EXPIRED',
        message: 'PWA 사용 기간이 만료되었습니다. 새로운 버전을 다운로드해주세요.'
      });
    });
  }
}

// 만료된 앱에 대한 응답 생성
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
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px 20px;
                margin: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 400px;
            }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            p { font-size: 1.2em; line-height: 1.6; margin-bottom: 30px; }
            .btn {
                background: #007aff;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .btn:hover {
                background: #0051d5;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📅 앱 만료</h1>
            <p>60일 사용 기간이 만료되었습니다.<br>새로운 버전을 다운로드해주세요.</p>
            <a href="/" class="btn" onclick="window.location.reload()">새로 다운로드</a>
        </div>
    </body>
    </html>
  `;

  return new Response(expiredHTML, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache'
    }
  });
}

// 백그라운드 동기화 (설치 시간 저장)
self.addEventListener('sync', (event) => {
  if (event.tag === 'saveInstallTime') {
    event.waitUntil(
      (async () => {
        try {
          const installTime = Date.now();
          localStorage.setItem('pwa-install-time', installTime.toString());
          console.log('💾 PWA 설치 시간 저장 완료');
        } catch (error) {
          console.error('❌ 설치 시간 저장 실패:', error);
        }
      })()
    );
  }
});

// 푸시 알림 (선택사항)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '나스닥 100 PEG 분석 업데이트',
    icon: '/bull_logo.png',
    badge: '/bull_logo.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '분석 보기',
        icon: '/bull_logo.png'
      },
      {
        action: 'close',
        title: '닫기'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('나스닥 100 PEG 분석', options)
  );
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('🚀 Service Worker 로드 완료 - PWA 준비됨'); 