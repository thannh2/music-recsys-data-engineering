import pandas as pd
import scipy.sparse as sparse
import implicit
from implicit.evaluation import train_test_split, precision_at_k, ndcg_at_k
import time
import matplotlib.pyplot as plt
import csv
import os
import yaml
from ml.models.baseline import get_top_k_popular, evaluate_baseline

def load_config(config_path="config.yaml"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, config_path)
    
    with open(full_path, "r") as f:
        return yaml.safe_load(f)
    
def load_and_prepare_data(filepath="final_training_data.parquet"):
    print(f"-> Đang tải dữ liệu từ {filepath} bằng PyArrow để tối ưu RAM...")
    import pyarrow.parquet as pq
    
    table = pq.read_table(filepath)
    
    # 1. Chuyển đổi sang DataFrame
    df_temp = table.select(['user_id', 'album_id', 'num_repeat']).to_pandas()
    
    # 2. Làm sạch hoàn toàn
    df_temp = df_temp.dropna(subset=['user_id', 'album_id', 'num_repeat'])
    
    # 3. Factorize sau khi đã làm sạch
    df_temp['user_idx'] = pd.factorize(df_temp['user_id'])[0]
    df_temp['album_idx'] = pd.factorize(df_temp['album_id'])[0]
    
    num_users = df_temp['user_idx'].nunique()
    num_albums = df_temp['album_idx'].nunique()
    print(f"-> Dữ liệu gồm {num_users} Users và {num_albums} Albums.")

    # 4. Xây dựng ma trận Sparse từ dữ liệu đã đồng bộ
    sparse_item_user = sparse.csr_matrix(
        (df_temp['num_repeat'].astype("float32"), (df_temp['album_idx'], df_temp['user_idx'])),
        shape=(num_albums, num_users)
    )
    sparse_user_item = sparse_item_user.T.tocsr()
    
    df = df_temp[['user_id', 'album_id', 'album_idx', 'num_repeat']].copy()
    
    return sparse_item_user, sparse_user_item, df

def grid_search_als(train_matrix, test_matrix, log_file="experiment_log.csv", K=10):
    config = load_config()
    factors_list = config['model']['factors']
    reg_list = config['model']['regs']
    
    results = []
    
    print(f"\n--- BẮT ĐẦU GRID SEARCH (EVALUATING ON TEST SET @K={K}) ---")
    
    import logging
    logging.getLogger('implicit').setLevel(logging.ERROR)
    
    for f in factors_list:
        for r in reg_list:
            start_time = time.time()
            
            model = implicit.als.AlternatingLeastSquares(
                factors=f, regularization=r, iterations=15, 
                calculate_training_loss=False, random_state=42 
            )
            
            model.fit(train_matrix, show_progress=False)
            
            score_prec = precision_at_k(model, train_matrix, test_matrix, K=K, show_progress=False)
            score_ndcg = ndcg_at_k(model, train_matrix, test_matrix, K=K, show_progress=False)
            
            run_time = time.time() - start_time
            
            log_experiment(log_file, f, r, score_prec, score_ndcg, K, run_time)
            results.append({'factors': f, 'reg': r, 'precision': score_prec, 'ndcg': score_ndcg})
            print(f"Factors: {f}, Reg: {r} | Precision@{K}: {score_prec:.4f}, NDCG@{K}: {score_ndcg:.4f} | Time: {run_time:.2f}s")
            
    return results

def plot_grid_search_results(experiment_results, filename="als_research_results.png"):
    print(f"\n-> Đang vẽ biểu đồ kết quả dựa trên NDCG@10 và lưu vào {filename}...")
    
    regs = sorted(list(set([r['reg'] for r in experiment_results])))
    factors = sorted(list(set([r['factors'] for r in experiment_results])))
    
    plt.figure(figsize=(10, 6))
    
    for r in regs:
        scores = [res['ndcg'] for res in experiment_results if res['reg'] == r]
        plt.plot(factors, scores, marker='o', label=f'Regularization = {r}')
    
    plt.title('Hiệu suất Mô hình ALS trên Tập Test (Theo NDCG@10)')
    plt.xlabel('Số lượng Nhân tố ẩn (Factors)')
    plt.ylabel('Test NDCG@10')
    plt.xticks(factors)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print("-> Đã lưu biểu đồ thành công!")

def log_experiment(results_file, factors, reg, prec, ndcg, K, run_time):
    file_exists = os.path.isfile(results_file)
    with open(results_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Ghi tiêu đề rõ ràng với K
            writer.writerow(['factors', 'reg', f'precision@{K}', f'ndcg@{K}', 'time_s'])
        writer.writerow([factors, reg, round(prec, 4), round(ndcg, 4), round(run_time, 2)])

def main():
    item_user_matrix, user_item_matrix, df_raw = load_and_prepare_data("final_training_data.parquet")
    
    # Chia dữ liệu: 80% Train, 20% Test
    train_matrix, test_matrix = train_test_split(user_item_matrix, train_percentage=0.8, random_state=42)
    
    # Chạy Baseline
    K_VALUE = 10
    top_k = get_top_k_popular(df_raw, K_VALUE)
    score_base = evaluate_baseline(top_k, user_item_matrix)
    print(f"=> Popularity Baseline Precision@10 (Full Data): {score_base:.4f}")
    
    # Grid Search ALS
    experiment_results = grid_search_als(train_matrix, test_matrix, K=K_VALUE)
    plot_grid_search_results(experiment_results)
    
    # Lựa chọn tham số tốt nhất dựa trên NDCG
    best_config = max(experiment_results, key=lambda x: x['ndcg'])
    print(f"\n-> Cấu hình tốt nhất: Factors={best_config['factors']}, Reg={best_config['reg']} với NDCG={best_config['ndcg']:.4f}")
    
    best_model = implicit.als.AlternatingLeastSquares(factors=best_config['factors'], regularization=best_config['reg'])
    best_model.fit(user_item_matrix, show_progress=False)
    
    save_dir = "artifacts"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    best_model.save(os.path.join(save_dir, "als_model.npz"))
    sparse.save_npz(os.path.join(save_dir, "user_item_matrix.npz"), user_item_matrix)
    print(f"-> Đã lưu mô hình vào: {save_dir}")

if __name__ == "__main__":
    main()