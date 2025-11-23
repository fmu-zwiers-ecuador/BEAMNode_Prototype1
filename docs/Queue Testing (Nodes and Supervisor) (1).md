# **Queue Testing (Nodes and Supervisor)**

---

**Basic Info**

* **Task Title:** Queue Testing  
*  **Student(s):** Alexander Lance  
*  **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
*  **Date Started / Completed:** November 3rd, 2025 \-  November 13rd, 2025  
*  **Status:** Done:   
*  **GitHub Link:** [*https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/tree/main/scripts/node*](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/node)  
* 

---

## **1\) Summary**

This task focused on testing the queue and shipping process between the supervisor and the nodes. The goal was to rsync the updated repository from the supervisor to the node, run the shipping script on the node so it moves everything from /home/pi/data into /home/pi/shipping/ and renames that folder using the node’s hostname and a UTC timestamp, and then run the queueing script on the supervisor so it pulls that folder and places it directly into /home/pi/data/ without overwriting any previous data. 

The updated system does not use ZIP files anymore. Instead, the node ships an entire folder named with its hostname and timestamp (for example: data-beam-node-02-20251113T210455Z/), and the supervisor stores that folder exactly as-is. This confirms that both the node’s shipping script and the supervisor’s queue script correctly handle folder transfers, folder naming conventions, and timestamp-based organization.

---

## **2\) Goals**

**Main goal:** Make sure rsync and queue scripts correctly send, date, and store the node’s data using the new folder-based process.

**Works when:**

* Running the shipping script on the node creates a new folder named with the correct node name and date inside /home/pi/shipping/.

* Running the queue script on the supervisor pulls that folder and places it into /home/pi/data/ each time without overwriting previous one  
* 

---

## 

## **3\) Setup**

**Hardware**

* Hardware  
  Supervisor Raspberry Pi, Node2 Raspberry Pi (no Wi-Fi connection).

**Software**

*  Raspberry Pi OS, Python3, BASH Shell, Git.

**Packages**

*  rsync, os, json, datetime.

**Install/Run Steps (How I actually tested it**):

### **Hardware**

* Supervisor Raspberry Pi, Node2 & Node3 Raspberry Pis (no Wi-Fi connections)

  ### **Software**

* Raspberry Pi OS, Python3, BASH Shell, Git

  ### **Packages**

* rsync, os, json, datetime

  ### **Install/Run Steps (How I actually tested it)**

1. Since the supervisor and the nodes did not have Wi-Fi, I flash-drived the updated repository from my computer to the supervisor.

2. On the supervisor, I rsynced those changes to the nodes.

1. On Node2, I ran the shipping script itself:

    python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/shipping.py  
2.  This should create a new folder inside /home/pi/shipping/ named like:

    data-beam-node-02-20251113T210455Z  
3.   
3. I checked the shipping results from the supervisor with:

    ssh pi@192.168.1.2 'ls \-l /home/pi/shipping'  
4.   
4. On the supervisor, I ran the queue script:

    python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py  
5.  This should pull the folder from the node and place it directly into /home/pi/data/.

5. I verified the results on the supervisor by listing /home/pi/data/:

    ls \-1 /home/pi/data  
6. Then I inspected the newest folder to confirm the data transferred correctly.  
     
   

---

**4\) Method** 

* Rsync the updated repository from the supervisor to the node.  
   Run the shipping script on the node so it moves everything from /home/pi/data into /home/pi/shipping/ and renames the folder as data-\<hostname\>-\<timestamp\>.  
   Run the queueing script on the supervisor so it pulls that folder from the node and places it directly into /home/pi/data/, creating a new timestamped folder each time without overwriting previous ones.

* One of the major problems I faced was that after I finished editing the shipping and queue scripts, the shipped folders were still showing the wrong node name and a September date. This made it look like node1 was shipping instead of node2, and the timestamps did not match the current date.

* How I fixed the first issue:  
   The problem was that the node\_id on node2 was wrong.  
   On node2, I edited the config so the node\_id actually matched that node. The old config had “beam-node-01”. I changed it to “beam-node-02” with:  
   node\_id: beam-node-02  
   base\_dir: /home/pi/data  
   ship\_dir: /home/pi/shipping

