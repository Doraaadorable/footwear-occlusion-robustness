"""Set up the Handiprint inputs from public sources and verify them.

1. Copies the canonical split manifest from splits/ in this repository into
   YOUR_PROJECT/data/ (checking its SHA-256).
2. Downloads Handiprint_database.xlsx and Handiprint Images.zip from the public
   ShoeCase record.
3. Extracts only the scans listed in the manifest and checks each one against the
   SHA-256 recorded there.

Usage:
    python scripts/fetch_handiprint_images.py --project-root /path/to/YOUR_PROJECT
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
METADATA_NAME = "Handiprint_database.xlsx"
REPO_MANIFEST = Path(__file__).resolve().parents[1] / "splits" / "split_manifest_final.csv"
MANIFEST_SHA256 = "20f942824a8c45c102837998cf2eb0b9f6d8cc9b243fa1ae87bef3db4f03d11d"
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
    data.mkdir(parents=True, exist_ok=True)

    manifest = data / "split_manifest_final.csv"
    if not manifest.exists():
        shutil.copyfile(REPO_MANIFEST, manifest)
        print(f"Copied the canonical manifest to {manifest}")
    if sha256(manifest) != MANIFEST_SHA256:
        raise SystemExit(f"{manifest} is not the canonical split manifest (SHA-256 mismatch).")

    files = None
    if not (data / METADATA_NAME).exists():
        with urllib.request.urlopen(ARTICLE) as response:
            files = json.load(response)
        url = next(f["download_url"] for f in files if f["name"] == METADATA_NAME)
        with urllib.request.urlopen(url) as response, open(data / METADATA_NAME, "wb") as out:
            shutil.copyfileobj(response, out)
        print(f"Downloaded {METADATA_NAME}")

    with open(manifest, newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["split"] in USED_SPLITS]
    print(f"Scans listed in the manifest: {len(rows)}")

    zip_path = args.zip_path or data / ZIP_NAME
    if not zip_path.exists():
        if files is None:
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
