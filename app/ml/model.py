import random

class SpamDetectionModel:
    def __init__(self):
        # 실제 환경에서는 여기서 학습된 모델 파일(.pkl, .onnx 등)을 로드합니다.
        # MLOps 관점에서는 모델 레지스트리(MLflow, BentoML)에서 다운로드 받거나 마운트된 볼륨에서 읽도록 설정합니다.
        self.is_loaded = True
        
    def predict(self, text: str) -> tuple[bool, float]:
        # 실제 모델 추론 로직 (더미 로직)
        spam_keywords = ["당첨", "무료", "대출", "클릭", "특가", "password", "bank", "urgent"]
        
        is_spam = any(keyword.lower() in text.lower() for keyword in spam_keywords)
        
        if is_spam:
            confidence = random.uniform(0.7, 0.99)
        else:
            confidence = random.uniform(0.5, 0.99)
            is_spam = random.random() > 0.95 # 약간의 False Positive 시뮬레이션
            if not is_spam:
                confidence = random.uniform(0.8, 0.99)
                
        return is_spam, confidence

# 싱글톤처럼 애플리케이션 라이프사이클 동안 하나의 모델 인스턴스만 유지합니다.
spam_model = SpamDetectionModel()
