// 나스닥 100 PEG 분석 PWA - Service Worker
// 기간 제한 없는 안정 버전

const CACHE_NAME = 'nasdaq-peg-v1.6.0'; // 캐시 버전 업데이트 (중요!)

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
// 1. 서비스 워커 설치
// ==========================================
self.addEventListener('install', (event) => {
  console.log(`[SW v1.6.0] 서비스 워커 설치 중...`);
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('💾 캐시 파일들을 저장하고 있습니다...');
        return cache.addAll(CACHE_URLS);
      })
      .then(() => {
        console.log('✅ [SW v1.6.0] 서비스 워커 설치 완료');
        return self.skipWaiting(); // 설치 즉시 활성화 되도록 설정
      })
      .catch((error) => {
        console.error('❌ [SW v1.6.0] 서비스 워커 설치에 실패했습니다:', error);
      })
  );
});

// ==========================================
// 2. 서비스 워커 활성화
// ==========================================
self.addEventListener('activate', (event) => {
  console.log(`🔄 [SW v1.6.0] 서비스 워커 활성화 중...`);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 현재 버전이 아닌 모든 이전 버전의 캐시를 삭제
          if (cacheName !== CACHE_NAME) {
            console.log(`🗑️ [SW v1.6.0] 오래된 캐시를 삭제합니다:`, cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ [SW v1.6.0] 서비스 워커 활성화 완료');
      return self.clients.claim(); // 클라이언트 제어권을 즉시 획득
    })
  );
});

// ==========================================
// 3. 네트워크 요청 처리 (캐시 우선 전략)
// ==========================================
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // 캐시에 응답이 있으면 즉시 반환
      if (cachedResponse) {
        return cachedResponse;
      }
      // 캐시에 없으면 네트워크에서 가져오기
      return fetch(event.request);
    })
  );
});

console.log('🚀 [SW v1.6.0] 서비스 워커 로드가 완료되었습니다.');