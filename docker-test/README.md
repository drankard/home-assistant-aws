# Docker Test Environment for Home Assistant AWS Integration

This Docker setup is specifically designed for **testing purposes** of the Home Assistant AWS custom component. It provides a quick way to set up a containerized Home Assistant instance with the custom component already mounted and ready for testing.

## Developer Quick Start

1. **Start the test environment**:
   ```bash
   docker-compose up -d
   ```

2. **Access Home Assistant**:
   Open http://localhost:8123 in your browser

3. **Testing Your Changes**:
   - Any changes to the custom component in `../custom_components` are mounted in the container
   - After making changes, you need to restart Home Assistant for them to take effect
   - Restart Home Assistant inside the container using one of these methods:
     ```bash
     # Option 1: Using the built-in restart script (easiest)
     docker exec homeassistant_aws_test restart-ha
     
     # Option 2: Restart the container (slower but always works)
     docker restart homeassistant_aws_test
     ```
   - Use this environment to develop and test your code without affecting your main Home Assistant instance
   - You can add your own automations to test the component functionality

## Example Automations

Check the `examples` directory for sample automations that demonstrate how to use the AWS component. These examples are a great starting point to understand the component's capabilities.

## Technical Details

- AWS integration is mounted from `../custom_components` to `/config/custom_components`
- Configuration files are mounted from local `mounted-config` directory
- Container restarts automatically unless stopped manually
- Home Assistant version: 2024.4 
- Developer mode is enabled with auto-reloading of custom components 