from pathlib import Path
import random
import csv
from datetime import datetime, timedelta

# Reproducibility
RNG = random.Random(42)

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_landing"

# Create the landing directory
RAW_DATA_DIR.mkdir(parents = True, exist_ok = True)

print(f"Project directory: {PROJECT_ROOT}")
print(f"Landing zone: {RAW_DATA_DIR}")

# Machine specifications
MACHINE_TYPES = [
    ("Stamping Press", 45),
    ("Welding Robot", 60),
    ("Painting Station", 120),
    ("Assembly Station", 90)
]

# Generate machine master data
machines = []

for line_number in range(1,4):
    for station_number, (machine_type, cycle_time) in enumerate(
        MACHINE_TYPES, start = 1
    ):
        machine_number = (line_number - 1) * 4 + station_number

        machines.append({
            "machine_id": f"M{machine_number:03d}",
            "line_id": f"L{line_number:02d}",
            "machine_type": machine_type,
            "ideal_cycle_time_seconds": cycle_time
        })

# Export machine data
output_file = RAW_DATA_DIR / "machines.csv"

with output_file.open("w", newline = "", encoding = "utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames = [
            "machine_id",
            "line_id",
            "machine_type",
            "ideal_cycle_time_seconds"
        ]
    )

    writer.writeheader()
    writer.writerows(machines)

print(f"Succesfully generated {len(machines)} machines.")
print(f"File saved at: {output_file}")

# Sensor simulation configuration
START_TIME = datetime(2026, 10, 1)

SIMULATION_DAYS = 7
INTERVAL_MINUTES = 5

SAMPLES_PER_MACHINE = (
    SIMULATION_DAYS * 24 * 60 // INTERVAL_MINUTES
)

# Machine operating states
STATUSES = ["running", "idle", "down"]

TRANSITION_WEIGHTS = {
    "running": [96, 3, 1],
    "idle": [35, 60, 5],
    "down": [15, 5, 80]
}

# Sensor ranges by operating state
SENSOR_RANGES = {
    "running": ((65, 95), (1.5, 4.5)),
    "idle": ((45, 65), (0.2, 1.0)),
    "down": ((30, 55), (0.0, 0.2))
}

# Create sensor landing directory
SENSOR_DIR = RAW_DATA_DIR / "sensors"
SENSOR_DIR.mkdir(parents = True, exist_ok = True)

sensor_file = SENSOR_DIR / "machine_sensor_logs.csv"

record_count = 0

with sensor_file.open("w", newline = "", encoding = "utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames = [
            "machine_id",
            "timestamp",
            "temperature_c",
            "vibration_mm_s",
            "status"
        ]
    )

    writer.writeheader()

    for machine in machines:

        status = "running"

        for step in range(SAMPLES_PER_MACHINE):

            timestamp = START_TIME + timedelta(
                minutes = step * INTERVAL_MINUTES
            )

            status = RNG.choices(
                STATUSES,
                weights = TRANSITION_WEIGHTS[status],
                k = 1
            )[0]

            temperature_range, vibration_range = SENSOR_RANGES[status]

            temperature = round(
                RNG.uniform(* temperature_range), 2
            )

            vibration = round(
                RNG.uniform(* vibration_range), 2
            )

            writer.writerow({
                "machine_id": machine["machine_id"],
                "timestamp": timestamp.isoformat(),
                "temperature_c": temperature,
                "vibration_mm_s": vibration,
                "status": status
            })

            record_count += 1

print(f"Succesfully generated {record_count} sensor readings.")
print(f"Sensor file saved at: {sensor_file}")