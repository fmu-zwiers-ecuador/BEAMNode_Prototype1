  
**BEAM Student Task Documentation Template**

Use this template to record your work clearly. Keep it short but complete so others can understand and reproduce your results.

---

**Basic Info**

* **Task Title:** Automatic Running System  
* **Student(s):** Jackson Roberts  
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started:  / Completed:** 01/26/2026  
* **Status:** Done  
* **GitHub Link:** https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/blob/main/installation\_bash/autostartinstall.sh

**1\) Summary** Created a Bash script to handle the "dirty work" of setting up a new node. It creates folders, sets permissions, and installs the system service automatically.

**2\) Goals**

* **Main goal(s):** Make node setup a one-command process.  
* **How do we know it works?** The terminal prints "SUCCESS: Installation Complete\!" at the end.

**3\) Setup**

* **Software:** Bash/Linux.  
* **Install/run steps:** chmod \+x autostartinstall.sh then ./autostartinstall.sh.

**4\) Method**

* Used mkdir \-p to create data and log directories without erroring if they already exist.  
* Used chmod \+x to ensure all Python scripts are executable by the system.  
* Used sudo cp to move the service file into the protected system directory.

**5\) Code**

* **Main script(s):** autostartinstall.sh  
* **Important snippet:**

Bash

sudo cp "$SERVICE\_SRC" /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable "$SERVICE\_NAME"

**6\) Testing**

* **Method:** Ran on a fresh Raspberry Pi OS install.  
* **Results:** All folders created, and the service started without manual intervention.

**7\) Lessons & Next Steps**

* **Worked well:** Using variables like PROJECT\_ROOT at the top makes the script easy to update if the file path changes later.


