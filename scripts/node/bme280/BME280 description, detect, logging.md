# **BME280 description, detection, JSON output/logging, and testing**

---
# Basic Sensor Description

**Sensor Description**

The BME280 is a small electronic environmental sensor developed by Adafruit. It records humidity, or how much moisture is present, along with temperature and air pressure, to help understand environmental conditions around the Raspberry Pi.
The sensor itself is small and is attached to a circuit board with labeled pins. These pins allow the wires to connect so the sensor can receive power and communicate with the Raspberry Pi. Once connected, the sensor continuously collects air data and sends it to the Raspberry Pi without requiring any user interaction, we’re just able to read the sensor’s current values and then log them.

**BME280 to Raspberry Pi Pin Assignments:**

VCC → Pin 1 (3.3V Power)

GND → Pin 6 (Ground)

SDA / MOSI → Pin 19 (GPIO10)

SCL / SCK → Pin 23 (GPIO11)

ADDR / MISO → Pin 21 (GPIO9)

CS → Pin 29 (GPIO5)

![GPIO Pin Diagram](https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2023/03/Raspberry-Pi-Pinout-Random-Nerd-Tutorials.png?quality=100&strip=all&ssl=1) 

**Detection Script Integration**

After wiring up the sensor, we developed a detection script that confirms whether the BME280 is present and responding. The script checks for a unique identification value, or it’s chip-ID, that only the BME sensor has. If that value is detected via SPI, the Raspberry Pi confirms that the sensor is connected correctly. We integrated this logic into a larger detection script that checks for all connected sensors.

Once the script finishes running, it automatically updates the config, or the configuration file. If the BME280 is detected, the sensor is marked as online. If it is not detected, the sensor is marked as offline. This configuration file is then read by other programs that collect environmental data, ensuring that only available sensors are used.


**Data Logging Script Integration**

Every hour, the BME280 data logging script runs and records environmental data from the sensor. The script reads the current temperature (°C), humidity (%), and air pressure (hPa) values from the BME280 and stores them along with a timestamp into a JSON file.

The script uses config.json file to determine whether the BME280 sensor is enabled. If the sensor is marked as disabled, the script exits without collecting data. This ensures that only available sensors are used during data collection.

When the script runs
By default, the data is stored in: home/pi/data/bme280/env_data.json, but the script dynamically determines the project root directory and creates a dedicated data folder for the BME280 if it does not already exist. 


Each time the script executes, a new dictionary containing the timestamp and environmental readings is appended to the records array inside the JSON file. The JSON structure includes the node ID, sensor name, and a list of recorded measurements.

After the data is written, the file is available for transfer into the shipping directory. The supervisor process then requests the most recent data from this folder for each node on an hourly basis.

---

# Script explanation

**Basic Info**

* **Primary Tasks For BME280** BME280 Detection to Config, Logging environmental data JSON output and verification  
* **Student(s):** Alexander Lance
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started / Completed for this documentation:** January 23rd, 2026 \- January 27th, 2026
* **Status:** Done  
* **GitHub Link:** [*https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/scripts/node/bme280/log_env_data.py*](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/bme280/log_env_data.py)
[*https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1/scripts/node/bme280/log_env_data.py*](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/tree/main/scripts/sensor_detection)
---

**1\) Summary**

The detect.py script sees whether or not the BME280 is available and updates the config.json. The log\_env\_data.py, BME280 logging script reads the temperature, humidity, and air pressure data and stores the values in a JSON file with a UTC timestamp. The data is saved locally on the Pi so it can then be collected by the supervisor.

---

**2\) Goals**

* Main goal(s): Ensure the BME280 is detected and sensor data (temperature, humidity, and pressure) is read correctly and logged to a JSON file


* How do we know it works? The script runs without error and appends new record with environmental data with updated timestamps each time it executes.

---

**3\) Setup**

*List what you used and how to set it up.*

* Hardware: Raspberry Pi 3, Adafruit BME280 Environmental  Sensor  
* Software: Python3, Vscode  
* Install/run steps: python3 scripts/node/sensor_detection/detect.py;
 python3 scripts/tsl2591/log\_lux\_data.py 

---

**4\) Method**
* To ensure that the proper libraries are installed, use command: 

pip3 install adafruit-circuitpython-tsl2591 --break-system-packages

* To ensure BME280 can be read, make sure SPI is enabled on PI.

*Check config.json to determine if node ID, SPI settings, and sensor status are correct

*Run log_env_data.py to: Read temperature (°C), humidity (%), and pressure (hPa) values from the sensor

*Created a JSON record containing a UTC timestamp and sensor readings

*Appended the record to the records array inside env_data.json

*Saved the updated JSON file to the BME280 data directory

---

**5\) Code**

* Main script(s): BEAMNode\_Prototype1/scripts/bme280/log\_env\_data.py  
* Example run: 

        python3 scripts/bme280/log_env_data.py  
        Env data appended to env_data.json at 2025-10-10 16:19:28.549835


    And

        cat data/bme280/env_data.json  
        {  
        "node_id": "beam-node-01",  
        "sensor": "bme280",  
        "records": [  
            {  
                "timestamp": "2025-10-10T15:26:58.609389+00:00",  
                "temperature_C": 22.4,  
                "humidity_percent": 48.7,  
                "pressure_hPa": 1012.6  
            }  
      ]  
  }

* Important snippet:

        # Read values
        temperature = float(sensor.temperature)
        humidity = float(sensor.humidity)
        pressure = float(sensor.pressure)

        # Directory and file for logs exist, create a 
        new dict if not  
        directory \= "home/pi/data/bme280/"

        # Target file (single JSON with a "records"
        array)  
        file\_name \= "env\_data.json"  
        file\_path \= os.path.join(directory,
        file\_name)


        # New record 
        env_json_data = {
            "timestamp": 
            datetime.now(timezone.utc).isoformat(),
            "temperature_C": temperature,
            "humidity_percent": humidity,
            "pressure_hPa": pressure
            }

        try:  
            data \= json.load(json\_file)  
            if not isinstance(data, dict) or "records"
            not in data:  
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

**6\) Testing**

**Noel for the log_env_data script:**

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

**7\) References**

* Links to GitHub repo, docs, guides, or other resources: [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1)

* [**https://forums.raspberrypi.com/search.php?keywords=json+file+bme280\&sid=603063906e27ef0fe9017deac3157f9f**](https://forums.raspberrypi.com/search.php?keywords=json+file+bme280&sid=603063906e27ef0fe9017deac3157f9f) **\-** Raspberrypi forums for help with JSON script

* [https://docs.circuitpython.org/projects/bme280/en/latest/api.html](https://docs.circuitpython.org/projects/bme280/en/latest/api.html) \- API reference for the BME280