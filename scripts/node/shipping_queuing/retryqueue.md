**Basic Info**

* **Task Title:** Write queue script  
* **Student(s):** Jaylen Small, Jackson Roberts  
* **Mentor/Reviewer:** Dr. Zwiers and Raiz Mohammed  
* **Date Started / Completed:** February 5th **\-** February 6th  
* **Status:** Done  
* **GitHub Link:** [retryqueue.py](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/scripts/node/shipping_queuing/retryqueue.py)

---

**1\) Summary**

This script requests and queues data from nodes via mDNS.

---

**2\) Goals**

* Main goal: For the supervisor to request collected data from all connected nodes and transfer the data from the nodes to the supervisor. Also to clear the shipping folder in every node after ther data is pulled.   
* How do we know it works? (e.g., can send message between Pis, script runs without error): The scripts runs without error and the logs return the expected output

---

**3\) Setup**

*List what you used and how to set it up.*

* Hardware (Pi model, sensors, etc.): Raspberry Pi  
* Software (OS, Python version, key packages): Python3, BATMAN Protocol, SSH keys  
* Install/run steps:

        python3 scripts/shipping\_queuing/retryqueue.py  
---

**4\) Method**

* In the script the following commands were used: 

        ping \-c 3 \-W 2 {ip} 
    To get the ping connection for every node to sort from strongest to weakest connection

        rsync \--list-only -e ssh {SSH_OPTS} /home/pi/shipping/
    To handle the data transfer between the supervisor and the nodes

* Using those commands together, this script ensures that after checking the directory to make sure it is not empty, each node is queued to transfer data based on how strong its ping connection is  
* In the configuration table, each node has a hardcoded ip address in the script as well

---

**5\) Code**

* Main script(s): scripts/shipping\_queue/queue\_data\_request.py  
* Example run:

        [2026-02-09 13:17:37] === STARTING DATA TRANSFER: NODES TO SUPERVISOR ===
        [2026-02-09 13:17:42] node1.local: OFFLINE
        [2026-02-09 13:17:42] node2.local: SUCCESS checking remote shipping folder
        [2026-02-09 13:17:42] node2.local: Pulling data...
        [2026-02-09 13:17:42] node2.local: Remote folder cleared.
        [2026-02-09 13:17:42] node2.local: TRANSFER SUCCESS
        [2026-02-09 13:17:43] node3.local: SUCCESS checking remote shipping folder
        [2026-02-09 13:17:43] node3.local: Pulling data...
        [2026-02-09 13:17:43] node3.local: Remote folder cleared.
        [2026-02-09 13:17:43] node3.local: TRANSFER SUCCESS
        [2026-02-09 13:17:44] node4.local: SUCCESS checking remote shipping folder
        [2026-02-09 13:17:44] node4.local: Pulling data...
        [2026-02-09 13:17:44] node4.local: Remote folder cleared.
        [2026-02-09 13:17:44] node4.local: TRANSFER SUCCESS
        [2026-02-09 13:17:48] node5.local: SUCCESS checking remote shipping folder
        [2026-02-09 13:17:48] node5.local: Pulling data...
        [2026-02-09 13:17:48] node5.local: TRANSFER SUCCESS
        [2026-02-09 13:17:48] node5.local: SUCCESS checking remote shipping folder
        [2026-02-09 13:18:02] === RETRYING FAILED NODES (Max 5) ===
        [2026-02-09 13:18:02] --- Retry Round 1 ---
        [2026-02-09 13:18:02] node1:local: SUCCESS on retry
        [2026-02-09 13:18:02] node1:local: Remote folder cleared.
        [2026-02-09 13:18:20] === FINAL STATUS: COMPLETED ===

* Important snippet:
        
        def main():
            log("=== STARTING DATA TRANSFER: NODES TO SUPERVISOR ===")
            nodes = load_nodes()
            if not nodes:
                return

            # STEP 1: Verify Node Health
            for name, info in nodes.items():
                full_host = get_full_host(name, info)
                nodes[name]["node_state"] = "alive" if ping_node(full_host) else "dead"
                if nodes[name]["node_state"] == "dead":
                    log(f"{full_host}: OFFLINE")
            save_nodes(nodes)

            # STEP 2: Initial Transfer Attempt
            failed_nodes = []
            for name, info in nodes.items():
                full_host = get_full_host(name, info)

                if info["node_state"] == "dead":
                    failed_nodes.append(name)
                    continue

                if not has_remote_data(full_host):
                    log(f"{full_host}: No files found in {REMOTE_SHIP_DIR}/")
                    nodes[name]["transfer_fail"] = False
                    continue

                log(f"{full_host}: Pulling data...")
                if rsync_pull(full_host):
                    log(f"{full_host}: TRANSFER SUCCESS")
                    nodes[name]["transfer_fail"] = False
                    delete_shipping_data(full_host)
                else:
                    log(f"{full_host}: TRANSFER FAILURE")
                    nodes[name]["transfer_fail"] = True
                    failed_nodes.append(name)
            save_nodes(nodes)

            # STEP 3: Retries for Offline or Failed Nodes
            if failed_nodes:
                log(f"=== RETRYING FAILED NODES (Max {MAX_RETRIES}) ===")
                for attempt in range(1, MAX_RETRIES + 1):
                    if not failed_nodes: break
                    log(f"--- Retry Round {attempt} ---")
                    still_failing = []
                    for name in failed_nodes:
                        full_host = get_full_host(name, nodes[name])
                        if ping_node(full_host) and has_remote_data(full_host):
                            if rsync_pull(full_host):
                                log(f"{full_host}: SUCCESS on retry")
                                nodes[name]["transfer_fail"] = False
                                delete_shipping_data(full_host)
                                continue
                        still_failing.append(name)
                    failed_nodes = still_failing
                    save_nodes(nodes)

            log("=== FINAL STATUS: COMPLETED ===")



---

**6\) Testing**

* **How you tested it (manual demo, script, unit tests):**  I would run every command individually that I used in the script to ensure that it would return the expected results so that everything in the script will interact with minimal issues  
* **Results (pass/fail, screenshots, notes):** Since I test everything thing individually, the script ran without issue the first try

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