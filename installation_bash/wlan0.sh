#!/usr/bin/env bash
set -euo pipefail

IFACE="wlan0"
CONF="/etc/wpa_supplicant/wpa_supplicant-${IFACE}.conf"

# ===== EDIT THESE =====
SSID="FMU"
IDENTITY="noel.challa"
PASSWORD="fmu88153"
COUNTRY="US"
# =====================

if [[ $EUID -ne 0 ]]; then
  echo "Run as root:"
  echo "  sudo $0"
  exit 1
fi

echo "== Writing wpa_supplicant config for $IFACE =="
umask 077
cat > "$CONF" <<EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=$COUNTRY

network={
    ssid="$SSID"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="$IDENTITY"
    password="$PASSWORD"
    phase2="auth=MSCHAPV2"
    priority=1
}
EOF

echo "== Bringing $IFACE up =="
ip link set "$IFACE" up || true

echo "== Restarting wpa_supplicant on $IFACE =="
pkill -f "wpa_supplicant.*-i$IFACE" 2>/dev/null || true
wpa_supplicant -B -i "$IFACE" -c "$CONF"

echo "== Requesting DHCP lease =="
dhcpcd -n "$IFACE" 2>/dev/null || dhcpcd "$IFACE"

echo "== Connection status =="
iw dev "$IFACE" link || true
ip -4 addr show dev "$IFACE" || true

echo "✅ University Wi-Fi setup complete for $IFACE"
