#!/bin/sh
# Restart Home Assistant service script
# This script will find and restart the Home Assistant service using s6

# Find the Home Assistant service directory
HA_SERVICE_PATH=$(find /var/run/s6 -path "*/home-assistant/supervise" -print 2>/dev/null | head -n 1 | sed 's|/supervise$||')

if [ -z "$HA_SERVICE_PATH" ]; then
  echo "Error: Could not find Home Assistant service path"
  exit 1
fi

echo "Restarting Home Assistant service at: $HA_SERVICE_PATH"
# Restart the service 
s6-svc -r "$HA_SERVICE_PATH"

# Check if restart was successful
if [ $? -eq 0 ]; then
  echo "Home Assistant service restarted successfully"
else
  echo "Failed to restart Home Assistant service"
  exit 1
fi 