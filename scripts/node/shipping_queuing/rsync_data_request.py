import subprocess
import os

def rsync_data_request(source: str, destination: str) -> bool:
    """
    Synchronize files using rsync.

    Args:
        source (str): Source path (local or remote, e.g., 'pi@192.168.0.10:/home/pi/data/')
        destination (str): Local destination directory

    Returns:
        bool: True if rsync succeeded, False otherwise
    """
    # Ensure destination directory exists
    os.makedirs(destination, exist_ok=True)

    # Build rsync command
    rsync_cmd = [
        "rsync", "-avz", "--partial", "--timeout=20",
        source,
        destination
    ]

    # Run rsync
    try:
        result = subprocess.run(
            rsync_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0

    except Exception:
        return False
