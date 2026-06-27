# Real-time Music Album Recommendation System (Kappa Architecture)

Dự án xây dựng một đường ống dữ liệu (Data Pipeline) theo thời gian thực phục vụ hệ thống gợi ý album nhạc. Hệ thống áp dụng Kiến trúc Kappa (Kappa Architecture) để xử lý toàn bộ dữ liệu dưới dạng luồng (stream-first design), kết hợp mô hình Lọc cộng tác (Collaborative Filtering) dựa trên phản hồi ẩn (Implicit Feedback).

## 1. Kiến trúc hệ thống

Hệ thống được chia thành 4 giai đoạn xử lý độc lập:
1. **Data Ingestion:** Kafka Producer đọc dữ liệu tương tác thô và đẩy vào luồng sự kiện theo thời gian thực.
2. **Stream Processing & Enrichment:** Spark Structured Streaming tiêu thụ luồng sự kiện, thực hiện `Stream-Static Join` trong bộ nhớ với siêu dữ liệu người dùng/album để làm giàu dữ liệu (Data Enrichment).
3. **Storage & Feature Store:** Ghi ma trận đặc trưng liên tục vào MongoDB (Hot Storage) và lưu trữ log sự kiện thô vào MinIO/HDFS (Cold Storage).
4. **Machine Learning & Serving:** Spark MLlib huấn luyện mô hình Alternating Least Squares (ALS) định kỳ. FastAPI cung cấp endpoint truy xuất danh sách gợi ý với độ trễ thấp.

## 2. Ngăn xếp công nghệ (Tech Stack)

* **Message Broker:** Apache Kafka
* **Stream Processing:** Apache Spark (Structured Streaming, PySpark)
* **Machine Learning:** Spark MLlib (ALS Algorithm)
* **Database / Feature Store:** MongoDB
* **Backend API:** FastAPI (Python 3.x)
* **Infrastructure:** Docker / Kubernetes (Minikube)

## 3. Cấu trúc thư mục

* `src/ingestion/`: Mã nguồn Kafka Producer giả lập luồng sự kiện.
* `src/streaming/`: Các job Spark Structured Streaming xử lý và làm giàu dữ liệu.
* `src/ml/`: Các job Spark Batch huấn luyện mô hình ALS.
* `src/api/`: Dịch vụ web FastAPI phục vụ kết quả gợi ý.
* `infrastructure/`: Các tệp cấu hình Docker Compose và Kubernetes.

## 4. Tập dữ liệu (Dataset)

Dự án sử dụng tập dữ liệu **LFM-1b Dataset**, bao gồm 3 tệp chính:
* `lfm1b-albums.inter`: Dữ liệu tương tác sự kiện (user_id, albums_id, timestamp, num_repeat).
* `lfm1b-albums.user`: Siêu dữ liệu nhân khẩu học và đặc trưng hành vi người dùng.
* `lfm1b-albums.item`: Siêu dữ liệu định danh album và nghệ sĩ.

## 5. Hướng dẫn cài đặt và khởi chạy

*(Phần này sẽ được bổ sung các lệnh cụ thể sau khi hoàn thiện mã nguồn và cấu hình hạ tầng)*

1. Khởi động hạ tầng (Kafka, MongoDB, Spark) qua Docker Compose.
2. Khởi chạy Kafka Producer.
3. Submit Spark Streaming Job.
4. Chạy mô hình ML và khởi động FastAPI Server.