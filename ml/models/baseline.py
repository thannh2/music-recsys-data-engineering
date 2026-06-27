import numpy as np

def get_top_k_popular(df_raw, k=10):
    """Tìm Top K album được nghe nhiều nhất hệ thống."""
    return df_raw.groupby('album_idx')['num_repeat'].sum().nlargest(k).index.tolist()

def evaluate_baseline(top_k_albums, user_item_matrix, k=10):
    """Tính Precision@K cho phương pháp gợi ý phổ biến."""
    np.random.seed(42)
    num_users = user_item_matrix.shape[0]
    sample_users = np.random.choice(num_users, size=min(1000, num_users), replace=False)
    
    hits = 0
    total_recommendations = 0
    
    for u in sample_users:
        user_items = user_item_matrix[u].indices
        if len(user_items) == 0:
            continue
            
        overlap = len(set(top_k_albums).intersection(set(user_items)))
        hits += overlap
        total_recommendations += k
        
    return hits / total_recommendations if total_recommendations > 0 else 0