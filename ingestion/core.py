import json
import os
import time
from kafka import KafkaProducer
from config import KAFKA_BROKER

def create_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            request_timeout_ms=30000,
            batch_size=16384,
            linger_ms=10
        )
    except Exception as e:
        print(f"[ERROR] Không thể kết nối Kafka: {e}")
        return None

def process_file(file_path, topic_name, producer, parser_func):
    if not producer: return
    if not os.path.exists(file_path):
        print(f"[CẢNH BÁO] Không tìm thấy file: {file_path}")
        return

    print(f"--- Đang bắt đầu gửi dữ liệu vào topic: {topic_name} ---")
    success_count = 0
    error_count = 0
    start_time = time.time()

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            payload = parser_func(parts)
            
            if payload:
                try:
                    # Gửi và đợi kết quả xác nhận (để đảm bảo không mất dữ liệu)
                    future = producer.send(topic_name, value=payload)
                    # producer.flush() # Bỏ comment nếu muốn độ tin cậy tuyệt đối (chậm hơn)
                    success_count += 1
                    
                    # LOG DEBUG: Cập nhật mỗi 10 dòng thay vì 200.000 dòng
                    if success_count % 10 == 0:
                        print(f"[{topic_name}] Đã đẩy {success_count} bản ghi...")
                    
                    time.sleep(0.1) # Giả lập 10 req/s
                except Exception as e:
                    print(f"[LỖI GỬI] {e}")
            else:
                error_count += 1
            
    producer.flush()
    print(f"Hoàn thành {topic_name}: {success_count} gửi thành công, {error_count} lỗi.")