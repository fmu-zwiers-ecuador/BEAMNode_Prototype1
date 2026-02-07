  
**BEAM Student Task Documentation Template**

Use this template to record your work clearly. Keep it short but complete so others can understand and reproduce your results.

---

**Basic Info**

* **Task Title:** Automatic Running System  
* **Student(s):** Jackson Roberts  
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started:  / Completed:** 01/26/2026  
* **Status:** Done  
* **GitHub Link:** https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/blob/main/beamnode.service

**1\) Summary** I configured the beamnode.service file to allow the Raspberry Pi to manage the node software as a background system process. This ensures the code starts automatically on boot and restarts itself if the Python script crashes.

**2\) Goals**

* **Main goal(s):** Achieve "Headless" operation (no monitor/keyboard needed).  
* **How do we know it works?** Run systemctl status beamnode.service and see the status "Active: active (running)".

**3\) Setup**

* **Hardware:** Raspberry Pi Zero.  
* **Software:** Linux Systemd.  
* **Install/run steps:**   
  * Run sudo systemctl enable beamnode.service.

**4\) Method**

* Defined `WorkingDirectory` to ensure Python finds the correct local files.  
* Set `Restart=always` with a 10-second delay to prevent infinite crash loops.  
* Redirected `StandardOutput` to `launcher.log` so we can debug.

**5\) Code**

* **Main script(s):** `beamnode.service`  
* **Important snippet:**

  Ini, TOML

* \[Service\]

* ExecStart=/usr/bin/python3 /home/pi/BEAMNode\_Prototype1/scripts/node/launcher.py

* Restart=always

* StandardOutput=append:/home/pi/BEAMNode\_Prototype1/logs/launcher.log


**6\) Testing**

* **Method:** Run sudo systemctl stop beamnode.service and then start to verify control.  
* **Results:** Service successfully initialized the launcher.py and began writing to the log file.

**7\) Lessons & Next Steps**

* **Worked well:** The StandardOutput append feature is great for keeping a history of runs.  
* **Problems:** You must use absolute paths (starting with /) or the service will fail to find Python.


