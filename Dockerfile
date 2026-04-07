# 1. 빌드 스테이지 (의존성 패키지 설치용)
FROM python:3.11-slim as builder

WORKDIR /app

# c++ 컴파일러 등 의존성 설치 (scikit-learn 등 일부 패키지 요구사항 대비)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 가상 환경 생성 (최종 이미지 크기 축소를 위해 활용)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# 2. 실행 스테이지 (최종 경량화 이미지)
FROM python:3.11-slim

# 캐시 및 파이썬 출력 최적화
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 헬스체크용 wget 설치 후 apt 캐시 삭제로 용량 최적화
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 설치된 가상환경 통째로 복사 (이로 인해 빌드 도구들은 제외됨)
COPY --from=builder /opt/venv /opt/venv

# 애플리케이션 코드 복사
COPY ./app ./app

# 권한 설정: 보안을 위해 root가 아닌 일반 사용자로 실행
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Docker Healthcheck (FastAPI에서 만들어둔 /health 엔드포인트 활용)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
