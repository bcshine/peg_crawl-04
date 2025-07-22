import pandas as pd
import json
from datetime import datetime, timezone, timedelta
import os
import re

def update_index_html():
    """CSV 파일에서 주식 데이터를 읽어 index.html의 JavaScript 데이터를 업데이트"""
    
    # 현재 날짜
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # CSV 파일 읽기 (실제 데이터 파일 우선 검색)
    csv_filename = f"nasdaq100_real_data_{current_date}.csv"
    
    # 실제 데이터 파일이 없으면 기존 나스닥 100 파일 검색
    if not os.path.exists(csv_filename):
        csv_filename = f"nasdaq100_pe_peg_{current_date}.csv"
        
    # 그것도 없으면 기존 파일 검색
    if not os.path.exists(csv_filename):
        csv_filename = f"stock_pe_peg_{current_date}.csv"
    
    try:
        df = pd.read_csv(csv_filename, encoding='utf-8-sig')
        print(f"✅ CSV 파일 '{csv_filename}'을 성공적으로 읽었습니다.")
    except FileNotFoundError:
        print(f"❌ CSV 파일 '{csv_filename}'을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"❌ CSV 파일 읽기 오류: {e}")
        return
    
    # 데이터가 비어있는 경우 확인
    if df.empty:
        print("❌ CSV 파일에 데이터가 없습니다.")
        return
    
    # JavaScript 형태의 데이터 배열 생성
    js_data = convert_to_js_data(df, current_date)
    
    # index.html 업데이트
    update_index_html_file(js_data, current_date)

def convert_to_js_data(df, current_date):
    """DataFrame을 JavaScript STOCK_DATA 배열 형태로 변환"""
    js_lines = []
    js_lines.append(f"        // =============================================")
    js_lines.append(f"        // 주식 데이터 모델 ({current_date} 최신 업데이트)")
    js_lines.append(f"        // =============================================")
    js_lines.append(f"        const STOCK_DATA = [")
    
    for _, row in df.iterrows():
        # 값들을 안전하게 변환
        company = str(row.get('종목명', '')).replace('"', '\\"')
        ticker = str(row.get('티커', ''))
        
        # 산업군 정보 간소화 (간단한 축약만)
        industry_full = str(row.get('산업군', ''))
        if ' - ' in industry_full:
            # 마지막 부분만 사용하되, 너무 길면 축약
            industry_parts = industry_full.split(' - ')
            last_part = industry_parts[-1]
            if len(last_part) > 15:
                industry_short = last_part[:12] + '...'
            else:
                industry_short = last_part
        else:
            industry_short = industry_full[:15] if len(industry_full) > 15 else industry_full
        
        industry = industry_short.replace('"', '\\"')
        
        # 숫자 값들 처리 (null 또는 빈 값을 null로 변환)
        def safe_float(value):
            if pd.isna(value) or str(value).strip() == '' or str(value).strip() == 'N/A':
                return 'null'
            try:
                return str(float(value))
            except:
                return 'null'
        
        peg = safe_float(row.get('PEG Ratio', ''))
        trail_pe = safe_float(row.get('Trailing P/E', ''))
        fwd_pe = safe_float(row.get('Forward P/E', ''))
        price = safe_float(row.get('현재가격', ''))
        
        js_line = f'            {{company: "{company}", ticker: "{ticker}", industry: "{industry}", peg: {peg}, trailPE: {trail_pe}, fwdPE: {fwd_pe}, price: {price}}},'
        js_lines.append(js_line)
    
    js_lines.append("        ];")
    
    return '\n'.join(js_lines)

def update_index_html_file(js_data, current_date):
    """index.html 파일의 JavaScript 데이터 부분을 업데이트"""
    try:
        # index.html 파일 읽기
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # JavaScript 데이터 부분 찾기 및 교체
        pattern = r'(        // =============================================\s*\n        // 주식 데이터 모델.*?\n        // =============================================\s*\n        const STOCK_DATA = \[.*?\];)'
        
        if re.search(pattern, html_content, re.DOTALL):
            # 기존 데이터 교체
            html_content = re.sub(pattern, js_data, html_content, flags=re.DOTALL)
        else:
            print("❌ index.html에서 STOCK_DATA 섹션을 찾을 수 없습니다.")
            return
        
        # 업데이트 시간 정보도 변경
        current_date_kr = current_date.replace('-', '.')
        
        # 헤더 업데이트 시간 변경
        html_content = re.sub(
            r'Updated: \d{4}\.\d{2}\.\d{2}[^•]*•',
            f'Updated: {current_date_kr} 최신 크롤링 •',
            html_content
        )
        
        # 푸터 업데이트 시간 변경
        html_content = re.sub(
            r'Data updated: \d{4}\.\d{2}\.\d{2}[^•]*•',
            f'Data updated: {current_date_kr} 최신 크롤링 •',
            html_content
        )
        
        # 수정된 내용을 index.html에 저장
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🎉 index.html이 성공적으로 업데이트되었습니다!")
        print(f"📅 업데이트 날짜: {current_date_kr}")
        
    except Exception as e:
        print(f"❌ index.html 업데이트 오류: {e}")

def generate_peg_analysis_webpage():
    """CSV 파일에서 주식 데이터를 읽어 PEG 분석 웹페이지를 생성"""
    
    # 현재 날짜
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # CSV 파일 읽기 (실제 데이터 파일 우선 검색)
    csv_filename = f"nasdaq100_real_data_{current_date}.csv"
    
    # 실제 데이터 파일이 없으면 기존 나스닥 100 파일 검색
    if not os.path.exists(csv_filename):
        csv_filename = f"nasdaq100_pe_peg_{current_date}.csv"
        
    # 그것도 없으면 기존 파일 검색
    if not os.path.exists(csv_filename):
        csv_filename = f"stock_pe_peg_{current_date}.csv"
    
    try:
        df = pd.read_csv(csv_filename, encoding='utf-8-sig')
        print(f"CSV 파일 '{csv_filename}'을 성공적으로 읽었습니다.")
    except FileNotFoundError:
        print(f"CSV 파일 '{csv_filename}'을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"CSV 파일 읽기 오류: {e}")
        return
    
    # 데이터가 비어있는 경우 확인
    if df.empty:
        print("CSV 파일에 데이터가 없습니다.")
        return
    
    # HTML 생성
    html_content = generate_html_content(df, current_date)
    
    # HTML 파일 저장
    html_filename = f"nasdaq100_real_peg_analysis_{current_date}.html"
    
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"웹페이지 '{html_filename}'이 성공적으로 생성되었습니다.")
        print(f"브라우저에서 파일을 열어 확인하세요!")
    except Exception as e:
        print(f"HTML 파일 저장 오류: {e}")

def get_peg_color_class(peg_value):
    """PEG 값에 따른 CSS 클래스 반환"""
    try:
        peg = float(peg_value)
        if peg < 1.0:
            return "peg-good"  # 파란색
        elif peg <= 2.0:
            return "peg-moderate"  # 노란색
        else:
            return "peg-high"  # 빨간색
    except (ValueError, TypeError):
        return "peg-na"  # 데이터가 없는 경우

def get_kst_time():
    """한국 표준시(KST) 현재 시간 반환"""
    kst_timezone = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst_timezone)
    return now_kst.strftime("%Y년 %m월 %d일 %H:%M KST")

