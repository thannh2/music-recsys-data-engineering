def calculate_hybrid_score(als_items, als_scores, popularity_scores, alpha=0.8):
    """Kết hợp điểm ALS và điểm Popularity theo trọng số alpha."""
    hybrid_results = []
    if len(als_scores) > 0 and als_scores.max() > 0:
        als_scores = als_scores / als_scores.max()
        
    for i, item_idx in enumerate(als_items):
        s_als = als_scores[i]
        s_pop = popularity_scores.get(item_idx, 0)
        # Công thức: Score = Alpha * ALS + (1 - Alpha) * Popularity
        s_final = (alpha * s_als) + ((1 - alpha) * s_pop)
        hybrid_results.append((item_idx, s_final))
        
    return sorted(hybrid_results, key=lambda x: x[1], reverse=True)