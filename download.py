import csv
import re
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


URL = "https://www.ssa.gov/oact/babynames/names.zip"
PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_ARCHIVE = PROJECT_DIR / "names.zip"
OUTPUT = PROJECT_DIR / "ssa-baby-names.csv"


def combine_archive(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        yearly_files = []
        for filename in archive.namelist():
            match = re.fullmatch(r"yob(\d{4})\.txt", Path(filename).name)
            if match:
                yearly_files.append((int(match.group(1)), filename))

        if not yearly_files:
            raise ValueError("The archive contains no yearly name files.")

        with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["year", "name", "sex", "count"])

            for year, filename in sorted(yearly_files):
                with archive.open(filename) as year_file:
                    for line in year_file:
                        name, sex, count = line.decode("utf-8").strip().split(",")
                        writer.writerow([year, name, sex, count])


def main():
    if LOCAL_ARCHIVE.exists():
        combine_archive(LOCAL_ARCHIVE)
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "names.zip"
            with urllib.request.urlopen(URL, timeout=60) as response:
                with archive_path.open("wb") as archive_file:
                    shutil.copyfileobj(response, archive_file)
            combine_archive(archive_path)

    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
