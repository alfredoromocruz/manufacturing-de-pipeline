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

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw_landing"
    / "production_orders"
    / "production_orders.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "production_orders"
)

MACHINES_BRONZE_DIR = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "machines"
)

PRODUCTION_SCHEMA = StructType([
    StructField("order_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("machine_id", StringType(), True),
    StructField("shift_id", StringType(), True),
    StructField("quantity_produced", StringType(), True),
    StructField("start_time", StringType(), True),
    StructField("end_time", StringType(), True),
    StructField("planned_production_minutes", StringType(), True)
])

spark = (
    SparkSession.builder
    .appName("Manufacturing Bronze - Production Orders")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    orders_df = (
        spark.read
        .option("header", True)
        .schema(PRODUCTION_SCHEMA)
        .csv(str(INPUT_FILE))
    )

    raw_count = orders_df.count()

    print("Total production orders:", raw_count)

    orders_df.printSchema()

    orders_df.show(5, truncate = False)

    print("Orders by production shift:")

    (
        orders_df
        .groupBy("shift_id")
        .count()
        .orderBy("shift_id")
        .show(truncate = False)
    )

    bronze_df = (
        orders_df
        .withColumn("source_file", input_file_name())
        .withColumn("ingestion_timestamp", current_timestamp())
    )

    bronze_df.write.mode("overwrite").parquet(str(OUTPUT_DIR))

    print(f"Bronze production data saved at: {OUTPUT_DIR}")

    bronze_orders_df = spark.read.parquet(str(OUTPUT_DIR))

    bronze_count = bronze_orders_df.count()

    print("Bronze production records:", bronze_count)

    if bronze_count != raw_count:
        raise ValueError(
            f"Record count mismatch: "
            f"raw = {raw_count}, bronze = {bronze_count}"
        )
    
    valid_machines_df = (
        spark.read
        .parquet(str(MACHINES_BRONZE_DIR))
        .select("machine_id")
        .distinct()
    )

    invalid_orders_df = bronze_orders_df.join(
        valid_machines_df,
        on = "machine_id",
        how = "left_anti"
    )

    invalid_count = invalid_orders_df.count()

    print("Orders with invalid machine id:", invalid_count)

    invalid_orders_df.select(
        "order_id",
        "machine_id"
    ).show(5, truncate = False)

    duplicate_orders = (
        bronze_orders_df
        .groupBy("order_id")
        .count()
        .filter("count > 1")
        .count()
    )

    print("Duplicate production order IDs:", duplicate_orders)

finally:
    spark.stop()
