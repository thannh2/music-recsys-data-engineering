from pydantic import BaseModel
from typing import List, Optional

class RecommendResponse(BaseModel):
    user_idx: int
    status: str
    strategy: str
    recommendations: List[int]
    scores: Optional[List[float]] = None

class TrendingResponse(BaseModel):
    status: str = "success"
    trending_albums: List[int]

class UserHistoryResponse(BaseModel):
    user_idx: int
    total_listened: int
    listened_albums: List[int]

class SystemStatusResponse(BaseModel):
    status: str
    model_loaded: bool
    matrix_shape: Optional[str] = None