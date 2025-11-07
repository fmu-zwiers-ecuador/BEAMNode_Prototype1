# **Detect.py Full Integration and Testing**

---

**Basic Info**

* **Task Title:** Detect.py Full Integration and Testing  
*  **Student(s):** Alexander Lance  
*  **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
*  **Date Started / Completed:** October 27th, 2025 \-  November 1st, 2025  
*  **Status:** Done:   
*  **GitHub Link:** [*https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/tree/main/scripts/node*](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/node)  
* 

---

## **1\) Summary**

I extended the detect.py script to detect all the sensors we currently have and ensure that it “enables” or “disables” the sensors in config.json. This was important because it lets the system automatically confirm which sensors are active and flips them to true after detection. This ensures that every sensor connected to the node is confirmed working before deployment and that config.json stays accurate.

---

## **2\) Goals**

* **Main goal:** Extend detect.py to detect all sensors (BME280, TSL2591, AHT, Camera, and AudioMoth) and flip them to “enabled”: true when found.  
* **Works when:** After running sudo detect.py, every connected sensor correctly flips from “enabled”: false to “enabled”: true inside the config.json file.  
* **To verify, run:**  
   cat /home/pi/BEAMNode\_Prototype1/scripts/node/config.json  
   and check that each detected sensor is enabled true.

---

## 

## **3\) Setup**

**Hardware**

* Hardware:Raspberry Pi 3 Model B, Adafruit BME280, TSL2591, AHT sensor (0x38), IMX219 Camera, AudioMoth USB microphone.  
* Software: Thonny IDE, BASH Shell, Python3, Vscode  
  * Packages: `os, json, logging, subprocess, spidev, RPi.GPIO, picamera2` 

* Install/Run Steps:   
* sudo git pull origin main  
* cd /home/pi/BEAMNode\_Prototype1/scripts/node  
* sudo python detect.py  
* cat config.json

---

**4\) Method** 

* Ran sudo git pull origin main to make sure the repo was up to date.  
   Cd’d into the prototype and into the config to check that they were all flipped to false.  
   Then cd’d into sensor detection and ran sudo detect.py, and after it completed, I cat back into config.json and confirmed that all present sensors on the node were enabled true.  
* Main issue I ran into was the config files not being flipped to true after detection. The solution was that I never actually changed the path when everything was reorganized.  
   Ran into the problem where the camera and audio blocks were nested inside bme280, so I fixed that and set:  
   CONFIG\_PATH \= "/home/pi/BEAMNode\_Prototype1/scripts/node/config.json"  
* After this change, all detected sensors flipped to “enabled”: true.  
* Another major problem I ran into was the audio and camera lines of code in the config file being nested inside bme all due to a stray brace (so for future students, always check syntax), and there wasn’t enough structure for detect\_imx219\_picamera2() \+ set\_config\_flag() calls to toggle things cleanly.

---

**5\) Code** 

* Main script(s): http://BEAMNode\_Prototype1/scripts/node/detect.py  
* Run with command:

Run with command:  
 sudo python detect.py  
New detect scripts for AHT:  
 "AHT": 0x38,

Made a more all-intensive detection script for tsl and aht sensors that just needs sensor addresses and sensor names for detection and to log detection:  
for sensor\_name, sensor\_addr in addr\_table.items():  
    if sensor\_addr in found\_addrs:  
        detected\_sensors.append(sensor\_name)  
        logging.info(f'{sensor\_name} detected.')

New detect script for Camera:  
def detect\_imx219\_picamera2():  
    try:  
        cams \= Picamera2.global\_camera\_info()  \# list of dicts  
        for c in cams:  
            model \= (c.get("Model") or c.get("model") or "").lower()  
            if "imx219" in model:  
                return True, f"Found camera: {c}"  
        return False, f"No IMX219 found. Cameras: {cams}"  
    except Exception as e:  
        return False, f"Picamera2 unavailable or failed: {e}"

ok, info \= detect\_imx219\_picamera2()  
print(ok, info)  
set\_config\_flag(CONFIG\_PATH, "camera", "enabled", True)

New detect script for Audio:  
def detect\_audiomoth\_simple():  
    roots \= \["/media/pi", "/media", "/mnt", "/run/media/pi"\]  
    for root in roots:  
        if os.path.isdir(root):  
            for name in sorted(os.listdir(root)):  
                full \= os.path.join(root, name)  
                if os.path.ismount(full):  
                    set\_config\_flag(CONFIG\_PATH, "audio", "enabled", True)  
                    set\_config\_flag(CONFIG\_PATH, "audio", "mount\_path", full)  
                    return True, f"AudioMoth USB storage at {full}"  
    return False, "No USB storage mount found."

ok\_am, info\_am \= detect\_audiomoth\_simple()  
print("AudioMoth:", ok\_am, "-", info\_am)

---

**6\) Testing  \***

* Verified detection for all sensors:  
* BME280 detection: ChipID: 0x60 (shows detection)  
* Camera detected: Result “enabled”: true, “last\_detect\_info”: Found camera: {‘Model’: ‘imx219’, ‘Location’: 2, ‘Rotation’: 180, ‘Id’: /base/soc/12c0mux/i2c@1/imx219@10’, ‘Num’: 0}  
* TSL and AHT sensors: “The following sensors are online: ‘TSL2591’, ‘AHT’”  
* AudioMoth: “AudioMoth: True – AudioMoth USB storage at /media/pi/BEAMdrive1”

After each run, used cat config.json to confirm all detected sensors switched to true.

---

**7\) Lessons & Next Steps** 

* The main issue I had was the config path not being updated after the reorganization. Once I corrected it, all sensors were detected and flipped to “enabled”: true. Another issue was the stray brace that caused the camera and audio sections to be nested inside bme280, which broke detection. For future students, always check syntax carefully.  
* After fixing those, the detect.py script fully worked and each sensor correctly toggled true when present.  
   For future work, I plan to make error handling more consistent when sensors aren’t detected or when the Pi camera fails to load properly at boot.


---

**8\) References \***

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [**https://forums.raspberrypi.com/search.php?keywords=json+file+bme280\&sid=603063906e27ef0fe9017deac3157f9f**](https://forums.raspberrypi.com/search.php?keywords=json+file+bme280&sid=603063906e27ef0fe9017deac3157f9f) **\-** Raspberrypi forums for help with JSON script

* [https://docs.circuitpython.org/projects/ahtx0/en/latest/](https://docs.circuitpython.org/projects/ahtx0/en/latest/) \- AHT Sensor Library

* [https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf) – Picamera2 API Reference

* [https://docs.circuitpython.org/projects/bme280/en/latest/api.html](https://docs.circuitpython.org/projects/bme280/en/latest/api.html) \- API reference for the BME280