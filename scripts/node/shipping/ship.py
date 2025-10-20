import os
import shutil
import tarfile
import hashlib
import datetime

 
# config

DATA_DIR = "/home/pi/data"             # where your node data lives
SENDING_DIR = "/home/pi/sending"       # where compressed data is sent/stored
DATE_STR = datetime.datetime.utcnow().strftime("%Y%m%d")
ARCHIVE_NAME = f"beam_data_{DATE_STR}.tar.gz"
ARCHIVE_PATH = os.path.join(SENDING_DIR, ARCHIVE_NAME)
CHECKSUM_PATH = ARCHIVE_PATH + ".sha256"


# helper functions
def ensure_directory(path):
    """Checks if directory exists."""
    os.makedirs(path, exist_ok=True)

def compute_checksum(file_path):
    """Compute SHA-256 checksum for the given file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# MAIN PROCESS
def ship_data():
    print("[SHIP] Starting daily shipment process...")
    ensure_directory(SENDING_DIR)

    # copies /data to /sending/data
    node_copy_path = os.path.join(SENDING_DIR, "data")
    if os.path.exists(node_copy_path):
        print("[SHIP] Cleaning previous /sending/data folder...")
        shutil.rmtree(node_copy_path)

    shutil.copytree(DATA_DIR, node_copy_path)
    print(f"[SHIP] Copied {DATA_DIR} → {node_copy_path}")

    # compress into .tar.gz
    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(node_copy_path, arcname="data")
    print(f"[SHIP] Compressed data → {ARCHIVE_PATH}")

    # compute and save checksum
    checksum_value = compute_checksum(ARCHIVE_PATH)
    with open(CHECKSUM_PATH, "w") as cfile:
        cfile.write(checksum_value)
    print(f"[SHIP] Checksum saved → {CHECKSUM_PATH}")

    # verify checksum before deletion
    verify_checksum = compute_checksum(ARCHIVE_PATH)
    if verify_checksum == checksum_value:
        print("[SHIP] Checksum verified. Cleaning up /sending/data...")
        shutil.rmtree(node_copy_path)
    else:
        print("[SHIP] Checksum mismatch. Keeping /sending/data for safety.")

    print("[SHIP] Shipment process complete.\n")

if __name__ == "__main__":
    ship_data()
