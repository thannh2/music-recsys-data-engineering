import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import os

def train_ranker():
    print("-> Đang nạp dữ liệu huấn luyện Ranker...")
    
    df_interactions = pd.read_parquet("training_data.parquet")
    df_interactions['label'] = 1 # Tương tác thực tế

    df_negatives = df_interactions.copy()
    df_negatives['album_id'] = df_negatives['album_id'].sample(frac=1).reset_index(drop=True)
    df_negatives['label'] = 0
    
    df_train = pd.concat([df_interactions, df_negatives]).sample(frac=1).reset_index(drop=True)

    import numpy as np
    df_train['als_score'] = np.random.rand(len(df_train)) # Điểm ALS
    df_train['user_age'] = np.random.randint(15, 50, len(df_train))
    df_train['album_popularity'] = np.random.randint(1, 100, len(df_train))
    
    features = ['als_score', 'user_age', 'album_popularity']
    X = df_train[features]
    y = df_train['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("-> Bắt đầu huấn luyện LightGBM Ranker...")
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.1,
        'num_leaves': 31,
        'verbose': -1
    }
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=[valid_data],
        callbacks=[lgb.early_stopping(stopping_rounds=10)]
    )
    
    # 6. Lưu mô hình
    os.makedirs("artifacts", exist_ok=True)
    model.save_model('artifacts/lightgbm_ranker.txt')
    print("-> Đã lưu mô hình Ranker tại artifacts/lightgbm_ranker.txt")

if __name__ == "__main__":
    train_ranker()