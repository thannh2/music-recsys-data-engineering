import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_metrics(csv_file="experiment_log.csv"):
    if not os.path.exists(csv_file):
        print(f"Lỗi: Không tìm thấy tệp {csv_file}")
        return

    # Đọc dữ liệu từ file CSV
    df = pd.read_csv(csv_file)
    
    df.columns = df.columns.str.strip()

    # Lọc dữ liệu chỉ lấy Reg = 0.2
    df = df[df['Reg'] == 0.2]
    regs = [0.2]

    # --- 1. Vẽ biểu đồ Precision@10 ---
    plt.figure(figsize=(10, 6))
    for reg in regs:
        subset = df[df['Reg'] == reg].sort_values(by='Factors')
        plt.plot(subset['Factors'], subset['Precision@10'], marker='o', label=f'Reg = {reg}')

    plt.title('Hiệu suất Mô hình ALS - Precision@10 (Reg = 0.2)')
    plt.xlabel('Số lượng Nhân tố ẩn (Factors)')
    plt.ylabel('Precision@10')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    precision_file = 'precision_plot.png'
    plt.savefig(precision_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Đã lưu biểu đồ Precision@10 thành '{precision_file}'")

    # --- 2. Vẽ biểu đồ NDCG@10 ---
    plt.figure(figsize=(10, 6))
    for reg in regs:
        subset = df[df['Reg'] == reg].sort_values(by='Factors')
        plt.plot(subset['Factors'], subset['NDCG@10'], marker='o', label=f'Reg = {reg}')

    plt.title('Hiệu suất Mô hình ALS - NDCG@10 (Reg = 0.2)')
    plt.xlabel('Số lượng Nhân tố ẩn (Factors)')
    plt.ylabel('NDCG@10')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    ndcg_file = 'ndcg_plot.png'
    plt.savefig(ndcg_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Đã lưu biểu đồ NDCG@10 thành '{ndcg_file}'")

if __name__ == "__main__":
    plot_metrics()