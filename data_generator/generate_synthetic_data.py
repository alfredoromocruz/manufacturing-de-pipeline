from pathlib import Path
import random
import csv
from datetime import datetime, timedelta
from collections import defaultdict

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

# Calculate running time per machine and shift
runtime_by_shift = defaultdict(int)

with sensor_file.open("r", newline = "", encoding = "utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        reading_time = datetime.fromisoformat(row["timestamp"])

        shift_number = reading_time.hour // 8 + 1

        key = (
            row["machine_id"],
            reading_time.date().isoformat(),
            f"S{shift_number}"
        )

        if row["status"] == "running":
            runtime_by_shift[key] += INTERVAL_MINUTES
        else:
            runtime_by_shift[key] += 0

print(f"Machine-shift combinations: {len(runtime_by_shift)}")

for (machine_id, date, shift_id), minutes in list(
    runtime_by_shift.items()
)[:6]:

    print(
        f"{machine_id} | {date} | "
        f"{shift_id} | {minutes} running minutes"
    )

# Generate production orders
PRODUCTION_DIR = RAW_DATA_DIR / "production_orders"
PRODUCTION_DIR.mkdir(parents = True, exist_ok = True)

production_file = PRODUCTION_DIR / "production_orders.csv"

PRODUCTS = ["P001", "P002", "P003"]

order_count = 0

with production_file.open("w", newline = "", encoding = "utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames = [
            "order_id",
            "product_id",
            "machine_id",
            "shift_id",
            "quantity_produced",
            "start_time",
            "end_time",
            "planned_production_minutes"
        ]
    )

    writer.writeheader()

    for day_offset in range(SIMULATION_DAYS):

        production_date = START_TIME + timedelta (days = day_offset)

        for shift_number in range(1, 4):

            shift_id = f"S{shift_number}"

            shift_start = production_date + timedelta(
                hours = (shift_number - 1) * 8
            )

            shift_end = shift_start + timedelta(hours = 8)

            for machine in machines:

                machine_id = machine["machine_id"]

                key = (
                    machine_id,
                    production_date.date().isoformat(),
                    shift_id
                )

                running_minutes = runtime_by_shift[key]

                ideal_cycle_time = machine["ideal_cycle_time_seconds"]

                theoretical_quantity = (
                    running_minutes * 60 / ideal_cycle_time
                )

                performance_factor = RNG.uniform(0.80, 0.98)

                quantity_produced = int(
                    theoretical_quantity * performance_factor
                )

                order_count += 1

                writer.writerow({
                    "order_id": f"ORD{order_count:05d}",
                    "product_id": RNG.choice(PRODUCTS),
                    "machine_id": machine_id,
                    "shift_id": shift_id,
                    "quantity_produced": quantity_produced,
                    "start_time": shift_start.isoformat(),
                    "end_time": shift_end.isoformat(),
                    "planned_production_minutes": 480
                })

print(f"Successfully generated {order_count} production orders.")
print(f"Production file saved at: {production_file}")