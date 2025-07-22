// 나스닥 100 PEG 분석 PWA - Service Worker
// 67일 만료 시스템 포함

const CACHE_NAME = 'nasdaq-peg-v1.3.0'; // 캐시 버전 업데이트
const USAGE_DAYS = 67; // 67일 사용 기간
const USAGE_MS = USAGE_DAYS * 24 * 60 * 60 * 1000;
const WARNING_DAYS = 7; // 7일 전 경고

// 캐시할 리소스 목록 (상대 경로로 수정)
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
  console.log('📦 Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('💾 캐시 파일들 저장 중...');
        return cache.addAll(CACHE_URLS);
      })
      .then(() => {
        // 설치 시간 저장 (67일 만료 체크용)
        const installTime = Date.now();
        // localStorage는 Service Worker에서 직접 접근 불가
        // indexedDB나 postMessage를 사용해야 하지만, 여기서는 클라이언트에서 처리하도록 단순화
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
// 네트워크 요청 처리 (Stale-While-Revalidate 전략)
// ==========================================
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          // 유효한 응답일 경우에만 캐시에 저장
          if (networkResponse && networkResponse.status === 200) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        });

        // 캐시된 응답이 있으면 즉시 반환하고, 네트워크에서 새로운 응답을 가져와 캐시를 업데이트
        return cachedResponse || fetchPromise;
      });
    })
  );
});

// ==========================================
// 클라이언트로부터 메시지 수신 (만료 시간 관리)
// ==========================================
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CHECK_EXPIRATION') {
    checkExpiration(event.data.installTime);
  }
});

function checkExpiration(installTime) {
  if (!installTime) return;

  const elapsedTime = Date.now() - installTime;
  const remainingTime = USAGE_MS - elapsedTime;

  if (remainingTime <= 0) {
    // 만료됨
    self.clients.matchAll().then(clients => {
      clients.forEach(client => client.postMessage({ type: 'APP_EXPIRED' }));
    });
  } else {
    // 만료 경고
    const warningTime = WARNING_DAYS * 24 * 60 * 60 * 1000;
    if (remainingTime <= warningTime) {
      const remainingDays = Math.ceil(remainingTime / (24 * 60 * 60 * 1000));
      self.registration.showNotification('나스닥 100 PEG 분석', {
        body: `앱이 ${remainingDays}일 후 만료됩니다. 새 버전 준비를 해주세요.`,
        icon: 'bull_logo.png',
        tag: 'expiration-warning'
      });
    }
  }
}

console.log('🚀 Service Worker 로드 완료 - v1.3.0');