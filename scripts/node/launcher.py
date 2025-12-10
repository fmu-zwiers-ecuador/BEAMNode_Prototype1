import subprocess
import os
import sys

# --- Configuration ---
PYTHON_EXEC = "/usr/bin/env python3"

# Scripts paths
DETECT_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/sensor_detection/detect.py"
SCHEDULER_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/scheduler.py"

# --- Launcher Logic ---
def run_startup_sequence():
    print("--- Starting BEAMNode Service Sequence ---")
    
    # 1. RUN DETECT.PY (ONCE)
    print(f"Executing one-time startup script: {os.path.basename(DETECT_SCRIPT)}")
    
    try:
        # subprocess.run waits for the script to finish and returns a CompletedProcess object.
        # This ensures the scheduler doesn't start until detection is complete.
        result = subprocess.run([PYTHON_EXEC, DETECT_SCRIPT], 
                                stdout=sys.stdout, 
                                stderr=sys.stderr, 
                                check=True) # check=True raises an error if the script fails
        print(f"SUCCESS: {os.path.basename(DETECT_SCRIPT)} completed successfully with return code {result.returncode}")
        
    except subprocess.CalledProcessError as e:
        print(f"CRITICAL FAILURE: {os.path.basename(DETECT_SCRIPT)} failed to run. Return code: {e.returncode}")
        # If the one-time script fails, the launcher exits. 
        # systemd's 'Restart=always' will attempt to run the launcher again.
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR during {os.path.basename(DETECT_SCRIPT)} execution: {e}")
        sys.exit(1)


    # 2. LAUNCH SCHEDULER.PY (CONTINUOUSLY)
    print(f"\nLaunching continuous service: {os.path.basename(SCHEDULER_SCRIPT)}")
    
    try:
        # subprocess.Popen starts the script in the background (non-blocking)
        scheduler_process = subprocess.Popen([PYTHON_EXEC, SCHEDULER_SCRIPT], 
                                             stdout=sys.stdout,
                                             stderr=sys.stderr)
        
        print(f"SUCCESS: {os.path.basename(SCHEDULER_SCRIPT)} started with PID {scheduler_process.pid}")
        
        # 3. MONITOR AND WAIT FOR SCHEDULER.PY
        print("\nMonitoring scheduler process. Launcher will stay active...")
        scheduler_process.wait()
        
    except Exception as e:
        print(f"CRITICAL FAILURE: Error launching or monitoring {os.path.basename(SCHEDULER_SCRIPT)}: {e}")
        sys.exit(1)
        
    print(f"Launcher script finished. {os.path.basename(SCHEDULER_SCRIPT)} exited.")
    # If scheduler.py exits, systemd will see the launcher exit and restart the whole sequence.

if __name__ == "__main__":
    run_startup_sequence()