* The second problem was the system time being incorrect. The folder names were being created with old September timestamps.  
   I fixed this by manually updating the time on the Pi. We will probably have to do this on all Pis.

* Another issue was misunderstanding the folder process in the new design. At first, I assumed the queue script was still supposed to create extra subdirectories like /home/pi/data/\<nodeName\>/\<timestamp\>/. After checking with the supervisor, I learned that the new system is simpler: the node ships one folder for each send, and the supervisor stores those folders directly inside /home/pi/data/. The timestamp in the folder name is what keeps everything separated, so no additional layers are needed.  
* After I fixed these issues and aligned the logic with the actual design, everything worked correctly.


---

**5\) Code** 

## **5\) Code**

**Main script(s):**  
 /scripts/node/shipping\_queuing/shipping.py  
 /scripts/node/shipping\_queuing/queue\_data\_request.py

Example run:

python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/shipping.py  
python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py

Confirm config.json has these set:

"global": {  
    "node\_id": "beam-node-03",  
    "base\_dir": "/home/pi/data",  
    "ship\_dir": "/home/pi/shipping"  
}

1. Make sure the supervisor can reach node2:

ping \-c 3 192.168.1.3

2. SSH into node3 and confirm the new correctly dated shipped folder:

ssh pi@192.168.1.3 'ls \-l /home/pi/shipping'

You should see something like:

data-beam-node-03-20251113T210455Z

3. Now run the queue script on the supervisor:

python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py

Expected log output:

Requesting shipped data from node3 (xx ms)...  
Pulled shipped data from node3 (192.168.1.3) \-\> /home/pi/data/

4. Verify the files were pulled correctly:

ls \-1 /home/pi/data

Expected output:

data-beam-node-03-20251113T210455Z  
data-beam-node-03-20251113T212130Z

List what’s inside the most recent folder:

ls \-l /home/pi/data/data-beam-node-03-20251113T210455Z/

---

**6\) Testing**  

After running all scripts and fixes, I confirmed:

* To test the system, I first ran connection tests on all five nodes to make sure the supervisor could reach them. Out of the five nodes, four responded correctly, and only one node did not reply to ping. This confirmed that most of the network was functioning and ready for queue testing.  
* After verifying connections, I prepared Node3 specifically for the shipping test by placing test data in its /home/pi/data directory and running the shipping script. This created a properly named folder inside /home/pi/shipping on Node3 using the hostname and timestamp.  
* On the supervisor, I ran the queue script to pull data from all reachable nodes. The supervisor measured the latency for each node and automatically selected the one with the lowest ping first. In this test, node1 had the lowest ping, so the supervisor processed node1 before any others.

* After node1, Node3 had the next lowest latency, so the supervisor attempted to acquire its shipped data next. The queue script successfully pulled Node3’s folder from /home/pi/shipping and placed it directly into /home/pi/data/ on the supervisor. Each run created a new timestamped folder without overwriting any previous data.  
* I confirmed that the folder from Node3 contained the correct content and matched what was originally on the node before shipping. After completing these tests, the system behaved as expected across the nodes that were reachable.

---

**7\) Lessons & Next Steps** 

* The main issues came from misunderstanding the new folder-based design. I originally assumed the system still used ZIP files and node-specific timestamped subdirectories. Because of that assumption, I implemented incorrect logic and misdiagnosed problems. After reviewing the design with the supervisor, I learned that the new approach moves whole folders instead of zipping them, and the supervisor stores those folders directly under /home/pi/data/.  
* The incorrect node\_id inside node2’s config.json and the wrong system date/time also contributed to early confusion. Fixing both made the folder names and timestamps correct. I learned the importance of always verifying assumptions with the supervisor before changing logic, confirming the node\_id in config.json, and making sure the Pi's system clock is set correctly during testing.  
* Next steps may include repeating this testing process on all other nodes.


---

**8\) References** 

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [**https://forums.raspberrypi.com/**](https://forums.raspberrypi.com/)**\-** For specific help with Ras Pi Issues

* [https://linux.die.net/man/1/rsync](https://linux.die.net/man/1/rsync) \-Linux Rsync manual