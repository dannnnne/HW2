from fastapi import FastAPI, HTTPException
from app.schemas.payload import PredictRequest, PredictResponse, FeedbackRequest
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

@app.post("/feedback")
def collect_feedback(feedback: FeedbackRequest):
    """사용자의 피드백을 수집하여 모델 재학습 데이터로 활용합니다."""
    # 실제 프로덕션에서는 데이터베이스나 데이터 레이크(S3) 등에 저장합니다.
    # 현재는 로컬 파일(feedback.jsonl)에 저장하도록 구현합니다.
    import json
    from datetime import datetime
    
    feedback_file = os.path.join(os.path.dirname(__file__), "..", "feedback.jsonl")
    data = feedback.dict()
    data["timestamp"] = datetime.now().isoformat()
    
    try:
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        print(f"Feedback collected: {data['is_correct']} (Model update data)")
        return {"message": "정상적으로 의견이 수집되었습니다. 더 나은 AI를 만드는데 활용하겠습니다!"}
    except Exception as e:
        print(f"Feedback save error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

