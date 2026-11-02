# Manufacturing Analytics Data Pipeline

## Project Overview

An end-to-end Data Engineering project designed to simulate
manufacturing operations in the automotive industry.

The pipeline processes synthetic manufacturing data to monitor
machine performance, production efficiency, and product quality.

## Business Objectives

- Monitor manufacturing equipment performance.
- Analyze production output across shifts.
- Identify downtime and operational inefficiencies.
- Measure quality defects.
- Calculate manufacturing KPIs, including OEE.

## Data Sources

1. Machine Master Data
2. Machine Sensor Logs
3. Production Orders
4. Quality Inspection Records

All datasets are synthetically generated for educational purposes.

## Technology Stack

### Currently Implemented

- Python
- Apache Spark (PySpark)
- Docker
- Git and GitHub

### Planned Technologies

- Apache Airflow
- PostgreSQL
- AWS S3

## Data Architecture

Landing Zone → Bronze → Silver → Gold → Data Warehouse

## Project Status

In Development

## Getting Started

This section explains how to generate synthetic manufacturing data
and execute the Bronze ingestion pipeline using Apache Spark and Docker.

### Prerequisites

- Python 3.12 or newer
- Docker Desktop with WSL 2 enabled (Windows)
- Git

### 1. Generate Synthetic Data

Run the following command from the project's root directory:

```powershell
python .\data_generator\generate_synthetic_data.py
```

The script generates four datasets:

- `data/raw_landing/machines.csv`
- `data/raw_landing/sensors/machine_sensor_logs.csv`
- `data/raw_landing/production_orders/production_orders.csv`
- `data/raw_landing/quality_checks/quality_inspections.csv`

### 2. Download Apache Spark Docker Image

```powershell
docker pull apache/spark:4.2.0-python3
```

This image provides a Linux environment with Apache Spark and Python.

### 3. Run Bronze Ingestion

Execute the following command from the project directory
using PowerShell:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace apache/spark:4.2.0-python3 /opt/spark/bin/spark-submit jobs/bronze_ingest.py
```

The command mounts the local project directory into the container
and executes the PySpark ingestion job.

### 4. Validate Bronze Output

The current ingestion job processes machine master data.

Expected results:

```text
Total machines: 12
Bronze data saved at: /workspace/data/bronze/machines
Bronze records: 12
```

The resulting Parquet files are stored locally in:

```text
data/bronze/machines/
```

### Data Storage

Generated CSV and Parquet files are excluded from Git tracking.

The repository stores the source code required to reproduce
the datasets and the pipeline execution.
