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

This task was focused on testing the queue and shipping process between the supervisor and the nodes. The goal was to rsync the updated repository from the supervisor to the node, run the shipping script on the node so it creates a ZIP file named with the node ID and the current date, and then run the queueing script on the supervisor which pulls that ZIP and places it into /home/pi/data/\<nodeName\>/ with a new timestamped directory so nothing gets overwritten.

This confirms that the node’s shipping script and the supervisor’s queue script both handle files correctly with proper dating and storage separation.

---

## **2\) Goals**

**Main goal: Make sure rsync and queue scripts correctly send, date, and store files between supervisor and nodes.**

**Works when:**

* Running the shipping script on the node creates a new ZIP named with the correct node ID and date.  
* Running the queue script on the supervisor creates a new timestamped folder under /home/pi/data/\<nodeName\>/ without overwriting previous ones.

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

1. Since the supervisor and the node didn’t have Wi-Fi, I flash-drived the updated repository from my computer to the supervisor.  
   On the supervisor I rsynced those changes to the node  
2. On Node2, I ran the shipping script itself:  
    python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping.py  
    This should create a ZIP file inside /home/pi/shipping named with the node ID and the current date.  
3. I checked shipping results from the supervisor with:  
    ssh pi@192.168.1.2 'ls \-l /home/pi/shipping'  
    The ZIP file should look like: beam-node-02\_20251113T190422Z.zip  
4. On the supervisor, I ran the queue script:  
    python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py  
    This should pull the ZIP from the node and create a new timestamped folder under /home/pi/data/node2/  
5. Then I verified the queue folder grew by listing new timestamp directories:  
    ls \-1 /home/pi/data/node2  
6. Then I checked the newest folder to confirm it had the right ZIP:  
    ls \-l /home/pi/data/node2/\<latest timestamp\>/  
   

---

**4\) Method** 

* Rsync the updated repository from the supervisor to the node.  
   Run the shipping script on the node so it creates a ZIP file with the node ID and the current date.  
   Run the queueing script on the supervisor so it pulls that ZIP and saves it in /home/pi/data/node2/\<timestamp\>/.  
* One of the major problems I faced was that after I finished editing the shipping and queue scripts, the results after shipping were still showing “node1” with a September date.  
* How I fixed the first issue:  
   The problem was that node\_id on node2 was wrong.  
   On node2, I edited the config so node\_id actually matches that node. The old config had “beam-node-01”. I changed it to “beam-node-02” with:  
   node\_id: beam-node-02  
   base\_dir: /home/pi/data  
   ship\_dir: /home/pi/shipping  
* The second problem was shipping.py giving results like:  
   “pi 1629 sep 18 9:49 shipping out” — completely wrong for both date and time.  
   I fixed this by manually updating the time on the Pi. We will probably have to do this on all Pis.  
* After I fixed both issues, everything worked correctly.  
* 

---

**5\) Code** 

* Main script(s): http://BEAMNode\_Prototype1/scripts/node/shipping\_queuing  
* Run with command:

**5\) Code**  
 Main script(s):

* /scripts/node/shipping\_queuing/shipping.py

* /scripts/node/shipping\_queuing/queue\_data\_request.py

Example run:  
python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/shipping.py  
python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py

Confirm config.json has these set:

"global": {  
  "node\_id": "beam-node-02",  
  "base\_dir": "/home/pi/data",  
  "ship\_dir": "/home/pi/shipping"  
}

1\) Make sure supervisor can reach node2  
 On the supervisor:  
ping \-c 3 192.168.1.2

2\) SSH into node2 and confirm the new, correctly dated shipped file  
 From the supervisor:  
ssh pi@192.168.1.2 'ls \-l /home/pi/shipping'

You should see:  
 beam-node-02\_20251113T190422Z.zip  
recent date   
3\) Now run the queue script on the supervisor  
python3 /home/pi/BEAMNode\_Prototype1/scripts/node/shipping\_queuing/queue\_data\_request.py

Expected log output:  
Requesting shipped data from node2 (xx ms)...  
Pulled shipped zips from node2 (192.168.1.2) \-\> /home/pi/data/node2/20251113T190610Z

4\) Verify the files were pulled correctly  
   
ls \-1 /home/pi/data/node2

Expected output:  
20251113T190610Z  
20251113T191201Z

List what’s inside the most recent folder:  
ls \-l /home/pi/data/node2/\*/

You should see your zipped file  
 beam-node-02\_20251113T190422Z.zip

Verify it’s not empty:  
echo "/home/pi/data/node2/$LATEST"  
unzip \-l "/home/pi/data/node2/$LATEST/beam-node-02\_\*.zip"

---

**6\) Testing**  

After running all scripts and fixes, I confirmed:

 • The shipping script on node2 creates a ZIP with the correct node ID and the correct date. 

• The supervisor’s queue script pulls that ZIP and makes a new timestamp directory under /home/pi/data/node2 each time.

 • Verified that nothing gets overwritten and that each pull produces a new timestamp folder.

 • Confirmed the ZIPs were valid by unzipping and checking their contents.

---

**7\) Lessons & Next Steps** 

* The main issues were the wrong node\_id inside config.json and the Pi’s incorrect date/time. After fixing both, the shipping and queue processes worked correctly. For future students: always make sure each node’s config.json has the right node\_id, and always confirm the Pi’s date/time before testing. Also verify that the queue script appends new folders instead of overwriting old ones.  
* Next steps may include testing this on each of the nodes.


---

**8\) References** 

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [**https://forums.raspberrypi.com/**](https://forums.raspberrypi.com/)**\-** For specific help with Ras Pi Issues

* [https://linux.die.net/man/1/rsync](https://linux.die.net/man/1/rsync) \-Linux Rsync manual