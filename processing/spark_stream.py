import os
os.environ["_JAVA_OPTIONS"] = "-Djava.security.manager=allow"

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pymongo import MongoClient
print("=== KHỞI ĐỘNG HỆ THỐNG SPARK STREAMING ===")

# 1. Khởi tạo Spark Session với thư viện kết nối Kafka
spark = SparkSession.builder \
    .appName("MusicRecSys_StreamProcessor") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Định nghĩa Schema (Cấu trúc dữ liệu) cho luồng Interactions
interaction_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("album_id", StringType(), True),
    StructField("timestamp", DoubleType(), True),
    StructField("num_repeat", DoubleType(), True)
])

# 3. Kết nối vào Kafka và đọc Topic 'music_interactions'
print("-> Đang kết nối tới Kafka Broker...")
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "music_interactions") \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Trích xuất và Ép kiểu dữ liệu (Transformation)
# Dữ liệu từ Kafka mặc định là dạng Byte, cần CAST sang String rồi dùng from_json
df_parsed = df_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), interaction_schema).alias("data")) \
    .select("data.*")

def write_to_mongo(df, epoch_id):

    def process_partition(partition):
        client = MongoClient("mongodb://mongodb:27017/")
        db = client["music_recsys"]
        collection = db["realtime_interactions"]

        from datetime import datetime
        docs = [row.asDict() for row in partition]
        for doc in docs:
            doc["processed_at"] = datetime.utcnow()
        if docs:
            collection.insert_many(docs)

        client.close()

    df.foreachPartition(process_partition)
    
# 5. In kết quả ra màn hình (Action)
print("-> Bắt đầu Streaming dữ liệu vào MongoDB...")
query = (
    df_parsed.writeStream
    .outputMode("append")
    .foreachBatch(write_to_mongo)
    .option(
        "checkpointLocation",
        "/opt/bitnami/spark/checkpoint/interactions"
    )
    .start()
)

query.awaitTermination()