from pymongo import MongoClient
import lightgbm as lgb
import numpy as np
import os

# Biến toàn cục
_db_collection = None
_ranker_model = None
# Cache siêu dữ liệu trong RAM để giảm thiểu độ trễ truy vấn (Look-up)
_user_meta_cache = {}
_album_meta_cache = {}

def load_models():
    """Nạp kết nối DB, nạp mô hình Ranker và cache metadata."""
    global _db_collection, _ranker_model, _user_meta_cache, _album_meta_cache
    
    print("-> API đang kết nối tới MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["music_recsys"]
    _db_collection = db["daily_recommendations"]
    
    ranker_path = "artifacts/lightgbm_ranker.txt"
    if os.path.exists(ranker_path):
        print("-> Đang nạp mô hình Re-ranker (LightGBM)...")
        _ranker_model = lgb.Booster(model_file=ranker_path)
    else:
        print("!! Cảnh báo: Không tìm thấy mô hình Ranker. Sẽ dùng mặc định ALS.")

    # Tải siêu dữ liệu (Mock: Đọc từ DB collection tương ứng)
    # user_docs = db["user_metadata"].find({}, {"_id": 1, "age": 1})
    # _user_meta_cache = {doc["_id"]: doc.get("age", 25) for doc in user_docs}
    
    print("-> Đã kết nối DB và sẵn sàng Re-ranking!")

def get_hybrid_recommendations(user_idx: int, k: int = 10):
    """Thực thi logic True Hybrid: Lấy Candidate từ DB -> Trích xuất Đặc trưng -> Re-rank."""
    
    user_doc = _db_collection.find_one({"_id": f"user_{user_idx}"})
    
    if user_doc:
        candidates = user_doc.get("recommendations", [])
        als_scores = user_doc.get("scores", [])
        
        # Nếu chưa nạp được mô hình Ranker, trả về kết quả ALS ban đầu
        if _ranker_model is None or len(candidates) == 0:
            return {
                "user_idx": user_idx,
                "status": "existing_user",
                "strategy": "als_precomputed",
                "recommendations": candidates[:k],
                "scores": als_scores[:k]
            }
            
        # --- BẮT ĐẦU RE-RANKING ---
        # 1. Trích xuất đặc trưng User
        user_age = _user_meta_cache.get(user_idx, 25) # Giá trị mặc định 25
        
        # 2. Xây dựng ma trận đặc trưng cho các ứng viên
        feature_matrix = []
        for i, album_idx in enumerate(candidates):
            a_score = als_scores[i]
            album_pop = _album_meta_cache.get(album_idx, 50) # Mặc định 50
            
            # Thứ tự mảng phải khớp chính xác với mảng features lúc train
            # features = ['als_score', 'user_age', 'album_popularity']
            feature_vector = [a_score, user_age, album_pop]
            feature_matrix.append(feature_vector)
            
        # 3. Đưa qua Ranker dự đoán (Predict)
        matrix_np = np.array(feature_matrix)
        reranked_scores = _ranker_model.predict(matrix_np)
        
        # 4. Ghép cặp và sắp xếp lại
        paired = list(zip(candidates, reranked_scores))
        paired.sort(key=lambda x: x[1], reverse=True)
        
        top_k = paired[:k]
        
        return {
            "user_idx": user_idx,
            "status": "existing_user",
            "strategy": "lightgbm_reranking",
            "recommendations": [int(x[0]) for x in top_k],
            "scores": [float(x[1]) for x in top_k]
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
    trending_doc = _db_collection.find_one({"_id": "trending_baseline"})
    recs = trending_doc.get("recommendations", [])[:limit] if trending_doc else []
    return {"status": "success", "trending_albums": recs}

def get_user_history(user_idx: int):
    user_doc = _db_collection.find_one({"_id": f"user_{user_idx}"})
    history = user_doc.get("history", []) if user_doc else []
    
    return {
        "user_idx": user_idx,
        "total_listened": len(history),
        "listened_albums": history
    }

def get_system_status():
    is_online = _db_collection is not None
    is_ranker_loaded = _ranker_model is not None
    return {
        "status": "online" if is_online else "offline",
        "architecture": "Re-ranking Pipeline",
        "database_connected": is_online,
        "ranker_loaded": is_ranker_loaded
    }