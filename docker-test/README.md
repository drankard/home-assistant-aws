# Docker Test Environment for Home Assistant AWS Integration

This directory contains a Docker-based test environment for the Home Assistant AWS Integration.

## Structure

- `config/` - Contains configuration template files for Home Assistant
- `data/` - Contains all runtime data and the `.storage` directory (git-ignored)
- `docker-compose.yml` - Docker Compose configuration
- `Dockerfile` - Builds the container with the setup script
- `setup.sh` - Setup script that runs inside the container
- `cleanup.sh` - Script to clean up unnecessary files

## Usage

1. **Start the environment**:
   ```bash
   docker-compose up -d
   ```

2. **Access Home Assistant**:
   Open http://localhost:8123 in your browser

3. **Login**:
   - Username: admin
   - Password: Password is derived from a hash in setup.sh

## Cleanup

When you're done, stop the container and clean up:

```bash
./cleanup.sh
```

The cleanup script:
- Stops any running containers
- Removes all files in the data directory (except for an empty `.storage` directory)
- Removes any other unnecessary files
- Ensures the directory structure remains intact

## Technical Details

- The docker-compose.yml:
  - Builds the Docker image from the Dockerfile
  - Mounts `./data` to `/data` in the container for all runtime data
  - Mounts individual configuration files from `./config` to `/data` in the container
  - Mounts `../custom_components` to `/data/custom_components` for the AWS integration

- The setup script:
  - Creates necessary directories and files
  - Sets up Home Assistant authentication
  - Ensures the AWS integration is enabled

- All runtime files are stored in the `data` directory, making cleanup easy 