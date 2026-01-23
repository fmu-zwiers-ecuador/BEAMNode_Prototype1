# BATMAN Commands

* **sudo batctl n** Shows the neighboring nodes connected to BATMAN  
* **sudo batctl o** Shows the originators that the supervisor can see

# Sudo Commands

* **sudo rm \-rf {repo\_name}** Deletes the specified repository  
* **sudo i2cdetect \-y {bus number}** Show the connected sensors and their memory address in the specified bus  
* **sudo reboot now** Reboots the pi

# Rsync Commands

* **rsync \-avz /home/pi/BEAMNode\_Prototype1 pi@192.168.1.{node number}:/home/pi/** Sends the BEAMNode folder from the supervisor, to the specified node

# Wifi Commands

* **ping \-c 3 \-W 1 192.168.1.{node number}** Tests and displays the ping for the specified node  
* **sudo bash enable\_wifi.sh** Runs a bash script to enable wifi on the supervisor

# Commands for running and accessing files

* **nano {file\_name}.json** Allows you to edit and access json files through the terminal  
* **sudo python3 {file\_name}.py** Runs a python file

