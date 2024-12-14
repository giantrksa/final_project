import os
import time
import psycopg2
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, FloatType
from datetime import datetime

# Define schema for the well logs
schema = StructType([
    StructField("depth", FloatType(), True),
    StructField("dgrc", FloatType(), True),
    StructField("btvpvs", FloatType(), True),
    StructField("btcs", FloatType(), True),
    StructField("btsflag", FloatType(), True),
    StructField("btcss", FloatType(), True),
    StructField("r15p", FloatType(), True),
    StructField("r09p", FloatType(), True),
    StructField("r39p", FloatType(), True),
    StructField("r27p", FloatType(), True),
    StructField("ewxt", FloatType(), True),
    StructField("alcdlc", FloatType(), True),
    StructField("tnps", FloatType(), True),
    StructField("aldclc", FloatType(), True)
])

# Database connection details
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "welldb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Maximum number of retries
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

def ensure_petrophysics_schema():
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cur = conn.cursor()
            cur.execute("CREATE SCHEMA IF NOT EXISTS petrophysics;")
            conn.commit()
            conn.close()
            print("Petrophysics schema ensured.")
            return
        except psycopg2.OperationalError as e:
            attempt += 1
            print(f"Attempt {attempt}/{MAX_RETRIES}: Could not connect to PostgreSQL. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"Error ensuring schema: {e}")
            raise e
    print("Exceeded maximum retries. Could not connect to PostgreSQL.")
    raise Exception("PostgreSQL connection failed after multiple attempts.")

class PostgresForeachWriter:
    def __init__(self, table, petrophysics_table):
        self.table = table
        self.petrophysics_table = petrophysics_table
        self.conn = None
        self.cur = None

    def open(self, partition_id, epoch_id):
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cur = self.conn.cursor()

            # Create main table
            create_main_table = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                depth FLOAT,
                dgrc FLOAT,
                btvpvs FLOAT,
                btcs FLOAT,
                btsflag FLOAT,
                btcss FLOAT,
                r15p FLOAT,
                r09p FLOAT,
                r39p FLOAT,
                r27p FLOAT,
                ewxt FLOAT,
                alcdlc FLOAT,
                tnps FLOAT,
                aldclc FLOAT
            );
            """
            # Create petrophysics table
            create_petrophysics_table = f"""
            CREATE TABLE IF NOT EXISTS {self.petrophysics_table} (
                depth FLOAT,
                dgrc FLOAT,
                btvpvs FLOAT,
                btcs FLOAT,
                btsflag FLOAT,
                btcss FLOAT,
                r15p FLOAT,
                r09p FLOAT,
                r39p FLOAT,
                r27p FLOAT,
                ewxt FLOAT,
                alcdlc FLOAT,
                tnps FLOAT,
                aldclc FLOAT,
                phi FLOAT,
                sw FLOAT
            );
            """
            self.cur.execute(create_main_table)
            self.cur.execute(create_petrophysics_table)
            self.conn.commit()
            print("Tables ensured.")
            return True
        except Exception as e:
            print(f"Error opening connection: {e}")
            return False

    def process(self, row):
        try:
            # Insert into main table
            insert_main = f"""
            INSERT INTO {self.table} (depth, dgrc, btvpvs, btcs, btsflag, btcss, r15p, r09p, r39p, r27p, ewxt, alcdlc, tnps, aldclc)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            main_values = (
                row.depth, row.dgrc, row.btvpvs, row.btcs, row.btsflag, row.btcss,
                row.r15p, row.r09p, row.r39p, row.r27p, row.ewxt, row.alcdlc,
                row.tnps, row.aldclc
            )
            self.cur.execute(insert_main, main_values)

            # Perform petrophysics calculations
            phi = 1 - (row.r15p / 2.65) if row.r15p and row.r15p != -999.25 else None
            sw = 1 / (1 + (row.r09p / row.r39p)) if row.r09p and row.r39p and row.r09p != -999.25 and row.r39p != -999.25 else None

            # Insert into petrophysics table
            insert_petrophysics = f"""
            INSERT INTO {self.petrophysics_table} (depth, dgrc, btvpvs, btcs, btsflag, btcss, r15p, r09p, r39p, r27p, ewxt, alcdlc, tnps, aldclc, phi, sw)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            petrophysics_values = (
                row.depth, row.dgrc, row.btvpvs, row.btcs, row.btsflag, row.btcss,
                row.r15p, row.r09p, row.r39p, row.r27p, row.ewxt, row.alcdlc,
                row.tnps, row.aldclc, phi, sw
            )
            self.cur.execute(insert_petrophysics, petrophysics_values)
            print(f"Inserted into petrophysics: {petrophysics_values}")
        except Exception as e:
            print(f"Error processing row: {e}")

    def close(self, error):
        try:
            if self.cur:
                self.conn.commit()
                self.cur.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

if __name__ == "__main__":
    # Ensure schema exists
    ensure_petrophysics_schema()

    spark = SparkSession.builder \
        .appName("WellLogsConsumerRowByRowWithPetrophysics") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .getOrCreate()

    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVER", "kafka:9092")
    kafka_topic = os.getenv("TOPIC_NAME", "well_logs")

    # Generate table names with date suffix
    date_suffix = datetime.now().strftime('%Y%m%d')
    main_table = f"well_logs_{date_suffix}"
    petrophysics_table = f"petrophysics.petrophysics_{date_suffix}"

    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse the JSON
    parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    # Create a ForeachWriter instance
    writer = PostgresForeachWriter(
        table=main_table,
        petrophysics_table=petrophysics_table
    )

    query = parsed_df.writeStream \
        .foreach(writer) \
        .outputMode("append") \
        .trigger(processingTime='1 seconds') \
        .start()

    query.awaitTermination()
