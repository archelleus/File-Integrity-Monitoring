import json
import argparse
import yaml
import os
import time
from scanner import scan_directory
from alerts import alert

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DB_FILE = "database.json"


# ---------------- CONFIG ----------------
def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            "monitor_path": "./test_dir",
            "ignore_extensions": [],
            "hash_algorithm": "sha256"
        }


# ---------------- DATABASE ----------------
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- CORE ----------------
def initialize(path, ignore_ext, algo):
    print(f"[*] Creating baseline for: {path}")
    data = scan_directory(path, ignore_ext, algo)
    save_db(data)
    print(f"[+] Baseline created with {len(data)} files.")


def scan(path, ignore_ext, algo):
    print(f"[*] Scanning directory: {path}")

    old_data = load_db()
    new_data = scan_directory(path, ignore_ext, algo)

    for file, hash_val in new_data.items():
        if file not in old_data:
            alert(f"NEW FILE: {file}")
        elif old_data[file] != hash_val:
            alert(f"MODIFIED: {file}")

    for file in old_data:
        if file not in new_data:
            alert(f"DELETED: {file}")

    print("[+] Scan complete.")


# ---------------- REAL-TIME WATCH ----------------
class WatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            alert(f"CREATED: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            alert(f"MODIFIED: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            alert(f"DELETED: {event.src_path}")


def watch(path):
    print(f"[*] Real-time monitoring started on: {path}")

    observer = Observer()
    observer.schedule(WatchHandler(), path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[!] Stopped monitoring.")

    observer.join()


# ---------------- MAIN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Integrity Monitoring System")

    parser.add_argument("--init", action="store_true", help="Create baseline")
    parser.add_argument("--scan", action="store_true", help="Scan for changes")
    parser.add_argument("--watch", action="store_true", help="Real-time monitoring")
    parser.add_argument("--path", type=str, help="Directory to monitor")

    args = parser.parse_args()
    config = load_config()

    path = args.path if args.path else config.get("monitor_path", "./test_dir")
    ignore_ext = config.get("ignore_extensions", [])
    algo = config.get("hash_algorithm", "sha256")

    if not os.path.exists(path):
        print(f"[ERROR] Path does not exist: {path}")
        exit(1)

    if not (args.init or args.scan or args.watch):
        print("Use --init, --scan, or --watch")
        exit(1)

    if args.init:
        initialize(path, ignore_ext, algo)

    if args.scan:
        scan(path, ignore_ext, algo)

    if args.watch:
        watch(path)