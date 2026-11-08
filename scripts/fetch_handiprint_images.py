"""Download the Handiprint scans used in this study from the public ShoeCase record and verify them.

Only the scans listed in the canonical split manifest are extracted, and each one
is checked against the SHA-256 recorded in that manifest.

Usage:
    python scripts/fetch_handiprint_images.py --project-root /path/to/YOUR_PROJECT

YOUR_PROJECT/data/split_manifest_final.csv must already exist. Scans are written to
YOUR_PROJECT/data/Handiprint_images/ at the paths given by the manifest's matched_path.
"""
import argparse
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

ARTICLE = "https://api.figshare.com/v2/articles/22814438/files?page_size=100"
ZIP_NAME = "Handiprint Images.zip"
USED_SPLITS = {"train", "val", "test"}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--zip-path", type=Path, help="Reuse an already downloaded Handiprint Images.zip")
    args = parser.parse_args()

    data = args.project_root.resolve() / "data"
    with open(data / "split_manifest_final.csv", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["split"] in USED_SPLITS]
    print(f"Scans listed in the manifest: {len(rows)}")

    zip_path = args.zip_path or data / ZIP_NAME
    if not zip_path.exists():
        with urllib.request.urlopen(ARTICLE) as response:
            files = json.load(response)
        url = next(f["download_url"] for f in files if f["name"] == ZIP_NAME)
        print(f"Downloading {ZIP_NAME} (about 2.1 GB) to {zip_path} ...")
        with urllib.request.urlopen(url) as response, open(zip_path, "wb") as out:
            shutil.copyfileobj(response, out, length=1 << 22)

    image_dir = data / "Handiprint_images"
    absent, mismatched = [], []
    with zipfile.ZipFile(zip_path) as archive:
        by_name = {Path(n).name: n for n in archive.namelist() if n.lower().endswith((".tif", ".tiff"))}
        for row in rows:
            member = by_name.get(Path(row["matched_path"]).name)
            if member is None:
                absent.append(row["matched_path"])
                continue
            target = image_dir / row["matched_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
            if sha256(target) != row["sha256"]:
                mismatched.append(row["matched_path"])

    print(f"Extracted: {len(rows) - len(absent)} | not in public zip: {len(absent)} | SHA-256 mismatches: {len(mismatched)}")
    if absent or mismatched:
        raise SystemExit(f"Problem files: {absent[:5]} {mismatched[:5]}")
    print("All scans match the manifest.")


if __name__ == "__main__":
    main()
