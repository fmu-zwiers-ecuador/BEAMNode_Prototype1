# BATMAN-adv Setup on Linux (Ad-Hoc Mesh Networking)

This guide explains how to install and configure **BATMAN-adv** on Linux (tested on Raspberry Pi / Debian systems).  
The setup ensures that the system automatically configures BATMAN-adv at boot using a systemd service.

---

## Installation & Setup

Follow these steps to set up BATMAN-adv.

---

### 1. Install Batman Package

sudo apt install batctl

---

### 2. Create the startup script

Create the file `/usr/local/bin/start-batman.sh` with the following contents:

```bash
#!/bin/bash

# Stop and disable conflicting services
systemctl stop wpa_supplicant        # stops WPA supplicant (used for WiFi management)
systemctl disable wpa_supplicant     # disables WPA supplicant on boot
systemctl stop NetworkManager        # stops NetworkManager (manages WiFi/eth)
systemctl disable NetworkManager     # disables NetworkManager on boot

# Load BATMAN module (kernel mesh networking driver)
modprobe batman-adv

# Configure wlan0 for IBSS (ad-hoc mode)
ip link set wlan0 down               # bring interface down before reconfiguring
iw dev wlan0 set type ibss           # set wlan0 to IBSS (ad-hoc) mode
ip link set wlan0 up                 # bring wlan0 back up
sudo iw dev wlan0 ibss join <network_name> <frequency>  
# join an ad-hoc network with SSID and frequency
# Example: sudo iw dev wlan0 ibss join myadhoc 2412

# Add wlan0 to BATMAN
batctl if add wlan0                  # attach wlan0 to BATMAN virtual interface
ip link set up dev bat0              # bring bat0 (BATMAN virtual interface) up

# Assign static IP address to bat0
ip addr add 192.168.x.x/24 dev bat0  
# Example: ip addr add 192.168.1.2/24 dev bat0
```

Make the script executable:

```bash
sudo chmod +x /usr/local/bin/start-batman.sh
```

---

### 3. Create the systemd service

Create the file `/etc/systemd/system/batman.service` with the following contents:

```ini
[Unit]
Description=BATMAN-adv Mesh Network
After=network.target sys-subsystem-net-devices-wlan0.device   # start after network + wlan0 detected
Wants=sys-subsystem-net-devices-wlan0.device                  # ensures wlan0 exists

[Service]
Type=oneshot                   # run script once and exit
RemainAfterExit=yes            # keeps service marked "active" after script runs
ExecStart=/bin/bash /usr/local/bin/start-batman.sh   # path to startup script

[Install]
WantedBy=multi-user.target     # start at normal multi-user boot (default runlevel)
```

---

### 4. Enable the service

Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload      # reload systemd configs
sudo systemctl enable batman.service   # enable service at boot
sudo systemctl start batman.service    # start service immediately
```

---

### 5. Verify the service

Check status:

```bash
sudo systemctl status batman.service
```

If successful, it should display:

```
Active: active (running)
```

---

## Notes

- It may take **~10 seconds** after boot for all commands to finish in the background before running:
  ```bash
  sudo batctl n
  ```
- Replace `<network_name>` and `<frequency>` with your own mesh configuration.  
- Replace `192.168.x.x` with the correct IP scheme for your mesh.
