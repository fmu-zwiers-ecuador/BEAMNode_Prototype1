#!/bin/bash

# =====================================================================
# === PART 1: Install all necessary libraries needed for for set up ===
# =====================================================================

set -euo pipefail

sudo apt update
sudo apt install -y \
  python3-pip python3-venv \
  libportaudio2 libjack0 \
  python3-pyaudio \
  batctl

# Create required data + log roots for the node runtime
sudo mkdir -p /home/pi/data /home/pi/shipping /home/pi/logs /home/pi/BEAMNode_Prototype1/logs
sudo chown -R pi:pi /home/pi/data /home/pi/shipping /home/pi/logs /home/pi/BEAMNode_Prototype1/logs

# Upgrade pip tooling (system-wide). --break-system-packages is for Debian/RPi OS policy.
sudo python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Adafruit + sensors
sudo python3 -m pip install --break-system-packages \
  adafruit-blinka==8.69.0 \
  adafruit-circuitpython-bme280==2.6.30 \
  adafruit-circuitpython-tsl2591==1.4.6 \
  adafruit-circuitpython-ahtx0==1.0.28

# NOTE:
# Do NOT apt install portaudio19-dev here (it can force exact-matching -dev deps and break on some Pi repos).
# If you ever *must* use pip's PyAudio instead, the typical requirement is:
#   sudo apt install libportaudio2 libjack0
#   pip3 install pyaudio
# (ideally inside a venv).  [oai_citation:1‡piwheels.org](https://www.piwheels.org/project/pyaudio/?utm_source=chatgpt.com)

sudo apt upgrade -y


# ======================================
# === PART 2: Autostart installation ===
# ======================================

# Location: /home/pi/BEAMNode_Prototype1/autostartinstall.sh

# 1. Configuration
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
NODE_DIR="$PROJECT_ROOT/scripts/node"
SERVICE_SRC="$PROJECT_ROOT/beamnode.service"
SERVICE_NAME="beamnode.service"
LOG_DIR="$PROJECT_ROOT/logs"

# 2. Create Required Folders
echo "[1/4] Preparing directories..."
mkdir -p "/home/pi/data"
mkdir -p "/home/pi/shipping"
mkdir -p "$LOG_DIR"

# 3. Set Permissions
echo "[2/4] Setting execution permissions..."
chmod +x "$NODE_DIR/launcher.py"
chmod +x "$NODE_DIR/scheduler.py"
chmod +x "$NODE_DIR/sensor_detection/detect.py"
chmod +x "$NODE_DIR/shipping_queuing/shipping.py"

# 4. Install Systemd Service
echo "[3/4] Registering systemd service..."
if [ -f "$SERVICE_SRC" ]; then
    # Copy from project root to system services folder
    sudo cp "$SERVICE_SRC" /etc/systemd/system/
    
    # Reload and Enable
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    # Start the service now
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Service $SERVICE_NAME installed and started."
else
    echo "❌ ERROR: Could not find $SERVICE_SRC"
    echo "Please ensure beamnode.service is in $PROJECT_ROOT"
    exit 1
fi

# 5. Verification
echo "[4/4] Verifying system status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "------------------------------------------------"
    echo "🎉 SUCCESS: Installation Complete!"
    echo "The Launcher is now running in the background."
    echo "------------------------------------------------"
else
    echo "⚠️ Service installed but failed to start."
    echo "Check logs with: journalctl -u $SERVICE_NAME -f"
fi


# =============================
# === PART 3: Setup crontab ===
# =============================

# --- CONFIGURATION ---
# Paths derived from the BEAMNode Project structure
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
SCRIPTS_DIR="$PROJECT_ROOT/scripts/node"
LOGS_DIR="/home/pi/logs"

# Ensure the log directory exists to capture cron output
mkdir -p "$LOGS_DIR"

# --- STEP 1: SET PERMISSIONS ---
# Granting execution permissions to essential BEAMNode scripts
echo "Setting execution permissions..."
chmod +x "$SCRIPTS_DIR/scheduler.py"
chmod +x "$SCRIPTS_DIR/shipping_queuing/shipping.py"
chmod +x "$SCRIPTS_DIR/sensor_detection/detect.py"
chmod +x "$SCRIPTS_DIR/launcher.py"

# --- STEP 2: CONSTRUCT CRONTAB ---
# Create a temporary file to safely handle crontab installation
TMP_CRON=$(mktemp)

# Load existing user crontab into the temp file
crontab -l > "$TMP_CRON" 2>/dev/null

# Define the BEAMNode cron block as seen in the system reference
# Using markers allows this script to be re-run without creating duplicates
CRON_BLOCK="
# === BEAMNode cron (managed) BEGIN ===
@reboot /bin/bash -lc 'sleep 5; echo \"[\$(date -Is)] cron boot hook ran\" >> $LOGS_DIR/cron_install.log'
@reboot /bin/bash -lc 'sleep 60; /usr/bin/python3 $SCRIPTS_DIR/scheduler.py >> $LOGS_DIR/scheduler.log 2>&1'
0 17 * * * /bin/bash -lc '$SCRIPTS"


# ===========================
# === BATMAN Installation ===
# ===========================

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
echo "  SSID:       $NETWORK_NAME"
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

# Stop and disable conflicting services
systemctl stop wpa_supplicant 2>/dev/null || true
systemctl disable wpa_supplicant 2>/dev/null || true
systemctl stop NetworkManager 2>/dev/null || true
systemctl disable NetworkManager 2>/dev/null || true

# Load BATMAN kernel module
modprobe batman-adv

# Configure wlan0 for ad-hoc mode
ip link set wlan0 down
iw dev wlan0 set type ibss
ip link set wlan0 up
iw dev wlan0 ibss join $NETWORK_NAME $FREQUENCY

# Add wlan0 to BATMAN
batctl if add wlan0
ip link set up dev bat0

# Assign static IP
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
ExecStart=/bin/bash /usr/local/bin/start-batman.sh

[Install]
WantedBy=multi-user.target
EOF

# --- Reload systemd and enable service ---
echo "[3/4] Reloading systemd and enabling service ..."
sudo systemctl daemon-reload
sudo systemctl enable batman.service

# --- Start service immediately ---
echo "[4/4] Starting BATMAN service ..."
sudo systemctl start batman.service

echo
echo "✅ BATMAN-adv setup complete!"
echo "To verify, run: sudo systemctl status batman.service"
echo "Then check mesh neighbors with: sudo batctl n"