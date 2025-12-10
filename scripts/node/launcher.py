import subprocess
import os
import sys

# --- Configuration ---
PYTHON_EXEC = "/usr/bin/env python3"
DETECT_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/sensor_detection/detect.py"
SCHEDULER_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/scheduler.py"

# --- Launcher Logic ---
def run_startup_sequence():
    print("--- Starting BEAMNode Service Sequence ---")
    
    # 1. RUN DETECT.PY (ONCE) - Synchronous execution
    print(f"Executing one-time startup script: {os.path.basename(DETECT_SCRIPT)}")
    
    try:
        # Blocks until detect.py finishes
        result = subprocess.run([PYTHON_EXEC, DETECT_SCRIPT], 
                                stdout=sys.stdout, 
                                stderr=sys.stderr, 
                                check=True)
        print(f"SUCCESS: {os.path.basename(DETECT_SCRIPT)} completed successfully with return code {result.returncode}")
        
    except subprocess.CalledProcessError as e:
        print(f"CRITICAL FAILURE: {os.path.basename(DETECT_SCRIPT)} failed to run. Return code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR during {os.path.basename(DETECT_SCRIPT)} execution: {e}")
        sys.exit(1)

    # 2. LAUNCH SCHEDULER.PY (CONTINUOUSLY) - Asynchronous execution
    print(f"\nLaunching continuous service: {os.path.basename(SCHEDULER_SCRIPT)}")
    
    try:
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

if __name__ == "__main__":
    run_startup_sequence()
