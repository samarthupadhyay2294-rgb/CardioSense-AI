"""
Extract sample ECG records from records100.zip into data/sample_ecg/.

Usage:
    py tools/extract_samples.py
    py tools/extract_samples.py 00001 00008
"""
import os
import sys
import zipfile

ZIP_PATH = os.path.join(os.path.dirname(__file__), "..", "records100.zip")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_ecg")

DEFAULT_IDS = ["00001"]


def extract(record_ids):
    if not os.path.exists(ZIP_PATH):
        print(f"Zip not found at {ZIP_PATH}. Skipping sample extraction.")
        return
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    with zipfile.ZipFile(ZIP_PATH) as z:
        for ecg_id in record_ids:
            prefix = f"records100/00000/{ecg_id}_lr"
            for ext in (".hea", ".dat"):
                member = prefix + ext
                try:
                    content = z.read(member)
                except KeyError:
                    print(f"  record {ecg_id}: {ext} not found, skipping")
                    continue
                dest = os.path.join(OUT_DIR, f"{ecg_id}_lr{ext}")
                with open(dest, "wb") as f:
                    f.write(content)
                print(f"  extracted {dest}")
    print(f"\nSamples ready in {os.path.abspath(OUT_DIR)}")


if __name__ == "__main__":
    ids = sys.argv[1:] or DEFAULT_IDS
    extract(ids)
