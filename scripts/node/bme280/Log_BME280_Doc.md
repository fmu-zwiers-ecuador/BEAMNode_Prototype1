# **Log BME280 values to JSON**

---

**Basic Info**

* **Task Title:** Log BME280 values to JSON 
*  **Student(s):** Alexander Lance  
*  **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
*  **Date Started / Completed:** September 29th, 2025 \-  October 10th, 2025  
*  **Status:** Done:   
*  **GitHub Link:** [*https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/scripts/node/bme280/log_env_data.py*](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/bme280)

---

## **1\) Summary**

I created the log\_env\_data.py script, which can read the temperature, humidity, and pressure from the BME280 sensors and save the data to a JSON file every hour to the directory data/bme280/. A timestamp is created to follow the proper JSON  format expected with the desired date. I made sure that the environmental data does not write over itself and appends to the same document. I also created a test\_env\_data to read and print the desired environmental data.

---

## **2\) Goals**

* **Main goal:** Log and append environmental data to a single JSON document that can be implemented to grow hourly. That JSON document should be sent from the pi for confirmation.  
* **Works when:** Running the logger manually adds a new record to home/pi/data/bme280/env\_data.json. and  appends when run again  
* **Should Print** "Env data appended to {file\_name} at {datetime.now()}"  
* Check /home/pi/data/bme280 for the json file, makes sure it includes   
* "timestamp": datetime.now(timezone.utc).isoformat(),  
*     "temperature\_C": temperature,  
*     "humidity\_percent": humidity,  
*     "pressure\_hPa": pressure  
* Use SCP commands to send JSON file to home computer

---

## 

## **3\) Setup**

**Hardware**

* Hardware: Raspberry Pi 3, Adafruit BME280 Temperature Humidity Pressure Sensor  
* Software: Thonny IDE, BASH Shell, Python3, Vscode  
  * Packages: `p3 install adafruit-circuitpython-bme280 adafruit-blinka,` python3-spidev, python3-rpi.gpio (RPi.GPIO), 

* Install/Run Steps: sudo apt install python3-spidev python3-rpi.gpio  
  * python3 log\_env\_data.py  
  * python3 test\_env\_data.py

---

**4\) Method** 

* Use the Adafruit CircuitPython BME280 library over SPI.  
* Initialize SPI via busio.SPI(board.SCK, board.MOSI, board.MISO) and set CS to DigitalInOut(board.D5).  
* Read values via sensor.temperature, sensor.humidity, sensor.pressure.  
* Append to one JSON file (data/bme280/env\_data.json):  
* If file exists, load it and ensure structure { "node\_id": "...", "sensor": "bme280", "records": \[\] }.  
* Append new record { timestamp, temperature\_C, humidity\_percent, pressure\_hPa }.  
* Verify growth using cat, reading the file from bash  
* Ssh from home computer  to send the JSON file to:   
* $ts \= Get-Date \-Format "yyyyMMdd\_HHmmss"  
* PS C:\\Users\\(homeuser)\> $dest \= "$env:USERPROFILE\\Documents\\env\_data\_$ts.json"  
* PS C:\\Users\\(homeuser)\> scp pi@(ip):/home/pi/data/bme280/env\_data.json $dest  
* 

---

**5\) Code** 

* Main script(s): http://BEAMNode\_Prototype1/scripts/bme280/  
* Run with command:

* python log\_env\_data.py  
* python test\_env\_data.py  
    
* Important Functions:

log\_env\_data.py  
\# Read sensor values  
temperature \= float(sensor.temperature)  
humidity    \= float(sensor.humidity)  
pressure    \= float(sensor.pressure)

\# Directory for saving logs  
directory \= "home/pi/data/bme280/"

\# Target file (single JSON with a "records" array)  
file\_name \= "env\_data.json"  
file\_path \= os.path.join(directory, file\_name)

\# New record  
env\_json\_data \= {  
    "timestamp": datetime.now(timezone.utc).isoformat(),  
    "temperature\_C": temperature,  
    "humidity\_percent": humidity,  
    "pressure\_hPa": pressure  
}  
try:  
                data \= json.load(json\_file)  
                if not isinstance(data, dict) or "records" not in data:  
                    data \= {  
                        "node\_id": "beam-node-01",  
                        "sensor": "bme280",  
                        "records": \[\]  
                    }  
 \# Append and write back  
    data\["records"\].append(env\_json\_data)  
    with open(file\_path, "w") as json\_file:  
        json.dump(data, json\_file, indent=4)

    print(f"Env data appended to {file\_name} at {datetime.now()}")

test\_env\_data.py

sensor \= basic.Adafruit\_BME280\_SPI(spi, cs, baudrate=100000)

print("Temperature (C):", sensor.temperature)  
print("Humidity (%):",    sensor.humidity)  
print("Pressure (hPa):",  sensor.pressure)

---

**6\) Testing  \***

* I pulled the latest version of the script from the main GitHub repository to the pi  
* Then I ran the log\_env\_data.py script and made sure there were no errors, and received expected:   
* Env data appended to env\_data.json at 2025-10-10 16:40:13.907867

* Then I went to the home/pi/data/bme280 directory and confirmed that the JSON file was being created correctly and contained the proper structure and data fields. I also verified that each  run of the script appended a new record to the existing JSON file  
* This ensured that the script was correctly reading the sensor values and saving them to the JSON file in the desired format.  
* Also used cat /home/pi/data/bme280/env\_data.json to verify

* Ran test\_env\_data.py; received output:  
* Temperature (C): 19.3640  
* Humidity (%): 49.7926  
* Pressure (hPA): 1021.7120

---

**7\) Lessons & Next Steps** 

* I found that it was very important to learn the API or library for any language or package you’re using. Early on, I made the mistake of trying to call Adafruit\_BME280\_SPI directly without properly importing basic. I just assumed the function existed in the base library. This led to initialization errors and set me back until I reviewed the documentation and adjusted my code accordingly.

* I also ran into the issue of continuously trying to SSH from my computer to the Pi over the campus guest wifi, even redownloading SSH capabilities on Windows, instead of just simply asking and collaborating, finding out that you are not able to SSH over campus guest, wasting a day of progress.

* For future work, I plan to refine the logging script to handle exceptions more effectively and potentially integrate error messages. With my upcoming task, checking for detection for the camera, I am able to use everything I’ve learned from these past two contracts. 

* **For Future Students:**

* Always double-check that you are importing the correct modules and initializing the sensor in the way the API expects, and don’t assume functions exist without confirming in the documentation.  
* Regularly check your output files to ensure data is being logged correctly with a quick cat or jq command to save on debugging time.  
* Also, don’t waste time troubleshooting network issues when you have to ability to ask for clarification. Simply asking and collaborating early on will have saved you a full day of progress.


---

**8\) References \***

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [**https://forums.raspberrypi.com/search.php?keywords=json+file+bme280\&sid=603063906e27ef0fe9017deac3157f9f**](https://forums.raspberrypi.com/search.php?keywords=json+file+bme280&sid=603063906e27ef0fe9017deac3157f9f) **\-** Raspberrypi forums for help with JSON script

* [https://docs.circuitpython.org/projects/bme280/en/latest/api.html](https://docs.circuitpython.org/projects/bme280/en/latest/api.html) \- API reference for the BME280