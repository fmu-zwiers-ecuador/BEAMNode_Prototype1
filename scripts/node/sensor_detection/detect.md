**TSL2591 Detection and Driver Check Documentation** 

---

**Basic Info**

* **Task Title:** TSL detection and driver implementation  
* **Student(s):** Jaylen Small  
* **Mentor/Reviewer:** Dr. Paul Zwiers / Raiz Mohammed  
* **Date Started / Completed:** September 15th, 2025 \-  September 26th, 2025  
* **Status:** Done  
* **GitHub Link:** [testlux.py](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/scripts/testlux.py), [detect.py](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1/blob/main/detect.py)

---

**1\) Summary**

I built two scripts. The testlux.py script was simply built to ensure that the TSL2591(light sensor) was detecting light properly. The detect.py script ensures that the TSL2591 is actually detected through i2c and logs its output into detect\_tsl2591.log.

---

**2\) Goals**

* Main goal(s): Test to ensure that the TSL2591 is reading from the lux and that it is plugged into the i2c board and is being detected  
* How do we know it works? Both scripts run without error and returns the expected output

---

**3\) Setup**

*List what you used and how to set it up.*

* Hardware: Raspberry Pi 3, Adafruit TSL2591 High Dynamic Range Digital Light Sensor  
* Software: Python3, Vscode  
* Install/run steps: python3 textlux.py and python3 detect.py

---

**4\) Method**

* Ran sudo i2cdetect \-y 1 to make sure that address “0x29” was on the table

* In the scan\_i2c() function, I made it so that command is ran automatically and returns the result

* The result of scan\_i2c() is then passed into the get\_devices() function where it looks for the memory address of “0x29”. If so, return it.

* Then the output of “TSL2591 detected” is logged into detect\_tsl2591.log

---

**5\) Code**

* Main script(s): BEAMNode\_Prototype1/scripts/detectlux.py and BEAMNode\_Prototype1/detect.py  
* Example run: 

python3 testlux.py   
Lux: 12.59567

And

python3 detect.py   
The following sensors are online: TSL2591

* Important snippet:

\# Function2 \- get\_devices(adds) \- Take in output from i2c detect, parse,  
\# return which sensors are currently online  
def get\_devices(adds):

    \# check adds for \-1, if so, return error \#  
    if adds \== \-1:  
        return "There are no available sensors"

    detected\_sensors \= \[\]

    address\_matches \= re.findall(r"\\b\[0-9a-f\]{2}\\b", adds, re.IGNORECASE)  
    found\_addrs \= \[int(addr, 16\) for addr in address\_matches\]

    for sensor\_name, sensor\_addr in addr\_table.items():  
        if sensor\_addr in found\_addrs:  
            detected\_sensors.append(sensor\_name)  
            logging.info(f'{sensor\_name} detected.')  
      
    return detected\_sensors  
---

**6\) Testing**

* I would write the code on my laptop then push it into the main repository

* I would then pull from the repository on the pi I was testing on and run the scripts from the terminal

---

**7\) Lessons & Next Steps**

* Once I understood how the pis worked and how it interacted with the sensors, all the pieces fell into place pretty smoothly  
* The main problems I faced were the steep learning curve for me because I’ve had very little experience with python for this project and no experience at all with Raspberry Pis  
* For any future students joining the project, I recommend that they familiarize themselves with all of the components on the pi ship and know where all of the pins the sensors are plugged into are located. It will make testing a lot easier.

---

**8\) References**

* [https://pinout.xyz/](https://pinout.xyz/) \- An interactive guide for learning all of the pins on the pi

* [https://docs.circuitpython.org/projects/tsl2591/en/stable/api.html](https://docs.circuitpython.org/projects/tsl2591/en/stable/api.html) \- API reference for the TSL2591

* [https://github.com/fmu-zwiers-ecuador/BEAMNode\_Prototype1](https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1) \- The main repository 

