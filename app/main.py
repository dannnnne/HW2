from fastapi import FastAPI, HTTPException
from app.schemas.payload import PredictRequest, PredictResponse
from app.ml.model import spam_model
import time

app = FastAPI(
    title="Phishing/Spam Detection API",
    description="실시간 피싱/스팸 탐지를 위한 ML 모델 서빙 API",
    version="1.0.0"
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 프론트엔드 정적 파일 경로 마운트 설정
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    # 사용자가 접속하면 웹 UI를 반환합니다.
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
def health_check():
    """Liveness & Readiness 헬스 체크 엔드포인트"""
    if spam_model.is_loaded:
        return {"status": "healthy", "model_loaded": True}
    raise HTTPException(status_code=503, detail="Model is not loaded")

@app.post("/predict", response_model=PredictResponse)
def predict_spam(request: PredictRequest):
    """입력된 텍스트의 피싱/스팸 여부를 예측합니다."""
    start_time = time.time()
    
    try:
        is_spam, confidence = spam_model.predict(request.text)
        
        # MLOps 관점: 모델 서빙 레이턴시 및 결과 로깅 (후에 데이터 드리프트 모니터링 등에 활용)
        process_time = time.time() - start_time
        print(f"Prediction in {process_time:.4f}s | is_spam={is_spam} | conf={confidence:.4f} | text='{request.text[:20]}...'")
        
        if is_spam:
            message = "Warning: Phishing/Spam content detected!"
        else:
            message = "This content appears to be safe."
            
        return PredictResponse(
            is_spam=is_spam,
            confidence=confidence,
            message=message
        )
    except Exception as e:
        # MLOps 관점: 예측 실패시 얼럿 트리거를 위해 로깅하고 명확한 HTTP 상태 코드를 반환합니다.
        print(f"Prediction Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal prediction engine error")
