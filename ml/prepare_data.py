import pandas as pd
from pymongo import MongoClient
import os

def export_to_parquet():
    print("-> Đang kết nối MongoDB để trích xuất dữ liệu...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["music_recsys"]
    collection = db["interactions"]
    

    projection = {"_id": 0, "user_id": 1, "album_id": 1, "num_repeat": 1}
    BATCH_SIZE = 1000000 
    temp_files = []
    
    print(f"-> Đang trích xuất dữ liệu từ collection 'interactions'...")
    total_docs = collection.count_documents({})
    
    # 1. Kỹ thuật Batch Processing & Temporary Storage
    for i in range(0, total_docs, BATCH_SIZE):
        try:
            cursor = collection.find({}, projection).skip(i).limit(BATCH_SIZE)
            df_batch = pd.DataFrame(list(cursor))
        except Exception as e:
            print(f"!! Lỗi giải mã BSON tại batch bắt đầu từ {i}: {e}. Đang bỏ qua batch này...")
            continue
        
        if df_batch.empty: break
            
        df_batch = df_batch.dropna(subset=['user_id', 'album_id'])
        
        temp_file = f"temp_batch_{i}.parquet"
        df_batch.to_parquet(temp_file)
        temp_files.append(temp_file)
        print(f"   + Đã xuất batch {i//BATCH_SIZE + 1} ({len(df_batch)} dòng)")

    if not temp_files:
        print("!! Không trích xuất được dữ liệu nào.")
        return

    print("-> Đang tổng hợp dữ liệu...")
    df_final = pd.concat([pd.read_parquet(f) for f in temp_files])
    df_final = df_final.drop_duplicates()
    
    print("-> Đang thực hiện lọc (Data Pruning)...")
    MIN_USER_INTERACTIONS = 20
    MIN_ALBUM_INTERACTIONS = 20

    user_counts = df_final['user_id'].value_counts()
    df_final = df_final[df_final['user_id'].isin(user_counts[user_counts >= MIN_USER_INTERACTIONS].index)]

    album_counts = df_final['album_id'].value_counts()
    df_final = df_final[df_final['album_id'].isin(album_counts[album_counts >= MIN_ALBUM_INTERACTIONS].index)]

    print(f"-> Đang lưu ra file training_data.parquet (Còn lại: {len(df_final)} dòng)...")
    df_final.to_parquet("training_data.parquet", index=False)
    
    for f in temp_files:
        if os.path.exists(f): os.remove(f)
        
    print("-> HOÀN THÀNH XUẤT DỮ LIỆU!")

if __name__ == "__main__":
    export_to_parquet()