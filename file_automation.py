"""
Python File Handling & Automation
---------------------------------
Demonstrates:
  1. Reading and writing TXT and CSV files
  2. Automating file operations (rename, move, copy, delete)
  3. Error handling with try-except
  4. Explaining the logic in comments

Run:  python file_automation.py
"""

import csv
import os
import shutil
from pathlib import Path

# ---------------------------------------------------------------
# Folder layout (all created next to this script)
#   workspace/input/      -> original files
#   workspace/output/     -> generated files
#   workspace/archive/    -> files moved here after processing
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent / "workspace"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
ARCHIVE_DIR = BASE_DIR / "archive"


def setup_workspace():
    """Create folders and sample input files so the script runs out of the box."""
    try:
        # exist_ok=True means no error if the folder already exists
        for folder in (INPUT_DIR, OUTPUT_DIR, ARCHIVE_DIR):
            folder.mkdir(parents=True, exist_ok=True)

        # Sample TXT file
        txt_path = INPUT_DIR / "notes.txt"
        if not txt_path.exists():
            txt_path.write_text(
                "Python makes file handling easy.\n"
                "Automation saves time.\n"
                "Always handle errors gracefully.\n",
                encoding="utf-8",
            )

        # Sample CSV file
        csv_path = INPUT_DIR / "students.csv"
        if not csv_path.exists():
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "subject", "marks"])
                writer.writerows([
                    ["Aarav", "Python", 88],
                    ["Diya", "Python", 92],
                    ["Kabir", "Python", 74],
                    ["Meera", "Python", 65],
                ])
        print("[OK] Workspace ready:", BASE_DIR)
    except OSError as err:
        print(f"[ERROR] Could not set up workspace: {err}")
        raise


# ---------------------------------------------------------------
# 1. TXT read / write
# ---------------------------------------------------------------
def read_text_file(path):
    """Read a text file and return its lines (without newline characters)."""
    try:
        # 'with' closes the file automatically, even if an error occurs
        with open(path, "r", encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
    except PermissionError:
        print(f"[ERROR] No permission to read: {path}")
    except UnicodeDecodeError:
        print(f"[ERROR] Could not decode file (not UTF-8?): {path}")
    return []  # safe fallback so the caller doesn't crash


def write_text_file(path, lines):
    """Write a list of strings to a text file, one per line."""
    try:
        # "w" mode creates the file, or overwrites it if it already exists
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"[OK] Wrote {len(lines)} lines -> {path.name}")
    except OSError as err:
        print(f"[ERROR] Could not write {path}: {err}")


# ---------------------------------------------------------------
# 2. CSV read / write
# ---------------------------------------------------------------
def read_csv_file(path):
    """Read a CSV into a list of dictionaries (header row = keys)."""
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"[ERROR] CSV not found: {path}")
        return []


def write_csv_file(path, rows, fieldnames):
    """Write a list of dictionaries to a CSV file."""
    try:
        # newline="" prevents blank lines between rows on Windows
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] Wrote {len(rows)} rows -> {path.name}")
    except OSError as err:
        print(f"[ERROR] Could not write {path}: {err}")


# ---------------------------------------------------------------
# 3. Processing logic (uses the read/write helpers)
# ---------------------------------------------------------------
def process_text():
    """Read notes.txt, convert to uppercase, add line numbers, save result."""
    lines = read_text_file(INPUT_DIR / "notes.txt")
    # enumerate(..., start=1) gives us line numbers beginning at 1
    processed = [f"{i}. {line.upper()}" for i, line in enumerate(lines, start=1)]
    write_text_file(OUTPUT_DIR / "notes_processed.txt", processed)


def process_csv():
    """Read students.csv, add a 'grade' column based on marks, save result."""
    rows = read_csv_file(INPUT_DIR / "students.csv")
    for row in rows:
        try:
            marks = int(row["marks"])  # CSV values are strings -> convert
        except (ValueError, KeyError):
            # Bad or missing marks: don't crash, just flag the row
            row["grade"] = "INVALID"
            continue

        # Simple grading rule
        if marks >= 90:
            row["grade"] = "A"
        elif marks >= 75:
            row["grade"] = "B"
        elif marks >= 60:
            row["grade"] = "C"
        else:
            row["grade"] = "F"

    write_csv_file(OUTPUT_DIR / "students_graded.csv", rows,
                   fieldnames=["name", "subject", "marks", "grade"])


# ---------------------------------------------------------------
# 4. File automation: rename, copy, move
# ---------------------------------------------------------------
def rename_files_with_prefix(folder, prefix):
    """Rename every file in `folder` by adding a prefix (e.g. 'done_')."""
    for item in folder.iterdir():
        if item.is_file() and not item.name.startswith(prefix):
            new_path = item.with_name(prefix + item.name)
            try:
                item.rename(new_path)
                print(f"[OK] Renamed: {item.name} -> {new_path.name}")
            except OSError as err:
                print(f"[ERROR] Rename failed for {item.name}: {err}")


def move_files(src_folder, dest_folder, extension=None):
    """Move files from src to dest. Optionally filter by extension (e.g. '.csv')."""
    for item in src_folder.iterdir():
        if not item.is_file():
            continue
        if extension and item.suffix.lower() != extension.lower():
            continue  # skip files that don't match the filter
        try:
            # shutil.move works across folders and drives
            shutil.move(str(item), str(dest_folder / item.name))
            print(f"[OK] Moved: {item.name} -> {dest_folder.name}/")
        except (shutil.Error, OSError) as err:
            print(f"[ERROR] Move failed for {item.name}: {err}")


def demo_error_handling():
    """Show that errors are caught and reported instead of crashing the script."""
    print("\n--- Error handling demo ---")
    read_text_file(INPUT_DIR / "does_not_exist.txt")  # triggers FileNotFoundError
    try:
        os.remove(INPUT_DIR / "ghost.txt")
    except FileNotFoundError:
        print("[ERROR] Tried to delete a file that doesn't exist (handled).")
    finally:
        # 'finally' always runs, whether or not an error happened
        print("[INFO] Cleanup check finished.")


# ---------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------
def main():
    print("=== Python File Handling & Automation ===\n")
    setup_workspace()

    print("\n--- Reading & writing TXT/CSV ---")
    process_text()
    process_csv()

    print("\n--- Automating file operations ---")
    rename_files_with_prefix(OUTPUT_DIR, "done_")   # rename
    move_files(OUTPUT_DIR, ARCHIVE_DIR)             # move

    demo_error_handling()

    print("\n--- Final archive contents ---")
    for f in sorted(ARCHIVE_DIR.iterdir()):
        print("  ", f.name)

    print("\nDone.")


if __name__ == "__main__":
    main()
