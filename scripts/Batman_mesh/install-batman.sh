#!/bin/bash
# ========================================
# BATMAN-adv Automatic Setup Script (Interactive)
# Tested on Debian / Raspberry Pi OS
# ========================================

set -e

echo "=== BATMAN-adv Setup Script ==="
echo

# --- Ask for configuration with defaults ---
read -p "Enter ad-hoc network name (SSID) [myadhoc]: " NETWORK_NAME
NETWORK_NAME=${NETWORK_NAME:-myadhoc}

read -p "Enter frequency in MHz (e.g. 2412 for channel 1) [2412]: " FREQUENCY
FREQUENCY=${FREQUENCY:-2412}

read -p "Enter static IP for bat0 (e.g. 192.168.1.2/24) [192.168.1.2/24]: " STATIC_IP
STATIC_IP=${STATIC_IP:-192.168.1.2/24}

echo
echo "Using configuration:"
echo "  SSID:        $NETWORK_NAME"
echo "  Frequency:  $FREQUENCY MHz"
echo "  IP Address: $STATIC_IP"
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

# --- Create BATMAN startup script ---
echo "[1/4] Creating /usr/local/bin/start-batman.sh ..."
cat <<EOF | sudo tee /usr/local/bin/start-batman.sh >/dev/null
#!/bin/bash
# ========================================
# BATMAN-adv Startup Script
# ========================================

echo "Starting BATMAN-adv mesh setup..."

# Stop and mask conflicting services (Masking is better for mesh stability)
systemctl stop wpa_supplicant NetworkManager 2>/dev/null || true
systemctl mask wpa_supplicant 2>/dev/null || true

# Load BATMAN kernel module
modprobe batman-adv

# Configure wlan0 for ad-hoc mode
ip link set wlan0 down
# Set MTU to 1532 to accommodate BATMAN encapsulation overhead
ip link set wlan0 mtu 1532
iw dev wlan0 set type ibss
ip link set wlan0 up

# Pi Zero: Disable Wi-Fi power saving to prevent the node from dropping
iw dev wlan0 set power_save off

# Join the ad-hoc cell (Fixed syntax error by using variables)
sleep 1
iw dev wlan0 ibss join $NETWORK_NAME $FREQUENCY

# Add wlan0 to BATMAN
batctl if add wlan0
sleep 1
ip link set up dev bat0

# Assign static IP (Handles the full range like 192.168.1.2/24)
ip addr add $STATIC_IP dev bat0

echo "BATMAN-adv setup complete!"
EOF

sudo chmod +x /usr/local/bin/start-batman.sh

# --- Create systemd service ---
echo "[2/4] Creating /etc/systemd/system/batman.service ..."
cat <<EOF | sudo tee /etc/systemd/system/batman.service >/dev/null
[Unit]
Description=BATMAN-adv Mesh Network
After=network.target sys-subsystem-net-devices-wlan0.device
Wants=sys-subsystem-net-devices-wlan0.device

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/start-batman.sh

[Install]
WantedBy=multi-user.target
EOF

# --- Reload systemd and enable service ---
echo "[3/4] Reloading systemd and enabling service ..."
sudo systemctl daemon-reload
sudo systemctl enable batman.service

# --- Start service immediately ---
echo "[4/4] Starting BATMAN service ..."
sudo systemctl restart batman.service

echo
echo "✅ BATMAN-adv setup complete!"
echo "To verify, run: sudo systemctl status batman.service"
echo "Then check mesh neighbors with: sudo batctl n"
