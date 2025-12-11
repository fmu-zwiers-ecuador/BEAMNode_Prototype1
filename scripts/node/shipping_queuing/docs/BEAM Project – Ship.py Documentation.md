## **Task: Ship Audio Data to /sending**

### **What Changed**

Originally, audio recordings stayed inside /data/audio  and built up over time.

I created ship.py to move and compress those recordings into /sending at the end of each day.

It also checks the file’s **SHA-256 checksum** to confirm integrity before deleting old data.

---

### **Why This Was Added**

Keeps the node’s storage clean and organized.

Makes sure that no corrupted or incomplete files are sent.

Prepares data for transfer to the Supervisor system safely.

---

### **How I Did It**

Defined directories:

 BASE\_DIR \= "/home/pi/data/audio/"

SEND\_DIR \= "/home/pi/sending/`"`

- Used tarfile to compress /data/audio/ into a .tar.gz file named using UTC timestamp format: audio\_YYYYMMDD\_HHMMSS.tar.gz   
- Added a checksum check using hashlib.sha256() to confirm the archive’s integrity.  
- Only if the checksum passes, previous files in /sending/ are safely deleted before the next shipment.  
- Printed log messages showing when the shipment was created and verified.

  ---

  ### **Example Output Files**

1. /sending/audio\_20251020\_143015.tar.gz  
2. /sending/audio\_20251020\_143015.sha256  
   

Printed log example:

3. \[SHIP\] Archive created: /sending/audio\_20251020\_143015.tar.gz  
4. \[SHIP\] SHA-256 checksum verified successfully.  
     
   ---

   ### **Testing on the Pi**

1. Created fake .wav and .json files in /data/audio/.  
   Ran:

    python3 ship.py  
2. Confirmed:

   * .tar.gz file appears under /sending/.

   * Terminal logs show timestamp and checksum result.

   * Old /sending/ content clears only after checksum success.

   ---

   ### **Why It Matters**

This process:

* Keeps each day’s recordings cleanly organized.

* Prevents data loss.

* Prepares files for automatic Supervisor upload in later stages.


