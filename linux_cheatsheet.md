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
* **ssh {username}@{ip}** Allows you to ssh into another pi

# Commands for running and accessing files

* **nano {file\_name}.json** Allows you to edit and access json files through the terminal  
* **sudo python3 {file\_name}.py** Runs a python file
* **tail {file_name}** Slows the last couple lines of the file

# Other Tutorials

## How to clone a new repository on the supervisor

Run the following commands in order:

* **sudo rm -rf BEAMNode_Prototype1** This deletes the current respository on the supervisor
* **sudo bash ./enable_wifi.sh** Enables wifi on the supervisor so it is able to fine the new repository from the internet
* **git clone https://github.com/fmu-zwiers-ecuador/BEAMNode_Prototype1** Clones the new repository onto the supervisor
* **sudo reboot now** This reboots the pi so that when it comes back on, it disconnects from wifi and connects back to BATMAN

