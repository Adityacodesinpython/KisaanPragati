#!/usr/bin/env python3
"""Compute average of the second column in each folder's Day.csv ignoring zeros.

Behavior:
- For each immediate subdirectory of the repo root, if it contains `Day.csv`, read it.
- Treat each data row as two columns (time, value). Ignore the time column and parse the second column as numeric.
- Ignore zero values and non-numeric entries. Average only the definite (non-zero numeric) values.
- Produce `day_averages.csv` in the repository root with columns: crop,average,count

This script is defensive: it skips leading metadata lines and will parse rows where the last field is numeric.
"""
import csv
import os
import math
from typing import List


def read_second_column_values(path: str) -> List[float]:
	"""Read a Day.csv and return list of non-zero numeric values from the second column.

	Assumes rows are CSV with at least two columns. Skips blank lines and non-numeric values.
	"""
	values: List[float] = []
	try:
		with open(path, "r", encoding="utf-8") as f:
			for raw in f:
				line = raw.strip()
				if not line:
					continue
				# Skip obvious metadata lines
				low = line.lower()
				if low.startswith("category:"):
					continue
				# Allow header lines like "Week,xxx" or "Time,xxx" to be skipped
				if low.startswith("week,") or low.startswith("time,"):
					continue
				# Now try to parse CSV columns
				if "," not in line:
					continue
				parts = [p.strip() for p in line.split(",")]
				if len(parts) < 2:
					continue
				# Per instruction: ignore the time column; take the other column as value
				val_str = parts[-1]
				try:
					num = float(val_str)
				except Exception:
					continue
				if num == 0:
					continue
				if math.isfinite(num):
					values.append(num)
	except FileNotFoundError:
		return []
	return values


def compute_averages(root_dir: str):
	results = []
	for name in sorted(os.listdir(root_dir)):
		full = os.path.join(root_dir, name)
		if not os.path.isdir(full):
			continue
		day_file = os.path.join(full, "Day.csv")
		if not os.path.isfile(day_file):
			continue
		vals = read_second_column_values(day_file)
		if vals:
			avg = sum(vals) / len(vals)
			results.append((name, avg, len(vals)))
		else:
			results.append((name, None, 0))
	return results


def write_csv(root_dir: str, rows):
	out_path = os.path.join(root_dir, "day_averages.csv")
	with open(out_path, "w", newline="", encoding="utf-8") as out:
		writer = csv.writer(out)
		writer.writerow(["crop", "average", "count"])
		for name, avg, count in rows:
			if avg is None:
				writer.writerow([name, "", count])
			else:
				writer.writerow([name, f"{avg:.6f}", count])
	return out_path


def main():
	root = os.path.dirname(os.path.abspath(__file__))
	rows = compute_averages(root)
	out = write_csv(root, rows)
	print(f"Wrote {out} with {len(rows)} rows")


if __name__ == "__main__":
	main()