def generate_html_content(df, date):
    """HTML 콘텐츠 생성"""
    
    # 테이블 행 생성
    table_rows = ""
    for _, row in df.iterrows():
        peg_class = get_peg_color_class(row['PEG Ratio'])
        
        # 산업군 정보 간소화 (뒤쪽 키워드만 사용)
        industry_full = row['산업군']
        if ' - ' in industry_full:
            industry_short = industry_full.split(' - ', 1)[1]  # 첫 번째 ' - ' 뒤의 부분만 사용
        else:
            industry_short = industry_full
        
        # 숫자 포매팅
        current_price = f"${row['현재가격']:.2f}" if pd.notna(row['현재가격']) else "N/A"
        trailing_pe = f"{row['Trailing P/E']:.2f}" if pd.notna(row['Trailing P/E']) else "N/A"
        forward_pe = f"{row['Forward P/E']:.2f}" if pd.notna(row['Forward P/E']) else "N/A"
        
        # PEG 비율 특별 포매팅 (소수점 2자리 또는 3자리로 적절히)
        if pd.notna(row['PEG Ratio']):
            peg_val = row['PEG Ratio']
            if peg_val < 1:
                peg_ratio = f"{peg_val:.3f}"  # 1 미만은 소수점 3자리
            else:
                peg_ratio = f"{peg_val:.2f}"  # 1 이상은 소수점 2자리
        else:
            peg_ratio = "N/A"
        
        table_rows += f"""
        <tr>
            <td>{row['종목명']}</td>
            <td class="ticker">{row['티커']}</td>
            <td class="industry">{industry_short}</td>
            <td class="price">{current_price}</td>
            <td class="pe-ratio">{trailing_pe}</td>
            <td class="pe-ratio">{forward_pe}</td>
            <td class="peg-ratio {peg_class}">{peg_ratio}</td>
        </tr>
        """
    
    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>나스닥 100 주요 종목 분석 (PEG)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .update-info {{
            background: transparent !important;
            color: rgba(255, 255, 255, 0.8);
            padding: 15px 20px;
            margin-top: 20px;
            text-align: center;
            font-size: 0.8em;
            line-height: 1.6;
        }}
        
        .update-info * {{
            background: transparent !important;
        }}
        
        .update-main {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}
        
        .update-badge {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.65em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
        }}
        
        .update-time {{
            font-weight: 600;
            color: white;
            background: transparent;
            font-size: 0.9em;
        }}
        
        .update-schedule {{
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
            font-size: 0.85em;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 6px;
        }}
        
        .schedule-icon {{
            font-size: 0.9em;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .legend {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .legend h3 {{
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .legend-items {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
                 .legend-color {{
             width: 20px;
             height: 20px;
             border-radius: 4px;
             border: 2px solid #ddd;
         }}
         
         .data-disclaimer {{
             margin-top: 15px;
             padding: 12px;
             background: #fff3cd;
             border: 1px solid #ffeaa7;
             border-radius: 6px;
             font-size: 0.9em;
         }}
         
         .data-disclaimer p {{
             margin: 0;
             color: #856404;
         }}
        
                 .table-wrapper {{
             padding: 30px;
             border-radius: 8px;
             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
             background: white;
         }}
         
         .table-container {{
             width: 100%;
             overflow-x: auto;
             overflow-y: visible;
             -webkit-overflow-scrolling: touch;
             border-radius: 8px;
             border: 1px solid #dee2e6;
         }}
         
         .table-header {{
             position: sticky;
             top: 0;
             z-index: 1000;
             background: white;
             border-radius: 8px 8px 0 0;
             overflow: hidden;
         }}
         
         .table-header table {{
             margin: 0;
             border-radius: 8px 8px 0 0;
         }}
         
         .table-body-container {{
             height: 60vh;
             overflow-y: auto;
             overflow-x: visible;
             border-radius: 0 0 8px 8px;
         }}
         
         table {{
             width: 100%;
             border-collapse: separate;
             border-spacing: 0;
             background: white;
             min-width: 1200px;
         }}
         
         /* 컬럼 넓이 최적화 */
         th:nth-child(1), td:nth-child(1) {{ width: 20%; }}  /* 종목명 */
         th:nth-child(2), td:nth-child(2) {{ width: 8%; }}   /* 티커 */
         th:nth-child(3), td:nth-child(3) {{ width: 25%; }}  /* 산업군 */
         th:nth-child(4), td:nth-child(4) {{ width: 12%; }}  /* 현재가격 */
         th:nth-child(5), td:nth-child(5) {{ width: 12%; }}  /* Trail P/E */
         th:nth-child(6), td:nth-child(6) {{ width: 12%; }}  /* For P/E */
         th:nth-child(7), td:nth-child(7) {{ width: 11%; }}  /* PEG */
          
         th {{
             background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
             color: white;
             padding: 15px 10px;
             text-align: left;
             font-weight: 600;
             cursor: pointer;
             transition: background 0.3s ease;
             user-select: none;
             border: none;
             position: relative;
         }}
         
         th:first-child {{
             border-top-left-radius: 8px;
         }}
         
         th:last-child {{
             border-top-right-radius: 8px;
         }}
        
        th:hover {{
            background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
        }}
        
        th::after {{
            content: '↕️';
            position: absolute;
            right: 8px;
            font-size: 0.8em;
        }}
        
        th.sort-asc::after {{
            content: '🔼';
        }}
        
        th.sort-desc::after {{
            content: '🔽';
        }}
        
                 tbody {{
             background: white;
         }}
         
         td {{
             padding: 12px 10px;
             border-bottom: 1px solid #eee;
             transition: background 0.2s ease;
             background: white;
         }}
         
         tbody tr:hover td {{
             background: #f8f9fa !important;
         }}
         
         tbody tr:nth-child(even) td {{
             background: #fafafa;
         }}
         
         tbody tr:nth-child(even):hover td {{
             background: #f0f0f0 !important;
         }}
        
                 .ticker {{
             font-weight: bold;
             color: #2c3e50;
             text-align: center;
         }}
         
         .industry {{
             font-size: 0.9em;
             color: #5a6c7d;
             text-align: left;
         }}
         
         .price {{
             font-weight: bold;
             color: #27ae60;
             text-align: right;
         }}
        
        .pe-ratio {{
            text-align: right;
        }}
        
        .peg-ratio {{
            text-align: right;
            font-weight: bold;
            border-radius: 4px;
            padding: 4px 8px;
        }}
        
        .peg-good {{
            background: #e3f2fd;
            color: #1976d2;
            border: 1px solid #bbdefb;
        }}
        
        .peg-moderate {{
            background: #fffbf0;
            color: #f57f17;
            border: 1px solid #ffe082;
        }}
        
        .peg-high {{
            background: #ffebee;
            color: #d32f2f;
            border: 1px solid #ffcdd2;
        }}
        
        .peg-na {{
            background: #f5f5f5;
            color: #757575;
        }}
        
        .update-time {{
            text-align: center;
            padding: 20px;
            color: #666;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }}
        
                 @media (max-width: 768px) {{
             .header h1 {{
                 font-size: 1.8em;
             }}
             
             .legend-items {{
                 flex-direction: column;
                 gap: 15px;
             }}
             
             .table-wrapper {{
                 padding: 15px;
             }}
             
             .table-container {{
                 border-radius: 6px;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
             }}
             
             table {{
                 min-width: 1000px;
             }}
             
             th, td {{
                 padding: 8px 6px;
                 font-size: 0.8em;
                 white-space: nowrap;
             }}
             
             /* 모바일에서 컬럼 넓이 재조정 */
             th:nth-child(1), td:nth-child(1) {{ min-width: 180px; }}  /* 종목명 */
             th:nth-child(2), td:nth-child(2) {{ min-width: 80px; }}   /* 티커 */
             th:nth-child(3), td:nth-child(3) {{ min-width: 150px; }}  /* 산업군 */
             th:nth-child(4), td:nth-child(4) {{ min-width: 100px; }}  /* 현재가격 */
             th:nth-child(5), td:nth-child(5) {{ min-width: 100px; }}  /* Trail P/E */
             th:nth-child(6), td:nth-child(6) {{ min-width: 100px; }}  /* For P/E */
             th:nth-child(7), td:nth-child(7) {{ min-width: 100px; }}  /* PEG */
             
             .industry {{
                 font-size: 0.75em;
             }}
             
             /* 업데이트 정보 모바일 최적화 */
             .update-info {{
                 padding: 12px 15px;
                 margin-top: 15px;
                 font-size: 0.75em;
             }}
             
             .update-main {{
                 flex-direction: column;
                 gap: 6px;
                 margin-bottom: 10px;
             }}
             
             .update-badge {{
                 font-size: 0.6em;
                 margin-bottom: 4px;
             }}
             
             .update-schedule {{
                 font-size: 0.7em;
             }}
             
             .scroll-hint {{
                 text-align: center;
                 padding: 10px;
                 font-size: 0.85em;
                 color: #666;
                 background: #f8f9fa;
                 border-top: 1px solid #dee2e6;
                 margin-top: 5px;
             }}
         }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 나스닥 100 주요 종목 분석 (PEG)</h1>
            <p>주요 기술주의 P/E 및 PEG 비율 분석 리포트</p>
            <div class="update-info">
                <div class="update-main">
                    <span class="update-badge">LIVE</span>
                    <span>마지막 업데이트:</span>
                    <span class="update-time">{get_kst_time()}</span>
                </div>
                <div class="update-schedule">
                    <span class="schedule-icon">⏰</span>
                    <span>매일 오전 9시 자동 업데이트</span>
                </div>
            </div>
        </div>
        
        <div class="legend">
            <h3>🎯 PEG 비율 해석 가이드</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color peg-good"></div>
                    <span><strong>1.0 미만</strong> - 저평가 (양호)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color peg-moderate"></div>
                    <span><strong>1.0 ~ 2.0</strong> - 적정 평가 (보통)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color peg-high"></div>
                    <span><strong>2.0 이상</strong> - 고평가 (주의)</span>
                </div>
            </div>
            <div class="data-disclaimer">
                <p><strong>⚠️ 데이터 안내:</strong> 이곳의 데이터는 수집방법에 따라 차이가 있습니다. 구체적인 정보는 증권앱에서 확인하십시오.</p>
            </div>
        </div>
        
                 <div class="table-wrapper">
             <div class="table-container">
                 <div class="table-header">
                     <table>
                         <thead>
                             <tr>
                                 <th onclick="sortTable(0)">종목명</th>
                                 <th onclick="sortTable(1)">티커</th>
                                 <th onclick="sortTable(2)">산업군</th>
                                 <th onclick="sortTable(3)">현재가격</th>
                                 <th onclick="sortTable(4)">Trail P/E</th>
                                 <th onclick="sortTable(5)">For P/E</th>
                                 <th onclick="sortTable(6)">PEG</th>
                             </tr>
                         </thead>
                     </table>
                 </div>
                 <div class="table-body-container">
                     <table id="stockTable">
                         <tbody>
                             {table_rows}
                         </tbody>
                     </table>
                 </div>
             </div>
             <div class="scroll-hint">
                 👈👉 테이블을 좌우로 스크롤하여 모든 데이터를 확인하세요
             </div>
         </div>
        
        <div class="update-time">
            <p>📅 업데이트: {date} | 📊 데이터 출처: Yahoo Finance</p>
        </div>
    </div>

         <script>
         let sortDirection = {{}};
         
         function sortTable(columnIndex) {{
             const bodyTable = document.getElementById('stockTable');
             const tbody = bodyTable.getElementsByTagName('tbody')[0];
             const rows = Array.from(tbody.getElementsByTagName('tr'));
             const headerTable = document.querySelector('.table-header table');
             const headers = headerTable.getElementsByTagName('th');
             
             // 정렬 방향 토글
             const currentDirection = sortDirection[columnIndex] || 'asc';
             const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
             sortDirection[columnIndex] = newDirection;
             
             // 모든 헤더에서 정렬 클래스 제거
             for (let header of headers) {{
                 header.classList.remove('sort-asc', 'sort-desc');
             }}
             
             // 현재 헤더에 정렬 클래스 추가
             headers[columnIndex].classList.add(`sort-${{newDirection}}`);
             
             // 행 정렬
             rows.sort((a, b) => {{
                 const aValue = a.getElementsByTagName('td')[columnIndex].textContent.trim();
                 const bValue = b.getElementsByTagName('td')[columnIndex].textContent.trim();
                 
                 // 숫자 컬럼 처리 (가격, P/E, PEG)
                 if (columnIndex >= 3) {{
                     const aNum = parseFloat(aValue.replace(/[$,]/g, '')) || 0;
                     const bNum = parseFloat(bValue.replace(/[$,]/g, '')) || 0;
                     
                     if (newDirection === 'asc') {{
                         return aNum - bNum;
                     }} else {{
                         return bNum - aNum;
                     }}
                 }}
                 
                 // 텍스트 컬럼 처리
                 if (newDirection === 'asc') {{
                     return aValue.localeCompare(bValue, 'ko');
                 }} else {{
                     return bValue.localeCompare(aValue, 'ko');
                 }}
             }});
             
             // 정렬된 행들을 테이블에 다시 추가
             rows.forEach(row => tbody.appendChild(row));
         }}
         
         // 페이지 로드 시 PEG 기준으로 기본 정렬
         document.addEventListener('DOMContentLoaded', function() {{
             sortTable(6); // PEG 컬럼 기준 정렬
         }});
     </script>
</body>
</html>
    """
    
    return html_template

if __name__ == "__main__":
    # 간소화된 워크플로우: index.html을 직접 업데이트
    update_index_html() 