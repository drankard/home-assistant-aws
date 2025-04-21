FROM homeassistant/home-assistant:2025.4

# Copy setup script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy restart script and make it executable
COPY restart-ha.sh /usr/local/bin/restart-ha
RUN chmod +x /usr/local/bin/restart-ha

COPY config-files/configuration.yaml /config/configuration.yaml
COPY config-files/automations.yaml /config/automations.yaml

# Launch Home Assistant with our setup script
ENTRYPOINT ["/entrypoint.sh"] 