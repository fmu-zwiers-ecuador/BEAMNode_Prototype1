  
**BEAM Student Task Documentation Template**

Use this template to record your work clearly. Keep it short but complete so others can understand and reproduce your results.

---

**Basic Info**

* **Task Title:** Automatic Running System  
* **Student(s):** Jackson Roberts  
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started:  / Completed:** 01/26/2026  
* **Status:** Done  
* **GitHub Link:** https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/blob/main/scripts/node/launcher.py

**1\) Summary** I wrote launcher.py to act as the "brain" of the node. It coordinates when other scripts (detection, scheduling, and shipping) should run.

**2\) Goals**

* **Main goal(s):** Run detect.py once, keep scheduler.py running forever, and run shipping.py daily at 13:00.  
* **How do we know it works?** Check launcher.log for the "13:00 Target reached" message.

**3\) Setup**

* **Hardware:** Raspberry Pi.  
* **Software:** Python 3.11.  
* **Install/run steps:** python3 launcher.py

**4\) Method**

* Used subprocess.run for synchronous tasks (must finish before moving on).  
* Used subprocess.Popen for the scheduler so it can run in the background while the launcher monitors the clock.  
* Implemented a while True loop with time.sleep(10) to save CPU power.

**5\) Code**

* **Main script(s):** `launcher.py`  
* **Important snippet:**

Python

if now.hour \== 13 and now.minute \== 0 and 0 \<= now.second \<= 30:

    log("13:00 Target reached. Running Shipping.py...")

    run\_script\_sync(SHIPPING\_PATH)

    time.sleep(31) \# Prevent double trigger

**6\) Testing**

* **Method:** Change system time to 12:59:50 and watch the logs at 13:00.  
* **Results:** The launcher correctly identified the time and executed the shipping script.

**7\) Lessons & Next Steps**

* **Problems:** Initially, the script triggered shipping.py multiple times in one minute. Adding time.sleep(31) fixed this.

