// 나스닥 100 PEG 분석 PWA - Service Worker
// GitHub Pages 호환성 및 안정성 개선

const CACHE_NAME = 'nasdaq-peg-v1.4.0'; // 캐시 버전 업데이트
const USAGE_DAYS = 67;

// 캐시할 핵심 리소스 목록 (상대 경로)
const CACHE_URLS = [
  './',
  './index.html',
  './bull_logo.png',
  './logo2.png',
  './bnb.jpg',
  './manifest.json'
];

// ==========================================
// Service Worker 설치
// ==========================================
self.addEventListener('install', (event) => {
  console.log(`📦 [SW v1.4.0] Service Worker 설치 중...`);
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('💾 캐시 파일들 저장 중...');
        return cache.addAll(CACHE_URLS);
      })
      .then(() => {
        console.log('✅ [SW v1.4.0] Service Worker 설치 완료');
        return self.skipWaiting(); // 즉시 활성화
      })
      .catch((error) => {
        console.error('❌ [SW v1.4.0] Service Worker 설치 실패:', error);
      })
  );
});

// ==========================================
// Service Worker 활성화
// ==========================================
self.addEventListener('activate', (event) => {
  console.log(`🔄 [SW v1.4.0] Service Worker 활성화 중...`);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 현재 버전이 아닌 모든 캐시 삭제
          if (cacheName !== CACHE_NAME) {
            console.log(`🗑️ [SW v1.4.0] 오래된 캐시 삭제:`, cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ [SW v1.4.0] Service Worker 활성화 완료');
      return self.clients.claim(); // 클라이언트 제어권 즉시 획득
    })
  );
});

// ==========================================
// 네트워크 요청 처리 (Stale-While-Revalidate 전략)
// ==========================================
self.addEventListener('fetch', (event) => {
  // HTML 페이지 요청에 대해서만 처리
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return fetch(event.request)
          .then((networkResponse) => {
            // 네트워크 응답을 캐시에 저장
            if (networkResponse.status === 200) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(() => {
            // 네트워크 실패 시 캐시에서 응답
            return cache.match(event.request);
          });
      })
    );
  } else if (CACHE_URLS.some(url => event.request.url.endsWith(url.substring(1)))) {
    // 기타 정적 리소스는 캐시 우선 전략 사용
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request).then((networkResponse) => {
          caches.open(CACHE_NAME).then((cache) => {
            if (networkResponse.status === 200) {
              cache.put(event.request, networkResponse.clone());
            }
          });
          return networkResponse;
        });
      })
    );
  }
});

// ==========================================
// 클라이언트 메시지 처리
// ==========================================
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CHECK_EXPIRATION') {
    checkExpiration(event.data.installTime);
  }
});

function checkExpiration(installTime) {
  if (!installTime) return;

  const usageMs = USAGE_DAYS * 24 * 60 * 60 * 1000;
  const elapsedTime = Date.now() - installTime;
  
  if (elapsedTime > usageMs) {
    // 만료된 경우 모든 클라이언트에 메시지 전송
    self.clients.matchAll().then(clients => {
      clients.forEach(client => client.postMessage({ type: 'APP_EXPIRED' }));
    });
  }
}

console.log('🚀 [SW v1.4.0] Service Worker 로드 완료');