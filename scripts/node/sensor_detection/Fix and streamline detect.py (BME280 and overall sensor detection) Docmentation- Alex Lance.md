# **Fix Detect.py (BME280 and overall sensor detection)Documentation**

---

**Basic Info**

* **Task Title:**  Fix and streamline detect.py (BME280 and overall sensor detection)  
*  **Student(s):** Alexander Lance  
*  **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
*  **Date Started / Completed:** January 19th, 2026 \-  January 23rd, 2026  
*  **Status:** Done:   
*  **GitHub Link:** *https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/blob/main/scripts/node/sensor\_detection/detect.py*

---

## **1\) Summary**

This week, I focused on debugging and improving the detect.py script, with the initial goal of fixing BME280 detection issues, I mainly focused on overall detection issues occurring specifically on Node 3\. I identified that the TSL sensor was being marked as detected and updating the configuration file by my detect script, but the logluxdata script was unable to access or print data from the TSL sensor. After looking into it, the TSL sensor was not actually functioning, and the script was falsely detecting it by checking I2C bus 2 at address 0x3A instead of the correct address 0x29 on I2C bus 1\.

After verifying wiring, making sure both SPI and I2C were enabled, and checking configuration file paths, we ended up replacing the Raspberry Pi, and I updated the detect.py to only check address 0x29 for the TSL sensor and to only scan I2C bus 1\. I streamlined detect.py across all nodes by removing unnecessary checks on the I2C board, and removing redundant imports and unnecessary logging. The updated script now prints a clean and readable detection summary for SPI, I2C, camera, and AudioMoth sensors.

---

## **2\) Goals**

* **Main goal:** Fix detect.py BME280 detection, ultimately including fixing TSL detection logic and fixing and cleaning up the entire script.   
* **Works when:**  
   The detect.p`y` script runs without error, correctly updates detection status in config.json, and prints a clean detection summary for each sensor.  
* **Successful detection output:**  
* \=== SENSOR DETECTION SUMMARY \===  
* SPI Sensor: BME280 detected  
* Camera: Camera IMX219 detected  
* I2C Sensors: TSL2591, AHT  
* AudioMoth: AudioMoth detected  
* \=== END OF DETECTION \===  
* 

---

## 

## **3\) Setup**

**Hardware**

* Hardware: Raspberry Pi 3, Adafruit BME280 Temperature Humidity Pressure Sensor,  Camera IMX219, Camera IMX219, TSL2591, TSL2591, AudioMoth  
* Software: Thonny IDE, BASH Shell, Python3, VSCode,  
  * Packages: sys, pathlib, subprocess ,python3-spidev, python3-rpi.gpio (RPi.GPIO), json, Logging, logging.handlers, picamera2, os, time

* Install/Run Steps: sudo python [detect.py](http://detect.py)  
* Sudo less config.json

---

**4\) Method**

* Ensure SPI and I2C are enabled using raspi-config.  
  Ensure all sensor configuration flags are initially set to false.  
* Update the detection logic to match the correct protocol for each sensor.  
  Restrict I2C detection to the correct bus and addresses to prevent false positives.  
* Verify that detected sensors update config.json correctly and produce clean terminal output.

* ---

**5\) Code**

* Main script(s):   
  * BEAMNode\_Prototype1/blob/main/scripts/node/sensor\_detection/[detect.py](http://detect.py)  
  * /BEAMNode\_Prototype1/blob/main/scripts/node/config.json  
* Run with command:  
  * sudo python [detect.py](http://detect.py)  
  * sudo less config.json

* Important functions for detection:

I2C\_ADDR\_TABLE \= {"tsl2591": \[0x29\], "aht": \[0x38\]}  
CANDIDATE\_I2C\_BUSES \= (1,)

def scan\_i2c(busnum):  
    try:  
        result \= subprocess.run(\["sudo", "i2cdetect", "-y", str(busnum)\],  
                                capture\_output=True, text=True, check=True)  
        return result.stdout  
    except Exception as e:  
        spi\_logger.warning(f"I2C scan failed on bus {busnum}: {e}")  
        return ""

 detect\_i2c\_sensors():  
    detected \= \[\]  
    for bus in CANDIDATE\_I2C\_BUSES:  
        if not os.path.exists(f"/dev/i2c-{bus}"):  
            continue  
        output \= scan\_i2c(bus)  
        found\_addrs \= set(int(m, 16\) for m in re.findall(r"\\b\[0-9a-f\]{2}\\b", output, re.IGNORECASE))

* Important functions for config writing, this one is for I2C, but the others follow a similar process:

print(f"I2C Sensor Found: {name} (Bus {bus}, Addr 0x{addr:02X})")  
                    print(f"I2C Sensor Found: {name} (Bus {bus}, Addr 0x{addr:02X})")  
                    set\_config\_flag(CONFIG\_PATH, name, "enabled", True)  
                    set\_config\_flag(CONFIG\_PATH, name, "i2c\_bus", bus)  
                    set\_config\_flag(CONFIG\_PATH, name, "address\_hex", f"0x{addr:02X}")  
                    detected.append(name)  
                    sensor\_found \= True  
 if not sensor\_found:  
                set\_config\_flag(CONFIG\_PATH, name, "enabled", False)  
                set\_config\_flag(CONFIG\_PATH, name, "i2c\_bus", None)  
                set\_config\_flag(CONFIG\_PATH, name, "address\_hex", None)

* Important functions for printing:

\# \---------------- Main \---------------- \#

print("=== Sensor Detection Summary \===")  
detect\_spi\_sensor()  
detect\_camera()  
detect\_i2c\_sensors()  
detect\_audiomoth()  
print("=== Detection Complete \===")

---

**6\) Testing** 

* I ran the updated detect.py script directly on the Raspberry Pi after enabling SPI and I2C and setting all sensor configs to false.  
* I verified that the script ran without errors and produced a clean sensor detection summary in the terminal.  
* I confirmed that the BME280 was detected over SPI and that its detection status was correctly written to config.json.  
* I tested I2C detection to ensure that the TSL2591 was only detected on bus 1 at address 0x29 and that false positives from bus 2 were removed.  
* I verified that the camera and AudioMoth detection completed successfully and updated their corresponding configuration values.  
* I checked config.json after each run using sudo less config.json to confirm that the correct ones were enabled on each node.

---

**7\) Lessons & Next Steps**

* Understood all issues with the current detect.py script and made necessary changes.  
* Understood how incorrect I2C bus and address checks can cause false sensor detection and lead to failures in downstream logging scripts.  
* Understood the importance of making sure the detection logic was correct before implementing a script for it, specifically for scanning the correct bus for the correct address.  
* Gained experience cleaning and streamlining a multi-sensor detection script to improve readability for all the nodes.  
* For future students: Get comfortable navigating the Raspberry Pi using BASH commands and pulling the repository onto each node. This makes the whole debugging process for any script you are working on easier. Also, verify all required outputs after each run, in this case, checking config.json, to avoid having to redo large portions of work later.

---

**8\) References**

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [https://pinout.xyz/](https://pinout.xyz/) \- An interactive guide for learning all of the pins on the pi

* [https://docs.circuitpython.org/projects/bme280/en/latest/api.html](https://docs.circuitpython.org/projects/bme280/en/latest/api.html) \- API reference for the BME280