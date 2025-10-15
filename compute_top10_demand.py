#!/usr/bin/env python3
"""Compare daily averages with average peak values and list top 10 crops by demand.

Rules:
- Load `day_averages.csv` (crop,average,count).
- Load `crop_average_peak_values.csv` (Crop,Average_Peak_Value).
- For crops present in both, if daily average >= Average_Peak_Value, consider it "meets/exceeds threshold".
- Rank those crops by daily average descending and output top 10 to `top10_by_demand.csv`.
"""
import csv
import os
from typing import Dict, Tuple, List


def load_day_averages(path: str) -> Dict[str, Tuple[float, int]]:
    """Return dict mapping normalized crop -> (average, count).

    Keeps the original crop casing separately is handled later when writing output.
    """
    d = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            crop = (r.get("crop") or r.get("Crop") or "").strip()
            avg_str = (r.get("average") or "").strip()
            count_str = (r.get("count") or "").strip()
            if not crop:
                continue
            try:
                avg = float(avg_str) if avg_str not in (None, "", " ") else None
            except Exception:
                avg = None
            try:
                cnt = int(count_str) if count_str not in (None, "", " ") else 0
            except Exception:
                cnt = 0
            key = crop.lower()
            # store as (avg, count) - if crop appears multiple times under different casing,
            # we will merge using weighted average downstream
            d.setdefault(key, []).append((crop, avg, cnt))
    return d


def load_peak_values(path: str) -> Dict[str, float]:
    d = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            crop = (r.get("Crop") or r.get("crop") or "").strip()
            val = (r.get("Average_Peak_Value") or r.get("average_peak_value") or "").strip()
            if not crop:
                continue
            try:
                v = float(val)
            except Exception:
                continue
            d[crop.lower()] = v
    return d


def compute_top10(day_averages_path: str, peak_values_path: str) -> List[Tuple[str, float, float]]:
    # day: normalized key -> list of (orig_name, avg, count)
    day = load_day_averages(day_averages_path)
    peak = load_peak_values(peak_values_path)
    merged = {}
    # Merge duplicates (case-insensitive). Use weighted average by count where possible.
    for key, entries in day.items():
        total_weighted = 0.0
        total_count = 0
        chosen_name = entries[0][0]
        for orig, avg, cnt in entries:
            if avg is None or cnt == 0:
                # if avg is present but count is missing, treat as single sample
                if avg is not None and cnt == 0:
                    total_weighted += avg
                    total_count += 1
                continue
            total_weighted += avg * cnt
            total_count += cnt
            chosen_name = orig  # keep last seen original casing
        if total_count > 0:
            merged[key] = (chosen_name, total_weighted / total_count, total_count)
        else:
            # fallback: try to take any single avg if present
            picked = None
            for orig, avg, cnt in entries:
                if avg is not None:
                    picked = (orig, avg, cnt or 0)
                    break
            if picked:
                merged[key] = picked

    # Simple deduplication: merge keys that are anagrams (sorted letters equal).
    # This handles cases like 'Jowar' and 'jawor' (same letters, different spelling/casing).
    final_merged = {}
    for key, (orig_name, avg, cnt) in merged.items():
        s = "".join(sorted(key))
        found = None
        for existing_key in list(final_merged.keys()):
            if "".join(sorted(existing_key)) == s:
                found = existing_key
                break
        if found:
            prev_orig, prev_avg, prev_cnt = final_merged[found]
            # weighted average
            total_cnt = prev_cnt + cnt
            if total_cnt > 0:
                total_weight = (prev_avg or 0.0) * prev_cnt + (avg or 0.0) * cnt
                new_avg = total_weight / total_cnt
            else:
                new_avg = prev_avg or avg
            final_merged[found] = (prev_orig, new_avg, total_cnt)
        else:
            final_merged[key] = (orig_name, avg, cnt)

    matched = []
    for key, (orig_name, avg, cnt) in final_merged.items():
        if avg is None:
            continue
        if key not in peak:
            continue
        threshold = peak[key]
        if avg >= threshold:
            matched.append((orig_name, avg, threshold))

    # sort by daily avg descending
    matched.sort(key=lambda x: x[1], reverse=True)
    return matched[:10]


def write_top10(root: str, rows: List[Tuple[str, float, float]]):
    out = os.path.join(root, "top10_by_demand.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["crop", "daily_average", "peak_threshold"])
        for crop, avg, thr in rows:
            writer.writerow([crop, f"{avg:.6f}", f"{thr:.6f}"])
    return out


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    day_path = os.path.join(root, "day_averages.csv")
    peak_path = os.path.join(root, "crop_average_peak_values.csv")
    rows = compute_top10(day_path, peak_path)
    out = write_top10(root, rows)
    print(f"Wrote {out}; top {len(rows)} crops:")
    for i, (c, a, t) in enumerate(rows, start=1):
        print(f"{i}. {c} — daily avg: {a:.3f}, threshold: {t:.3f}")


if __name__ == "__main__":
    main()
