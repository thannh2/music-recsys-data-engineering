from pyspark.sql import SparkSession

def run_batch_loader():
    # Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("Metadata_Batch_Loader") \
        .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/music_recsys") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    def write_to_mongo(df, collection):

        df.write.format("com.mongodb.spark.sql.DefaultSource") \
            .option("database", "music_recsys") \
            .option("collection", collection) \
            .mode("append") \
            .save()
        print(f"-> Đã đẩy xong {collection}")

    # LUỒNG 1: Nạp dữ liệu Albums
    print("-> Bắt đầu nạp Albums...")
    df_albums = spark.read.option("sep", "\t").option("header", "true").csv("file:///mnt/data/lfm1b-albums.item")
    df_albums_opt = df_albums.selectExpr(
        "`albums_id:token` as album_id",
        "`name:token_seq` as title",
        "`artists_id:token` as artist_id"
    )
    write_to_mongo(df_albums_opt, "albums")

    # LUỒNG 2: Nạp dữ liệu Users
    print("-> Bắt đầu nạp Users...")
    df_users = spark.read.option("sep", "\t").option("header", "true").csv("file:///mnt/data/lfm1b-albums.user")
    df_users_opt = df_users.selectExpr(
        "`user_id:token` as user_id",
        "`country:token` as country",
        "cast(`age:float` as double) as age",
        "`gender:token` as gender",
        "cast(`playcount:float` as double) as playcount",
        "cast(`registered_timestamp:float` as double) as registered_timestamp",
        "cast(`novelty_artist_avg_year:float` as double) as novelty_artist_avg_year",
        "cast(`mainstreaminess_global:float` as double) as mainstreaminess_global",
        "cast(`cnt_distinct_artists:float` as double) as cnt_distinct_artists"
    )
    write_to_mongo(df_users_opt, "users")

    # LUỒNG 3: Nạp dữ liệu Interactions (File 3.4GB)
    print("-> Bắt đầu nạp Interactions...")
    df_inter = spark.read.option("sep", "\t").option("header", "true").csv("file:///mnt/data/lfm1b-albums.inter")
    df_inter_opt = df_inter.selectExpr(
        "`user_id:token` as user_id",
        "`albums_id:token` as album_id",
        "`timestamp:float` as timestamp",
        "cast(`num_repeat:float` as double) as num_repeat"
    )
    write_to_mongo(df_inter_opt, "interactions")

    print("=== BATCH LOAD DỮ LIỆU VÀO MONGODB HOÀN TẤT ===")
    spark.stop()

if __name__ == "__main__":
    run_batch_loader()