# kafka_game_event_stream.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
EC2_HOST = os.getenv('EC2_HOST')

# SparkSession 생성
spark = SparkSession.builder \
    .appName("KafkaGameEventStream") \
    .master("local[*]") \
    .config("spark.sql.streaming.schemaInference", True) \
    .getOrCreate()

# 로그 줄이기
spark.sparkContext.setLogLevel("WARN")

# Kafka 메시지 스키마 정의 (HTML에서 전송된 JSON 구조와 일치)
schema = StructType() \
    .add("user", StringType()) \
    .add("user_choice", StringType()) \
    .add("computer_choice", StringType()) \
    .add("result", StringType()) \
    .add("timestamp", StringType())  # 또는 TimestampType() if parsing timestamp

# Kafka에서 데이터 읽기
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{EC2_HOST}:9092") \
    .option("subscribe", "gameevents") \
    .option("startingOffsets", "latest") \
    .load()

# value는 바이너리 → 문자열로 변환
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# 콘솔에 출력
query = df_parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
