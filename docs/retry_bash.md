# **BEAM Student Task Documentation**

### **Basic Info**

* **Task Title:** Scheduled RetryQueue Supervisor Setup  
* **Student(s):** Jackson Roberts  
* **Mentor/Reviewer:** Raiz Mohammed  
* **Date Started / Completed:** 2/5/2026 – 2/9/2026  
* **Status:** Done  
* **GitHub Link:** [set\_retryservice.sh](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/installation_bash/set_retryservice.sh)

---

### **1\) Summary**

I developed a deployment script that configures a **systemd timer and service** to handle scheduled data transfers. Instead of running a script 24/7, this setup triggers the `retryqueue.py` logic once daily at 14:00 (2:00 PM), ensuring that queued messages are processed during a specific maintenance window to optimize node resources.

### **2\) Goals**

* **Main goal:** Automate the creation of a persistent daily timer for the BEAMNode data queue.  
* **Success Metric:** `systemctl list-timers` shows the next scheduled run at 13:10:00, and the service executes without manual intervention.

### **3\) Setup**

* **Hardware:** Raspberry Pi (Standard BEAMNode kit).  
* **Software:** Linux (Systemd-enabled), Python 3\.  
* **Directories Required:** `/home/pi/logs` and `/home/pi/data`.  
* **Install/run steps:**

Bash  
chmod \+x set\_retryservice.sh  
sudo ./set\_retryservice.sh

### **4\) Method**

* **Directory Prep:** Created standard log and data directories to ensure the Python script has a place to write output.  
* **Permission Handling:** Forced execution permissions on the target Python script.  
* **Dual-Unit Logic:**  
  * Created a `.service` file of `Type=oneshot` (runs then exits).  
  * Created a `.timer` file using `OnCalendar` to specify the 14:00 schedule.  
* **Persistence:** Set `Persistent=true` in the timer so that if the Pi is powered off during the scheduled time, the task runs immediately upon next boot.

### **5\) Code**

* **Main script:** `installation_bash/set_retryservice.sh`  
* **Target script:** `scripts/node/shipping_queuing/retryqueue.py`

**Important Snippet (The Timer Logic):**

Bash  
\[Timer\]  
OnCalendar=\*-\*-\* 14:00:00  
Persistent=true  
Unit=retryqueue.service

### **6\) Testing**

* **Validation:** Used `systemctl is-active --quiet retryqueue.timer` to confirm successful activation.  
* **Scheduling Check:** Ran `systemctl list-timers` to verify the "Next" and "Left" columns correctly pointed to 1:10 PM.  
* **Results:** **Pass**. The system recognizes the schedule and links the timer correctly to the one-shot service.

### **7\) Lessons & Next Steps**

* **What worked well:** Using `oneshot` services is much more efficient for periodic tasks than `always` restart services.  
* **Problems faced:** Timezone synchronization. If the Pi's system clock is not set to the local time, the 14:00 trigger will happen at the wrong time.  
* **Suggestions:** Ensure NTP (Network Time Protocol) is active on the Pi so the "14:00" trigger remains accurate.

### **8\) References**

* [BEAMNode Prototype 1 Repo](https://www.google.com/search?q=https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/)  
* [ArchWiki: Systemd Timers](https://wiki.archlinux.org/title/Systemd/Timers)

