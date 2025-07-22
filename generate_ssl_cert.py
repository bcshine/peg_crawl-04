#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL 인증서 생성 스크립트
PWA HTTPS 서버용 자체 서명 인증서를 생성합니다.
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress

def generate_ssl_certificate():
    """자체 서명 SSL 인증서 생성"""
    
    print("🔐 SSL 인증서 생성 중...")
    
    # 1. RSA 개인키 생성
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # 2. 인증서 주체 정보
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "KR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Seoul"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Seoul"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NASDAQ PEG Analysis"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # 3. 인증서 생성
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # 1년간 유효
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("*.localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
            # 현재 로컬 IP도 추가
            x509.IPAddress(ipaddress.IPv4Address("14.33.80.107")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # 4. 인증서를 PEM 파일로 저장
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # 5. 개인키를 PEM 파일로 저장
    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print("✅ SSL 인증서 생성 완료!")
    print("   - cert.pem: 인증서 파일")
    print("   - key.pem: 개인키 파일")
    print("📱 이제 HTTPS로 PWA 서버를 실행할 수 있습니다.")

if __name__ == "__main__":
    try:
        generate_ssl_certificate()
    except ImportError:
        print("❌ cryptography 라이브러리가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install cryptography")
    except Exception as e:
        print(f"❌ SSL 인증서 생성 실패: {e}") 