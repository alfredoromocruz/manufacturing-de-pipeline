from pathlib import Path
import random
import csv

# Reproducibility
RNG = random.Random(42)

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_landing"

# Create the landing directory
RAW_DATA_DIR.mkdir(parents = True, exist_ok = True)

print(f"Project directory: {PROJECT_ROOT}")
print(f"Landing zone: {RAW_DATA_DIR}")

# machine specifications
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