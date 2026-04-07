from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., title="Text to analyze", description="The text content (email, message) to check for phishing/spam.")

class PredictResponse(BaseModel):
    is_spam: bool
    confidence: float
    message: str
