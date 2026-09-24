from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    raw_text: str


class AnalyzeResponse(BaseModel):
    toxicity_level: int
    copyright_risk: int
    culture_insensitivity: int
