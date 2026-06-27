from pymongo import MongoClient

# Biến toàn cục
_db_collection = None

def load_models():
    """Nạp kết nối DB để phục vụ Batch Inference results."""
    global _db_collection
    
    print("-> API đang kết nối tới MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["music_recsys"]
    _db_collection = db["daily_recommendations"]
    print("-> Đã kết nối DB và sẵn sàng!")

def get_recommendations(user_idx: int, k: int = 10):
    """
    Theo thiết kế trong báo cáo: API lấy danh sách gợi ý đã sinh trước (Batch Inference) từ MongoDB.
    """
    if _db_collection is None:
        return {
            "user_idx": user_idx,
            "status": "offline",
            "strategy": "none",
            "recommendations": [],
            "scores": []
        }
        
    user_doc = _db_collection.find_one({"_id": f"user_{user_idx}"})
    
    if user_doc:
        candidates = user_doc.get("recommendations", [])
        als_scores = user_doc.get("scores", [])
        
        return {
            "user_idx": user_idx,
            "status": "existing_user",
            "strategy": "als_precomputed",
            "recommendations": candidates[:k],
            "scores": als_scores[:k]
        }
        
    # Fallback cho User mới (Cold-start)
    trending_doc = _db_collection.find_one({"_id": "trending_baseline"})
    trending_recs = trending_doc.get("recommendations", [])[:k] if trending_doc else []
    
    return {
        "user_idx": user_idx,
        "status": "new_user",
        "strategy": "popularity_baseline",
        "recommendations": trending_recs,
        "scores": None
    }

def get_trending_albums(limit: int = 10):
    if _db_collection is None:
        return {"status": "offline", "trending_albums": []}
        
    trending_doc = _db_collection.find_one({"_id": "trending_baseline"})
    recs = trending_doc.get("recommendations", [])[:limit] if trending_doc else []
    return {"status": "success", "trending_albums": recs}

def get_user_history(user_idx: int):
    if _db_collection is None:
        return {"user_idx": user_idx, "total_listened": 0, "listened_albums": []}
        
    user_doc = _db_collection.find_one({"_id": f"user_{user_idx}"})
    history = user_doc.get("history", []) if user_doc else []
    
    return {
        "user_idx": user_idx,
        "total_listened": len(history),
        "listened_albums": history
    }

def get_system_status():
    is_online = _db_collection is not None
    return {
        "status": "online" if is_online else "offline",
        "model_loaded": is_online,
        "matrix_shape": "N/A (Batch inference mode)"
    }