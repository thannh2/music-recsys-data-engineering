from fastapi import APIRouter
from api.schemas.music_schema import RecommendResponse, TrendingResponse, UserHistoryResponse, SystemStatusResponse
from api.services.inference import get_hybrid_recommendations, get_trending_albums, get_user_history, get_system_status

router = APIRouter(prefix="/api/v1", tags=["Music Recommendations"])

@router.get("/recommend/{user_idx}", response_model=RecommendResponse)
def recommend_music(user_idx: int, k: int = 10):
    """
    Lấy danh sách k album gợi ý cho người dùng.
    Hỗ trợ cả người dùng cũ (ALS) và người dùng mới (Baseline).
    """
    result = get_hybrid_recommendations(user_idx, k)
    return result

@router.get("/trending", response_model=TrendingResponse, tags=["Explore"])
def get_trending(limit: int = 10):
    """
    Lấy danh sách Top các Album được nghe nhiều nhất.
    Rất hữu ích để hiển thị trên màn hình Trang chủ (Home).
    """
    return get_trending_albums(limit)

@router.get("/history/{user_idx}", response_model=UserHistoryResponse, tags=["User Profile"])
def get_history(user_idx: int):
    """
    Lấy lịch sử các Album mà người dùng đã từng tương tác.
    """
    return get_user_history(user_idx)

@router.get("/status", response_model=SystemStatusResponse, tags=["System DevOps"])
def check_status():
    """
    Kiểm tra trạng thái nạp mô hình của hệ thống.
    """
    return get_system_status()