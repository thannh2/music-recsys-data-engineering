from kafka.admin import KafkaAdminClient, NewTopic
from config import KAFKA_BROKER, TOPICS

def init_topics():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER, client_id='init_script')
        existing_topics = admin_client.list_topics()
        
        topics_to_create = []
        for topic_name in TOPICS.values():
            if topic_name not in existing_topics:
                # Tạo topic với 1 partition và 1 replication (dành cho local)
                new_topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
                topics_to_create.append(new_topic)
                
        if topics_to_create:
            admin_client.create_topics(new_topics=topics_to_create)
            print(f"[SETUP] Đã tạo mới các topics: {[t.name for t in topics_to_create]}")
        else:
            print("[SETUP] Các topics Kafka đã sẵn sàng.")
            
        admin_client.close()
    except Exception as e:
        print(f"[SETUP ERROR] Không thể tự động tạo topics: {e}")