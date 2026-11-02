from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType
)
from pyspark.sql.functions import (
    current_timestamp,
    input_file_name
)

PROJECT_ROOT =  Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw_landing"
    / "sensors"
    / "machine_sensor_logs.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "sensors"
)

SENSOR_SCHEMA = StructType([
    StructField("machine_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("temperature_c", StringType(), True),
    StructField("vibration_mm_s", StringType(), True),
    StructField("status", StringType(), True)
])

spark = (
    SparkSession.builder
    .appName("Manufacturing Bronze - Sensors")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    sensors_df = (
        spark.read
        .option("header", True)
        .schema(SENSOR_SCHEMA)
        .csv(str(INPUT_FILE))
    )

    raw_count = sensors_df.count()

    print("Total sensor readings:", raw_count)

    sensors_df.printSchema()

    sensors_df.show(5, truncate = False)

    print("Sensor status distribution:")

    (
        sensors_df
        .groupBy("status")
        .count()
        .orderBy("status")
        .show(truncate = False)
    )

    bronze_df = (
        sensors_df
        .withColumn("source_file", input_file_name())
        .withColumn("ingestion_timestamp", current_timestamp())
    )

    bronze_df.write.mode("overwrite").parquet(str(OUTPUT_DIR))

    print(f"Bronze sensor data saved at: {OUTPUT_DIR}")

    bronze_readback_df = spark.read.parquet(str(OUTPUT_DIR))

    bronze_count = bronze_readback_df.count()

    print("Bronze sensor records:", bronze_count)

    bronze_readback_df.printSchema()

    if bronze_count != raw_count:
        raise ValueError(
            f"Record count mismatch: "
            f"raw = {raw_count}, bronze = {bronze_count}"
        )
    
    duplicate_keys = (
        bronze_readback_df
        .groupBy("machine_id", "timestamp")
        .count()
        .filter("count > 1")
        .count()
    )

    print("Duplicate machine-timestamp groups:", duplicate_keys)

    print("Bronze ingestion metadata:")

    bronze_readback_df.select(
        "machine_id",
        "timestamp",
        "source_file",
        "ingestion_timestamp"
    ).show(3, truncate = False)

finally:
    spark.stop()
    