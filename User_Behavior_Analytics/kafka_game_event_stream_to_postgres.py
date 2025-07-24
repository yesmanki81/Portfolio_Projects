from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, TimestampType
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()
KAFKA_HOST = os.getenv("EC2_HOST")
PG_URL = os.getenv("POSTGRES_URL")         # e.g. jdbc:postgresql://localhost:5432/gameevent
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PASSWORD")

# Spark Session
spark = SparkSession.builder \
    .appName("KafkaGameEventStreamToPostgres") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Kafka 메시지 스키마 정의
schema = StructType() \
    .add("user", StringType()) \
    .add("user_choice", StringType()) \
    .add("computer_choice", StringType()) \
    .add("result", StringType()) \
    .add("timestamp", StringType())  # 또는 TimestampType() if needed

# Kafka에서 스트리밍 데이터 읽기
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{KAFKA_HOST}:9092") \
    .option("subscribe", "gameevents") \
    .option("startingOffsets", "latest") \
    .load()

# JSON 파싱
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# PostgreSQL에 저장하는 함수 정의
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", "rps_events") \
        .option("user", PG_USER) \
        .option("password", PG_PW) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# 스트리밍 쿼리 실행
query = df_parsed.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

query.awaitTermination()


