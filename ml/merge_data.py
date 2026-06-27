import pandas as pd
import glob
import os

def merge_dask_parts(directory="training_data.parquet", output_file="final_training_data.parquet"):
    # Tìm tất cả các file part bên trong thư mục
    files = glob.glob(os.path.join(directory, "part.*.parquet"))
    print(f"-> Tìm thấy {len(files)} file part. Đang gộp...")
    
    # Đọc và gộp từng file một để tránh tràn RAM
    df_list = [pd.read_parquet(f) for f in files]
    df_final = pd.concat(df_list, ignore_index=True)
    
    # Lưu ra file đơn lẻ
    df_final.to_parquet(output_file, index=False)
    print(f"-> Đã gộp xong thành công: {output_file}")

if __name__ == "__main__":
    merge_dask_parts()