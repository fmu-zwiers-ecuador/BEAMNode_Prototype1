**Basic Info**

* **Task Title:** Write queue script  
* **Student(s):** Jaylen Small, Noel Challa  
* **Mentor/Reviewer:** Dr. Zwiers and Raiz Mohammed  
* **Date Started / Completed:** October 20th **\-** November 1st  
* **Status:** Done  
* **GitHub Link:** [queue\_data\_request.py](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/scripts/node/shipping_queuing/queue_data_request.py)

---

**1\) Summary**

Once a day, this script will check the connection of all connected nodes, sort them, then request a data transfer of nodes with the strongest connection to the weakest connection.

---

**2\) Goals**

* Main goal: For the supervisor to request collected data from all connected nodes and transfer the data from the nodes to the supervisor   
* How do we know it works? (e.g., can send message between Pis, script runs without error): The scripts runs without error and the logs return the expected output

---

**3\) Setup**

*List what you used and how to set it up.*

* Hardware (Pi model, sensors, etc.): Raspberry Pi  
* Software (OS, Python version, key packages): Python3, BATMAN Protocol, SSH keys  
* Install/run steps:

python3 scripts/shipping\_queuing/queue\_data\_request.py  
---

**4\) Method**

* In the script the following commands were used: 

  * ping \-c 3 \-W 1 {ip} To get the ping connection for every node to sort from strongest to weakest connection

  * rsync \-avz pi@{ip}:{remote\_path} {local\_path} to handle the data transfer between the supervisor and the nodes

* Using those commands together, this script ensures that each node is queued to transfer data based on how strong its ping connection is  
* In the configuration table, each node has a hardcoded ip address in the script as well

---

**5\) Code**

* Main script(s): scripts/shipping\_queue/queue\_data\_request.py  
* Example run:

\=== Starting daily data queue \===   
node1 (192.168.1.1) \-\> 11.702 ms   
node2 (192.168.1.2) \-\> 17.411 ms   
node3 (192.168.1.3) \-\> 103.644 ms   
node4 (192.168.1.4) \-\> 23.79 ms   
node5 (192.168.1.5) \-\> 8.789 ms   
Best connection: node5 (8.789 ms) Requesting data from nodes (8.789 ms)...   
bash: warning: setlocale: LC\_ALL: cannot change locale (en\_US.UTF-8): No such file or directory receiving incremental file list

sent 24 bytes received 803 bytes 551.33 bytes/sec total size is 295, 766,228 speedup is 357, 637.52  
Successfully synced data from node1 (192.168.1.1)  
Requesting data from node2 (17.411 ms) ... receiving incremental file list

sent 24 bytes received 803 bytes  
330.80 bytes/sec  
total size is 295, 766,228 speedup is 357,637.52  
Successfully synced data from node2 (192.168.1.2)  
Requesting data from node4 (23.79 ms) ...  
bash: warning: setlocale: LC\_ALL: cannot change locale (en\_US.UTF-8): No such le or directory receiving incremental file list

sent 24 bytes received 803 bytes 330.80 bytes/sec total size is 295, 766, 228 speedup is 357, 637.52  
Successfully synced data from node2 (192.168.1.2)  
Requesting data from node4 (23.79 ms)...  
bash: warning: setlocale: LC\_ALL: cannot change locale (en\_US.UTF-8): No such file or directory receiving incremental file list

sent 24 bytes received 831 bytes 570.00 bytes/sec total size is 295, 766,700 speedup is 345,925.96  
Successfully synced data from node4 (192.168.1.4)  
Requesting data from node3 (103.644 ms)...  
bash: warning: setlocale: LC\_ALL: cannot change locale (en\_US.UTF-8): No such  
file or directory receiving incremental file list

sent 24 bytes received 829 bytes  
341.20 bytes/sec  
total size is 295, 766, 232 speedup is 346, 736.50  
Successfully synced data from node3 (192.168.1.3)  
\=== Data queue complete \===

* Important snippet:

def main():  
    log("=== Starting daily data queue \===")

    \# Measure latency for all nodes  
    latencies \= {}  
    for name, ip in NODES.items():  
        latency \= ping\_latency(ip)  
        latencies\[name\] \= latency  
        log(f"{name} ({ip}) \-\> {latency if latency else 'unreachable'} ms")

     \# Sort nodes by latency (ignore unreachable)  
    reachable \= {n: l for n, l in latencies.items() if l is not None}  
    sorted\_nodes \= sorted(reachable.items(), key\=lambda x: x\[1\])

    if not sorted\_nodes:  
        log("No reachable nodes. Exiting.")  
        return

    log(f"Best connection: {sorted\_nodes\[0\]\[0\]} ({sorted\_nodes\[0\]\[1\]} ms)")

    \# Request data from best node first  
    for name, latency in sorted\_nodes:  
        log(f"Requesting data from {name} ({latency} ms)...")  
        rsync\_data(NODES\[name\], name)  
        time.sleep(2)  \# small delay between transfers

    log("=== Data queue complete \===\\n")

---

**6\) Testing**

* How you tested it (manual demo, script, unit tests): I would run every command individually that I used in the script to ensure that it would return the expected results so that everything in the script will interact with minimal issues  
* Results (pass/fail, screenshots, notes): Since I test everything thing individually, the script ran without issue the first try

---

**7\) Lessons & Next Steps**

* In order to bypass entering the password when using the rsync command, I had to set up ssh keys for each pi, here is how I did it(using ip address 192.168.1.4 as an example, but replace this with whatever ip address you need):

  * Step 1 \- Generate an SSH key: ssh-keygen \-t ed25519 \-C "pi@192.168.1.4"

  * Step 2 \- Copy the public key to the remote server: ssh-copy-id pi@192.168.1.4

  * Step 3 \- This is optional but you can test the ssh command to see if it’ll let you bypass the password or not: ssh pi@192.168.1.4

  * Step 4 \- Then run your rsync normally: rsync \-avz pi@192.168.1.4:/home/pi/data /home/pi/supervisor

---

**8\) References**

* Github: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/) 

* Generating an SSH key tutorial: [https://www.unixtutorial.org/how-to-generate-ed25519-ssh-key/](https://www.unixtutorial.org/how-to-generate-ed25519-ssh-key/) 

