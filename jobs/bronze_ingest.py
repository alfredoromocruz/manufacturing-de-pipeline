from pathlib import Path
from pyspark.sql import SparkSession

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw_landing" / "machines.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "bronze" / "machines"
)

# Create Spark session
spark = (
    SparkSession.builder
    .appName("Manufacturing Bronze Ingestion")
    .master("local[2]")
    .getOrCreate()
)

try:
    # Read CSV as a Spark DataFrame
    machines_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .csv(str(INPUT_FILE))
    )

    # Explore data
    print("Total machines:", machines_df.count())

    machines_df.printSchema()
    machines_df.show(5, truncate = False)

    # Write Bronze data as Parquet
    machines_df.write \
        .mode("overwrite") \
        .parquet(str(OUTPUT_DIR))

    print(f"Bronze data saved at: {OUTPUT_DIR}")

    # Validate Bronze output
    bronze_df = spark.read.parquet(str(OUTPUT_DIR))

    print("Bronze records:", bronze_df.count())

    bronze_df.printSchema()

finally:
    spark.stop()