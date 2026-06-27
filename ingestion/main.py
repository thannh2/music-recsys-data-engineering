import sys
import os

# Thêm thư mục hiện tại (ingestion) vào sys.path để import file bên trong nó
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DATA_FILES, TOPICS
from setup_kafka import init_topics
from parsers import parse_album, parse_user, parse_interaction
from core import create_producer, process_file

def run_pipeline():
    print("=== KHỞI ĐỘNG SIMULATION ENGINE ===")
    init_topics()
    producer = create_producer()
    
    try:
        # CHỈ ĐẨY INTERACTIONS - Đây là luồng "dữ liệu động" bạn cần cho Stream
        process_file(DATA_FILES['interactions'], TOPICS['interactions'], producer, parse_interaction)
        
    except KeyboardInterrupt:
        print("\n[HỆ THỐNG] Đã dừng giả lập.")
    finally:
        producer.close()

if __name__ == "__main__":
    run_pipeline()