import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import ssl
import certifi
import os
import time
from nasdaq100_tickers import NASDAQ_100_TICKERS

# SSL 인증서 문제 해결을 위한 설정
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")

# 배치 크기 설정 (안전하게 5개씩)
BATCH_SIZE = 5
DELAY_BETWEEN_TICKERS = 2  # 각 종목 간 2초 대기
DELAY_BETWEEN_BATCHES = 5  # 배치 간 5초 대기

print(f"🎯 나스닥 100 실제 데이터 크롤링 시작")
print(f"📊 총 종목 수: {len(NASDAQ_100_TICKERS)}개")
print(f"🔄 배치 크기: {BATCH_SIZE}개씩")
print(f"⏱️  종목 간 대기: {DELAY_BETWEEN_TICKERS}초")
print(f"🔄 배치 간 대기: {DELAY_BETWEEN_BATCHES}초")
print("=" * 60)

# 결과를 저장할 리스트와 딕셔너리
results_list = []
all_stock_data = {}

# 통계
total_tickers = len(NASDAQ_100_TICKERS)
successful_count = 0
failed_count = 0
current_ticker_index = 0

# 배치별로 처리
for batch_start in range(0, total_tickers, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, total_tickers)
    batch_tickers = NASDAQ_100_TICKERS[batch_start:batch_end]
    batch_number = (batch_start // BATCH_SIZE) + 1
    total_batches = (total_tickers + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n🔄 배치 {batch_number}/{total_batches} 처리 중...")
    print(f"📋 종목: {', '.join(batch_tickers)}")
    
    for ticker in batch_tickers:
        current_ticker_index += 1
        try:
            print(f"\n[{current_ticker_index}/{total_tickers}] {ticker} 실제 데이터 수집 중...")
            
            # yfinance를 사용하여 실제 주식 정보 가져오기
            data = yf.Ticker(ticker)
            
            # 실제 데이터 요청 (재시도 로직 포함)
            info_data = {}
            for attempt in range(3):  # 최대 3번 시도
                try:
                    print(f"  📡 {ticker} 실제 데이터 요청 중... (시도 {attempt + 1}/3)")
                    info_data = data.info
                    if info_data and len(info_data) > 5:  # 최소한의 데이터가 있는지 확인
                        print(f"  ✅ {ticker} 실제 데이터 수신 성공!")
                        break
                    else:
                        print(f"  ⚠️ {ticker} 데이터 부족, 재시도...")
                        time.sleep(1)
                except Exception as e:
                    print(f"  ❌ {ticker} 데이터 요청 실패 (시도 {attempt + 1}): {e}")
                    if attempt < 2:  # 마지막 시도가 아니면 대기
                        time.sleep(2)
            
            # 실제 데이터가 있는 경우 처리
            if info_data and len(info_data) > 5:
                # 통계 딕셔너리에 실제 데이터 저장
                all_stock_data[ticker] = info_data
                
                # 필요한 실제 정보 추출
                company_name = info_data.get('longName', info_data.get('shortName', 'N/A'))
                sector = info_data.get('sector', 'N/A')
                industry = info_data.get('industry', 'N/A')
                current_price = info_data.get('currentPrice', None)
                trailing_pe = info_data.get('trailingPE', None)
                forward_pe = info_data.get('forwardPE', None)
                
                # 실제 PEG 비율 다중 소스 확인
                peg_ratio = info_data.get('trailingPegRatio', None)
                if peg_ratio is None:
                    peg_ratio = info_data.get('pegRatio', None)
                if peg_ratio is None:
                    peg_ratio = info_data.get('forwardPegRatio', None)
                if peg_ratio is None and trailing_pe is not None:
                    earnings_growth = info_data.get('earningsGrowth', None)
                    if earnings_growth is not None and earnings_growth > 0:
                        peg_ratio = trailing_pe / (earnings_growth * 100)
                
                # 산업군 정보 조합
                industry_info = f"{sector}"
                if industry != 'N/A' and industry != sector:
                    industry_info += f" - {industry}"
                
                # 실제 데이터 정보 출력
                print(f"  📊 {ticker} 실제 정보:")
                print(f"    종목명: {company_name}")
                print(f"    현재가: ${current_price}")
                print(f"    P/E: {trailing_pe}")
                print(f"    PEG: {peg_ratio}")
                
                # 유효한 실제 데이터만 저장
                if current_price is not None or trailing_pe is not None or peg_ratio is not None:
                    results_list.append({
                        "날짜": current_date,
                        "종목명": company_name,
                        "티커": ticker,
                        "산업군": industry_info,
                        "현재가격": current_price,
                        "Trailing P/E": trailing_pe,
                        "Forward P/E": forward_pe,
                        "PEG Ratio": peg_ratio
                    })
                    successful_count += 1
                    print(f"  ✅ {ticker} 실제 데이터 저장 완료")
                else:
                    print(f"  ⚠️ {ticker} 유효한 재무 데이터 없음")
            else:
                print(f"  ❌ {ticker} 실제 데이터 수집 실패")
                failed_count += 1
            
            # 종목 간 대기 (API 안정성)
            if current_ticker_index < total_tickers:
                print(f"  ⏱️  {DELAY_BETWEEN_TICKERS}초 대기...")
                time.sleep(DELAY_BETWEEN_TICKERS)
            
        except Exception as e:
            failed_count += 1
            print(f"  ❌ {ticker} 처리 오류: {e}")
            time.sleep(3)  # 오류 시 더 긴 대기
    
    # 배치 완료 후 대기
    if batch_end < total_tickers:
        print(f"\n🔄 배치 {batch_number} 완료. {DELAY_BETWEEN_BATCHES}초 대기 후 다음 배치...")
        time.sleep(DELAY_BETWEEN_BATCHES)

# 최종 실제 데이터 결과 요약
print(f"\n" + "=" * 60)
print(f"🎉 실제 데이터 크롤링 완료!")
print(f"✅ 성공: {successful_count}개 종목")
print(f"❌ 실패: {failed_count}개 종목")
print(f"📊 총 처리: {total_tickers}개 종목")
print(f"🎯 성공률: {(successful_count/total_tickers)*100:.1f}%")
print("=" * 60)

# 실제 데이터 DataFrame 생성
if results_list:
    results = pd.DataFrame(results_list)
    print(f"\n📊 수집된 실제 데이터: {len(results)}개 종목")
else:
    results = pd.DataFrame()
    print("\n❌ 수집된 실제 데이터가 없습니다.")

# 실제 데이터가 있는 경우 CSV 파일로 저장
if not results.empty:
    csv_filename = f"nasdaq100_real_data_{current_date}.csv"
    try:
        results.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n📄 실제 데이터가 '{csv_filename}' 파일에 저장되었습니다.")
    except PermissionError:
        import random
        csv_filename = f"nasdaq100_real_data_{current_date}_{random.randint(1000,9999)}.csv"
        results.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n📄 실제 데이터가 '{csv_filename}' 파일에 저장되었습니다.")
    
    # Top 5 PEG 종목 실제 데이터 표시
    if 'PEG Ratio' in results.columns:
        peg_column = 'PEG Ratio'
        peg_stocks = results[results[peg_column].notna()].sort_values(by=peg_column)
        if not peg_stocks.empty:
            print(f"\n🏆 실제 PEG 상위 5개 종목:")
            for i, (_, row) in enumerate(peg_stocks.head().iterrows(), 1):
                print(f"  {i}. {row['종목명']} ({row['티커']}): PEG {row[peg_column]:.3f}")

# 실제 데이터 통합 JSON 파일 저장
if all_stock_data:
    unified_json_filename = f"nasdaq100_real_unified_{current_date}.json"
    try:
        with open(unified_json_filename, "w", encoding='utf-8') as f:
            json.dump(all_stock_data, f, indent=2, ensure_ascii=False)
        print(f"\n📋 실제 데이터 통합 JSON이 '{unified_json_filename}' 파일에 저장되었습니다.")
        print(f"   - 실제 데이터 종목수: {len(all_stock_data)}개")
    except Exception as e:
        print(f"\n❌ JSON 파일 저장 실패: {e}")

print(f"\n�� 실제 데이터 크롤링 완료!") 