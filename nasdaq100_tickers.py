# 나스닥 100 종목 티커 리스트
# 2024-2025년 기준 주요 나스닥 100 구성 종목들

NASDAQ_100_TICKERS = [
    # 대형 기술주
    "AAPL",    # Apple Inc.
    "MSFT",    # Microsoft Corporation
    "GOOGL",   # Alphabet Inc. Class A
    "GOOG",    # Alphabet Inc. Class C
    "AMZN",    # Amazon.com Inc.
    "TSLA",    # Tesla Inc.
    "NVDA",    # NVIDIA Corporation
    "META",    # Meta Platforms Inc.
    
    # 반도체 및 기술
    "AVGO",    # Broadcom Inc.
    "ASML",    # ASML Holding N.V.
    "AMD",     # Advanced Micro Devices
    "INTC",    # Intel Corporation
    "QCOM",    # QUALCOMM Incorporated
    "TXN",     # Texas Instruments
    "AMAT",    # Applied Materials
    "LRCX",    # Lam Research Corporation
    "MRVL",    # Marvell Technology
    "KLAC",    # KLA Corporation
    "NXPI",    # NXP Semiconductors
    "MCHP",    # Microchip Technology
    "ADI",     # Analog Devices
    "MPWR",    # Monolithic Power Systems
    
    # 소프트웨어 및 서비스
    "ADBE",    # Adobe Inc.
    "CRM",     # Salesforce Inc.
    "ORCL",    # Oracle Corporation
    "NOW",     # ServiceNow Inc.
    "INTU",    # Intuit Inc.
    "TEAM",    # Atlassian Corporation
    "WDAY",    # Workday Inc.
    "PANW",    # Palo Alto Networks
    "CRWD",    # CrowdStrike Holdings
    "FTNT",    # Fortinet Inc.
    "DDOG",    # Datadog Inc.
    "ZS",      # Zscaler Inc.
    "OKTA",    # Okta Inc.
    "SNPS",    # Synopsys Inc.
    "CDNS",    # Cadence Design Systems
    "ANSS",    # ANSYS Inc.
    "ADSK",    # Autodesk Inc.
    
    # 통신 및 미디어
    "NFLX",    # Netflix Inc.
    "CMCSA",   # Comcast Corporation
    "TMUS",    # T-Mobile US Inc.
    "CHTR",    # Charter Communications
    "ROKU",    # Roku Inc.
    "ZM",      # Zoom Video Communications
    "DOCU",    # DocuSign Inc.
    
    # 전자상거래 및 소비재
    "COST",    # Costco Wholesale Corporation
    "ABNB",    # Airbnb Inc.
    "EBAY",    # eBay Inc.
    "BKNG",    # Booking Holdings Inc.
    "EXPD",    # Expeditors International
    "FAST",    # Fastenal Company
    "DLTR",    # Dollar Tree Inc.
    "KDP",     # Keurig Dr Pepper Inc.
    "MNST",    # Monster Beverage Corporation
    "PEP",     # PepsiCo Inc.
    "MDLZ",    # Mondelez International
    
    # 바이오테크 및 제약
    "GILD",    # Gilead Sciences Inc.
    "AMGN",    # Amgen Inc.
    "BIIB",    # Biogen Inc.
    "REGN",    # Regeneron Pharmaceuticals
    "VRTX",    # Vertex Pharmaceuticals
    "ILMN",    # Illumina Inc.
    "MRNA",    # Moderna Inc.
    "SGEN",    # Seagen Inc.
    
    # 기타 기술 및 산업
    "HON",     # Honeywell International
    "ADP",     # Automatic Data Processing
    "PAYX",    # Paychex Inc.
    "FISV",    # Fiserv Inc.
    "PYPL",    # PayPal Holdings Inc.
    "INTC",    # Intel Corporation (중복 제거됨)
    "CSCO",    # Cisco Systems Inc.
    "SBUX",    # Starbucks Corporation
    "LULU",    # Lululemon Athletica
    "ODFL",    # Old Dominion Freight Line
    "VRSK",    # Verisk Analytics Inc.
    "EXC",     # Exelon Corporation
    "XEL",     # Xcel Energy Inc.
    "CPRT",    # Copart Inc.
    "CTAS",    # Cintas Corporation
    "IDXX",    # IDEXX Laboratories
    "MELI",    # MercadoLibre Inc.
    "LCID",    # Lucid Group Inc.
    "RIVN",    # Rivian Automotive Inc.
    "COIN",    # Coinbase Global Inc.
    "HOOD",    # Robinhood Markets Inc.
    
    # 추가 주요 종목들
    "ISRG",    # Intuitive Surgical Inc.
    "LOGI",    # Logitech International
    "WBA",     # Walgreens Boots Alliance
    "SIRI",    # SiriusXM Holdings Inc.
    "FOXA",    # Fox Corporation Class A
    "FOX",     # Fox Corporation Class B
    "EA",      # Electronic Arts Inc.
    "ATVI",    # Activision Blizzard Inc.
    "NTES",    # NetEase Inc.
    "JD",      # JD.com Inc.
    "PDD",     # PDD Holdings Inc.
    "BIDU",    # Baidu Inc.
]

# 중복 제거
NASDAQ_100_TICKERS = list(set(NASDAQ_100_TICKERS))

# 알파벳 순 정렬
NASDAQ_100_TICKERS.sort()

print(f"총 나스닥 100 종목 수: {len(NASDAQ_100_TICKERS)}")
print("종목 리스트:", NASDAQ_100_TICKERS[:10], "... (처음 10개)") 