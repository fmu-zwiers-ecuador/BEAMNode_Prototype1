**TSL2591 JSON output and verification Documentation** 

---

**Basic Info**

* **Task Title:** TSL2591 JSON output and verification  
* **Student(s):** Jaylen Small  
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started / Completed:** September 29th, 2025 \-  October 11th, 2025  
* **Status:** Done  
* **GitHub Link:** [log\_lux\_data.py](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/scripts/tsl2591/log_lux_data.py) 

---

**1\) Summary**

The log\_lux\_data script grabs the lux data from the TSL light sensor and stores it into a json file with a specified timestamp. This data is stored onto the data folder on the home pi folder(file path being: home/pi/data)

---

**2\) Goals**

* Main goal(s): Test to ensure that the lux data from the TSL2591 is being read and stored into a json file with updating timestamps  
* How do we know it works? The script runs without error and appends the json file with new information everytime the script is run

---

**3\) Setup**

*List what you used and how to set it up.*

* Hardware: Raspberry Pi 3, Adafruit TSL2591 High Dynamic Range Digital Light Sensor  
* Software: Python3, Vscode  
* Install/run steps: python3 scripts/tsl2591/log\_lux\_data.py 

---

**4\) Method**
* To insure that the proper libaries are installed, use command: 

pip3 install adafruit-circuitpython-tsl2591 --break-system-packages

* In the script, the main json file is sorted into a dictionary with variables: "node\_id": "beam-node-01", "sensor": "tsl2591", and "records": \[\]. In the records array, that is where the lux data dictionary will be appended and stored.

  * When the script is run, it makes a new dictionary with variables: "timestamp": datetime.now(timezone.utc).isoformat(), and "lux": lux. Then the records array is appended with the new data.

* Ran python scripts/tsl2591/log\_lux\_data.py to log the current lux data into the lux\_data.json file.

* Ran cat home/pi/data/tsl2591/lux\_data.py to verify that the data is being saved and appended correctly.

---

**5\) Code**

* Main script(s): BEAMNode\_Prototype1/scripts/tsl2591/log\_lux\_data.py  
* Example run: 

python3 scripts/tsl2591/log\_lux\_data.py   
Lux data appended to lux\_data.json at 2025-10-10 16:19:28.549835

And

cat data/tsl2591/lux\_data.json   
{  
	“node\_id”: “beam-node-01”,  
	“sensor”: tsl2591”,  
	“records”: \[  
		{  
			“timestamp”: “2025-10-08T16:11:48.024263+00:00”,  
			“lux”: 44.018304  
		},  
		{  
			“timestamp”: “2025-10-10T15:19:28.542859+00:00”,  
			“lux”: 0.0  
		},  
		{  
			“timestamp”: “2025-10-10T15:26:58.609389+00:00”,  
			“lux”: 82.81420800001  
		}  
	\]  
}

* Important snippet:

try:  
    \# Attempt to load existing data if it exist, create a new dict if not  
    if os.path.exists(file\_path):  
        with open(file\_path, 'r') as json\_file:  
            data \= json.load(json\_file)  
            if not isinstance(data, dict) or "records" not in data:  
                data \= {  
                    "node\_id": "beam-node-01",  
                    "sensor": "tsl2591",  
                    "records": \[\]  
                }  
    else:  
        data \= {  
            "node\_id": "beam-node-01",  
            "sensor": "tsl2591",  
            "records": \[\]  
        }

    \# Append the new data  
    data\["records"\].append(new\_lux\_data)

    \# Save back to the file  
    with open(file\_path, 'w') as json\_file:  
        json.dump(data, json\_file, indent\=4)

    print(f"Lux data appended to {file\_name} at {datetime.now()}")  
except Exception as e:  
     print(f"Error saving lux data: {e}")

---

**6\) Testing**

* I would write the code on my laptop then push it into the main repository

* I would then pull from the repository on the pi I was testing on and run the scripts from the terminal

* I would run cat checks on the json files to ensure that the data was appending as intended

---

**7\) Lessons & Next Steps**

* Once I understood how the pis worked and how it interacted with the sensors, all the pieces fell into place pretty smoothly  
* The main problems I faced were the steep learning curve for me because I’ve had very little experience with python for this project and no experience at all with Raspberry Pis  
* For any future students joining the project, I recommend that they familiarize themselves with all of the components on the pi ship and know where all of the pins the sensors are plugged into are located. It will make testing a lot easier.

---

**8\) References**

* [https://docs.circuitpython.org/projects/tsl2591/en/stable/api.html](https://docs.circuitpython.org/projects/tsl2591/en/stable/api.html) \- API reference for the TSL2591

* [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1) \- The main repository

* [https://www.w3schools.com/python/module\_os.asp?ref=escape.tech](https://www.w3schools.com/python/module_os.asp?ref=escape.tech) \- API reference for the python os library 

* [https://www.w3schools.com/python/python\_json.asp](https://www.w3schools.com/python/python_json.asp) \- API reference for the python json library  