# spark-scripts/spark-streaming.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, FloatType
import os

# Define the schema based on your LAS data
schema = StructType([
    StructField("DEPT", FloatType(), True),
    StructField("DT", FloatType(), True),
    StructField("RHOB", FloatType(), True),
    StructField("NPHI", FloatType(), True),
    StructField("GR", FloatType(), True),
    # Add other fields as necessary
])

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("LAS_Kafka_Streaming") \
    .master(os.getenv('SPARK_MASTER_URL', 'spark://spark-master:7077')) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "las-data") \
    .option("startingOffsets", "earliest") \
    .load()

# Convert the binary 'value' column to string and then to JSON
json_df = df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), schema).alias("data")) \
    .select("data.*")

# Write to PostgreSQL (Requires JDBC driver)
jdbc_url = "jdbc:postgresql://postgres:5432/postgres_dw"
properties = {
    "user": os.getenv('POSTGRES_USER', 'postgres'),
    "password": os.getenv('POSTGRES_PASSWORD', 'postgres'),
    "driver": "org.postgresql.Driver"
}

query = json_df.writeStream \
    .foreachBatch(lambda batch_df, batch_id: batch_df.write.jdbc(
        url=jdbc_url,
        table="las_data",
        mode="append",
        properties=properties
    )) \
    .outputMode("append") \
    .start()

query.awaitTermination()
