# **Queue Testing (Nodes and Supervisor)**

---

**Basic Info**

* **Task Title:** Fixing sensor detection issues before deployment  
* **Student(s)**: Alexander Lance  
* **Mentor/Reviewer**: Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started** / Completed: December 8 \- December 12 2025  
* **Status:** Done  
* **GitHub Link:** [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)[https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/tree/main/scripts/node](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/node)  
* 

---

## **1\) Summary**

While setting up all sensors across the nodes, we ran into several issues that needed to be fixed before deployment. The main problems were a BME280 that would not detect on one Pi even though the code worked on every other node, inconsistent I²C behavior across different SD cards and Pis, and confusion around AudioMoth/MicroMoth USB microphone sample rates (384 kHz vs 48 kHz). I fixed these by identifying hardware wiring issues, making I²C detection more flexible across buses and addresses, and simplifying AudioMoth detection while clarifying the correct USB microphone configuration workflow.

---

## **2\) Goals**

* **Main goal:** Make sensor detection reliable across all nodes and remove setup issues that could break deployment.

Works when:  
 All connected sensors are correctly detected on any node.  
 `config.json` updates automatically with correct enabled flags and I²C details.  
 AudioMoth/MicroMoth USB microphones are detected consistently and understood to require the correct firmware/config approach.  
 Sensor failures are easy to diagnose instead of guessing whether the issue is code or hardware.

---

## 

## **3\) Setup**

1. **Setup**  
    **List what you used and how to set it up.**

**Hardware:**  
 **Raspberry Pi (multiple nodes)**  
 **Adafruit BME280 (SPI)**  
 **TSL2591 (I²C)**  
 **AHT (I²C)**  
 **AudioMoth / MicroMoth (USB microphone mode)**  
 **IMX219 Camera (on some nodes)**

**Software:**  
 **Raspberry Pi OS**  
 **Python 3**  
 **Packages/Tools: spidev, RPi.GPIO, i2c-tools, json, subprocess**

**Install/Run Steps:**  
 **sudo apt update**  
 **sudo apt install \-y i2c-tools python3-spidev python3-rpi.gpio**  
 **sudo raspi-config \# enable I²C and SPI**  
 **sudo git pull origin main**

**CONFIG\_PATH used in the script:**  
 **/home/pi/BEAMNode\_Prototype1/config.json**

2.   
     
   

---

**4\) Method** 

* BME280 not detecting on one Pi  
   The BME280 would not detect on a specific Pi even though the same code worked on every other node. We swapped Pis and sensors and were close to rewriting detection logic, but the actual issue ended up being bad jumper wires. Once the wires were replaced, detection worked immediately.  
* I²C detection made consistent across nodes  
   Different nodes exposed different I²C buses (`/dev/i2c-1` vs `/dev/i2c-2`), and the TSL2591 showed up at different addresses (`0x29` or `0x3A`) depending on the board. I replaced the I²C detection section so it scans both buses, accepts multiple valid addresses, and writes the correct bus and address back into `config.json`.  
* AudioMoth USB microphone detection and sample rate issue  
   Some MicroMoths showed up as 48 kHz USB microphones while others enumerated at 384 kHz. We originally tried using the AudioMoth Configuration App, which is meant for field recording firmware, not USB microphone mode. The fix was understanding that USB microphone sample rate is defined by the USB mic firmware/config workflow. Detection was simplified to rely only on `lsusb`, avoiding unnecessary bus or mount assumptions.


---

**5\) Code** 

5. Main script(s): /home/pi/BEAMNode\_Prototype1/detect.py

Example run:  
 python detect.py

Key snippet \#1: I²C detection that scans bus 1 and 2 and supports multiple addresses  
 addr\_table \= {  
 "tsl2591": \[0x29, 0x3A\],  
 "aht": \[0x38\],  
 }

CANDIDATE\_I2C\_BUSES \= (1, 2\)

def scan\_i2c(busnum):  
 try:  
 result \= subprocess.run(  
 \["sudo", "i2cdetect", "-y", str(busnum)\],  
 capture\_output=True,  
 text=True,  
 check=True  
 )  
 return result.stdout  
 except Exception:  
 return \-1

