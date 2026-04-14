import os
from hasher import get_hash

def scan_directory(path, ignore_ext=None, algo="sha256"):
    file_hashes = {}

    for root, _, files in os.walk(path):
        for file in files:
            if ignore_ext and any(file.endswith(ext) for ext in ignore_ext):
                continue

            full_path = os.path.join(root, file)
            file_hashes[full_path] = get_hash(full_path, algo)

    return file_hashes