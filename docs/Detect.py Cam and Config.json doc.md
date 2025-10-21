**Detect.py Cam and Config.json Integration BEAM Student Task Documentation** 

---

**Basic Info**

* **Task Title: Detect.py cam branch \+ detect.py and config.json integration**  
* **Student(s): Alexander Lance**  
* **Mentor/Reviewer: Dr. Paul Zwiers / Raiz Mohammed**  
* **Date Started / Completed: October 13th, 2025 – October 17th, 2025**  
* **Status:** Done  
* **GitHub Link: https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1**

---

**1\) Summary**

I extended the detect.py script to automatically enable each sensor’s "enabled" flag inside the config.json file when that sensor is successfully detected. This included adding a camera detection branch using the IMX219 ID, similar to how chip-ID detection works for BME280 on SPI. This matters because it removes the need to manually edit the config file after plugging in sensors, allowing the node to self-configure correctly when sensors are connected.

---

**2\) Goals**

**Main goal:** Modify detect.py so that each supported sensor (BME280, TSL2591, and IMX219 camera) automatically flips its "enabled" flag from false to true inside config.json when detected.

**Works when:**

* Running python detect.py correctly detects each connected sensor.

* config.json is updated so that the enabled fields for the detected sensors are set to true after the script runs.

* No errors occur during detection or JSON editing.  
* 

---

**3\) Setup**

*List what you used and how to set it up.*

Hardware:

* Raspberry Pi 3

* Adafruit BME280 (SPI), TSL2591 (I²C), IMX219 Camera Module

Software:

* Raspberry Pi OS

* Python 3

* Packages: spidev, RPi.GPIO, picamera2, json

Install/Run Steps:

sudo apt update && sudo apt install \-y python3-spidev python3-rpi.gpio python3-picamera2

sudo git pull origin main   \# pull new detect.py changes

CONFIG\_PATH used in the script:

/home/pi/BEAMNode\_Prototype1/config.json

---

**4\) Method**

* Extended detect.py to include a set\_config\_flag() method for safely editing JSON without overwriting other fields.  
  For BME280, used chip-ID detection over SPI. Manually controlled GPIO5 for CS and set spi.no\_cs \= True to avoid CE0/CE1 conflicts.  
* For TSL2591, reused the existing I²C scan, and called set\_config\_flag(CONFIG\_PATH, "tsl2591", "enabled", True) if the sensor was found in the devices list.  
  For camera detection, used Picamera2’s global\_camera\_info() to check if any camera model strings contain "imx219". If found, flipped "camera": { "enabled": true } in the config.  
* Removed print-only detection messages; detection now silently enables sensors in config.  
* Verified file path correctness for CONFIG\_PATH, since this was previously incorrect and caused the flag updates not to apply.

* 

---

**5\) Code**

* Main script(s): /home/pi/BEAMNode\_Prototype1/[detect.py](http://detect.py)

**Example run:**

python [detect.py](http://detect.py)

**Key snippet:**  
CONFIG\_PATH \= "/home/pi/BEAMNode\_Prototype1/config.json"  
def set\_config\_flag(path, section, key, value):  
    try:  
        with open(path, "r") as f:  
            cfg \= json.load(f)  
    except Exception:  
        cfg \= {}  
    if section not in cfg or not isinstance(cfg\[section\], dict):  
        cfg\[section\] \= {}  
    if cfg\[section\].get(key) \!= value:  
        cfg\[section\]\[key\] \= value  
        tmp\_path \= f"{path}.tmp"  
        with open(tmp\_path, "w") as f:  
            json.dump(cfg, f, indent=2)  
        os.replace(tmp\_path, path)  
**Camera detection script:**  
from picamera2 import Picamera2

def detect\_imx219\_picamera2():  
    try:  
        cams \= Picamera2.global\_camera\_info()  
        for c in cams:  
            model \= (c.get("Model") or c.get("model") or "").lower()  
            if "imx219" in model:  
                set\_config\_flag(CONFIG\_PATH, "camera", "enabled", True)  
                return True, f"Found camera: {c}"  
        return False, f"No IMX219 found. Cameras: {cams}"  
    except Exception as e:  
        return False, f"Picamera2 unavailable or failed: {e}"

---

**6\) Testing**

* For testing, I first ran:  
* sudo git pull origin main  
* cat config.json   \# to verify all enabled flags were set to false  
* Then ran the detection script:  
* python detect.py  
* BME280 was connected over SPI, and the script printed:  
* Chip ID: 0x60 (BME280)  
* TSL2591 was also online on the I²C bus.  
* The bash will print whether or not the IMX219 was connected.  
* Afterwards, I ran:  
* cat config.json  
* Both "bme280" and "tsl2591" had their "enabled" flags flipped to true, and 

---

**7\) Lessons & Next Steps**

* Enabling the sensors in config initially didn’t work because BME280 was being “detected” even when nothing was connected. I fixed this by tightening the SPI detection logic and using spi.no\_cs \= True so that spidev doesn’t drive CE0/CE1.  
* I learned to always verify physical wiring and pins before debugging code, and to tighten code earlier to save time later.  
* Another problem was that the CONFIG\_PATH was wrong at first, so the JSON was never actually being updated. This reinforced that checking file paths should be step one before deeper debugging.  
* For future work, I could add a “disable if not found” step to keep the config always in sync if sensors are unplugged.


---

**8\) References**

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* **https://forums.raspberrypi.com/viewtopic.php?t=216176\#p1329465 \-** Raspberrypi forums for help with JSON script

* [https://docs.circuitpython.org/projects/bme280/en/latest/api.html](https://docs.circuitpython.org/projects/bme280/en/latest/api.html) \- API reference for the BME280

