import subprocess
import os
import sys

# --- Configuration ---
# Define the full paths to the scripts you want to run.
# These paths are what the launcher uses to start the child processes.
SCRIPTS_TO_RUN = [
    "/home/pi/BEAMNode_Prototype1/scripts/node/sensor_detection/detect.py",
    "/home/pi/BEAMNode_Prototype1/scripts/node/scheduler.py",
]

# --- Launcher Logic ---
def run_scripts_in_parallel():
    python_exec = "/usr/bin/env python3"
    processes = []
    
    print("--- Starting BEAMNode Services ---")

    for script_path in SCRIPTS_TO_RUN:
        script_name = os.path.basename(script_path)
        print(f"Attempting to start: {script_name}")
        
        try:
            # Popen runs the script non-blocking (in parallel)
            process = subprocess.Popen([python_exec, script_path], 
                                     stdout=sys.stdout,
                                     stderr=sys.stderr)
            processes.append(process)
            print(f"SUCCESS: Started {script_name} with PID {process.pid}")
        except Exception as e:
            print(f"FAILURE: Error starting {script_name}: {e}")

    # Keep the main launcher script alive indefinitely by waiting on its child processes.
    print("\nAll processes initiated. Launcher running in monitoring mode...")
    
    try:
        # Wait for all child processes to complete (which should be never, if they run forever)
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\nLauncher interrupted. Terminating child processes...")
        for process in processes:
            process.terminate()
            
    print("Launcher script finished.")

if __name__ == "__main__":
    run_scripts_in_parallel()
