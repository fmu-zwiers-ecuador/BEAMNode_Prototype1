import subprocess
import logging
import re

def detect_batman():
    try:
        result = subprocess.run(
            ["sudo", "batctl", "o"],
            capture_output=True,
            text=True,  # ensures stdout is a string
            check=True  # raises CalledProcessError on failure
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print("Error calling batctl:")
        print(e.stderr)
        return -1

    except FileNotFoundError:
        print("batctl command not found.")
        return -1

# This function will loop through the BATMAN output and search for a 
# ([digits]) pattern and store it into a connections array
def find_connections(output):
    if output == -1:
        return "There are no avaliable connected sensors"
    
    connections = []
    found_connections = re.findall(r'\((\d+)\)', output)
    for connec_num in found_connections:
        connection = int(connec_num)
        connections.append(connection)
        
        connections.sort(reverse=True)
    return connections
    
batman_output = detect_batman()
print(find_connections(batman_output))
