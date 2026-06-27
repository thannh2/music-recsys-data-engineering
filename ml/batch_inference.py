import implicit
import scipy.sparse as sparse
import pandas as pd
from pymongo import MongoClient
import os
import time

def run_batch_inference(k=50):
    print("-> Đang khởi tạo Batch Inference (Sinh 50 Candidates)...")
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client["music_recsys"]
    collection = db["daily_recommendations"]
    
    print("-> Xóa dữ liệu gợi ý của ngày hôm trước (Refresh)...")
    collection.delete_many({})
    
    model_path = "artifacts/als_model.npz"
    matrix_path = "artifacts/user_item_matrix.npz"
    data_path = "training_data.parquet"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError("Không tìm thấy file mô hình trong artifacts!")
        
    print("-> Đang nạp mô hình ALS vào RAM để tính toán...")
    dummy_model = implicit.als.AlternatingLeastSquares()
    model = dummy_model.__class__.load(model_path)
    user_item_matrix = sparse.load_npz(matrix_path)
    
    print("-> Đang tính toán Trending Baseline...")
    df = pd.read_parquet(data_path)
    df['album_idx'] = df['album_id'].astype("category").cat.codes
    popular_albums = df.groupby('album_idx')['num_repeat'].sum().nlargest(k).index.tolist()
    
    collection.insert_one({
        "_id": "trending_baseline",
        "recommendations": popular_albums,
        "updated_at": time.time()
    })
    
    num_users = user_item_matrix.shape[0]
    batch_docs = []
    BATCH_SIZE = 10000 
    
    print(f"-> Bắt đầu tính toán cho {num_users} users...")
    for user_idx in range(num_users):
        user_interactions = user_item_matrix[user_idx]
        
        if user_interactions.nnz == 0:
            continue
            
        ids, scores = model.recommend(user_idx, user_interactions, N=k, filter_already_liked_items=True)
        
        batch_docs.append({
            "_id": f"user_{user_idx}",
            "recommendations": [int(x) for x in ids],
            "scores": [float(x) for x in scores],
            "history": [int(x) for x in user_interactions.indices]
        })
        
        if len(batch_docs) >= BATCH_SIZE:
            collection.insert_many(batch_docs)
            batch_docs = []
            print(f"   + Đã lưu {user_idx + 1}/{num_users} users vào DB...")
            
    if batch_docs:
        collection.insert_many(batch_docs)
        print(f"   + Đã lưu {num_users}/{num_users} users vào DB...")
        
    print("-> HOÀN THÀNH BATCH INFERENCE! Dữ liệu đã sẵn sàng cho API.")

if __name__ == "__main__":
    run_batch_inference()