def scan\_all\_i2c\_buses(buses=CANDIDATE\_I2C\_BUSES):  
 all\_found\_addrs \= set()  
 addr\_to\_buses \= {}

`for bus in buses:`    
    `if not os.path.exists(f"/dev/i2c-{bus}"):`    
        `continue`  

    `adds = scan_i2c(bus)`    
    `if adds == -1:`    
        `continue`  

    `matches = re.findall(r"\b[0-9a-f]{2}\b", adds, re.IGNORECASE)`    
    `for m in matches:`    
        `addr = int(m, 16)`    
        `all_found_addrs.add(addr)`    
        `addr_to_buses.setdefault(addr, set()).add(bus)`  

`return all_found_addrs, addr_to_buses`  

def detect\_i2c\_sensors():  
 found\_addrs, addr\_to\_buses \= scan\_all\_i2c\_buses()  
 detected \= \[\]

`for sensor_name, possible_addrs in addr_table.items():`    
    `found_addr = None`    
    `found_bus = None`  

    `for addr in possible_addrs:`    
        `if addr in found_addrs:`    
            `found_addr = addr`    
            `found_bus = min(addr_to_buses[addr])`    
            `break`  

    `if found_addr is not None:`    
        `detected.append(sensor_name)`    
        `set_config_flag(CONFIG_PATH, sensor_name, "enabled", True)`    
        `set_config_flag(CONFIG_PATH, sensor_name, "i2c_bus", found_bus)`    
        `set_config_flag(CONFIG_PATH, sensor_name, "address_hex", f"0x{found_addr:02X}")`    
    `else:`    
        `set_config_flag(CONFIG_PATH, sensor_name, "enabled", False)`    
        `set_config_flag(CONFIG_PATH, sensor_name, "i2c_bus", None)`  

`return detected`  

devices \= detect\_i2c\_sensors()

Key snippet \#2: Simple AudioMoth detection using `lsusb`  
 def detect\_audiomoth\_simple():  
 """Detect AudioMoth by lsusb only."""  
 try:  
 result \= subprocess.run(  
 \["lsusb"\],  
 capture\_output=True,  
 text=True,  
 check=True  
 )

   `for line in result.stdout.splitlines():`    
        `if "audiomoth" in line.lower():`    
            `set_config_flag(CONFIG_PATH, "audio", "enabled", True)`    
            `set_config_flag(CONFIG_PATH, "audio", "mount_path", None)`    
            `return True, f"AudioMoth detected: {line.strip()}"`  

`except Exception as e:`    
    `print(f"[detect] lsusb failed: {e}")`  

`set_config_flag(CONFIG_PATH, "audio", "enabled", False)`    
`set_config_flag(CONFIG_PATH, "audio", "mount_path", None)`    
`return False, "No AudioMoth USB device found."` 

---

**6\) Testing**


* For the BME280 issue, we tested the same sensor and code across multiple Pis. Detection only failed on one setup, and replacing the jumper wires fixed it immediately.  
* For I²C, I manually verified addresses using:  
   sudo i2cdetect \-y 1  
   sudo i2cdetect \-y 2  
* This confirmed TSL2591 at either `0x29` or `0x3A` and AHT at `0x38`, and the script correctly updated `config.json` with the detected bus and address.  
* For AudioMoth, I used `lsusb` to confirm detection and verified which devices enumerated as 48 kHz vs 384 kHz USB microphones, confirming the issue was firmware/config related rather than code related.  
* 

---

**7\) Lessons & Next Steps** 

* The BME280 issue was not a code problem but a wiring problem, which reinforced the importance of checking physical connections early.  
*  I²C detection needs to assume variation between nodes, so scanning multiple buses and addresses is necessary. AudioMoth USB microphone sample rate cannot be fixed from the Pi side and depends on using the correct USB microphone firmware and configuration workflow.   
* Next steps are to standardize all MicroMoths to the same 48 kHz USB microphone setup and keep using detect.py as a quick verification step before deployment.


---

**8\) References** 

* [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [https://www.openacousticdevices.info/audiomoth](https://www.openacousticdevices.info/audiomoth)

* [https://www.openacousticdevices.info/usb-microphone](https://www.openacousticdevices.info/usb-microphone)