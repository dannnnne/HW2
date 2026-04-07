from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., title="Text to analyze", description="The text content (email, message) to check for phishing/spam.")

class PredictResponse(BaseModel):
    is_spam: bool
    confidence: float
    message: str

class FeedbackRequest(BaseModel):
    text: str = Field(..., title="Analyzed text")
    prediction: bool = Field(..., title="AI prediction result")
    is_correct: bool = Field(..., title="User feedback if it was correct or not")
