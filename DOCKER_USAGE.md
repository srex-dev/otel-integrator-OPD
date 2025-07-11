# Docker Usage Guide

## Quick Start

### Build the Image
```bash
docker build -t otel-integrator:latest .
```

### Run Basic Discovery
```bash
docker run --rm otel-integrator:latest run --enhanced
```

### Run with Volume Mounting (Recommended)
```bash
# Mount current directory to /data in container
docker run --rm -v $(pwd):/data otel-integrator:latest run --enhanced --scan-path /data
```

## Common Commands

### Discovery and Config Generation
```bash
# Standard discovery
docker run --rm -v $(pwd):/data otel-integrator:latest run --scan-path /data

# Enhanced discovery (recommended)
docker run --rm -v $(pwd):/data otel-integrator:latest run --enhanced --scan-path /data
```

### Validation and Health Checks
```bash
# Validate generated config
docker run --rm -v $(pwd):/data otel-integrator:latest validate

# Check backend services health
docker run --rm -v $(pwd):/data otel-integrator:latest check-backends

# Check instrumentation
docker run --rm -v $(pwd):/data otel-integrator:latest check-instrumentation

# Check TLS certificates
docker run --rm -v $(pwd):/data otel-integrator:latest check-tls
```

### Install and Run Collector
```bash
# Install collector with generated config
docker run --rm -v $(pwd):/data otel-integrator:latest install

# Health check on collector
docker run --rm -v $(pwd):/data otel-integrator:latest health-check
```

### Automatic SDK Installation

To automatically install the required OpenTelemetry SDKs for Python, Node.js, and Java projects in your mounted directory, run:

```bash
docker run --rm -v $(pwd):/data otel-integrator:latest install-sdks --scan-path /data
```
- Installs Python SDK system-wide if Python services are detected.
- Installs Node.js SDK in each detected Node.js project directory.
- Downloads the latest OpenTelemetry Java agent JAR into each detected Java project directory.
- Silent, no prompts. Custom project paths supported via --scan-path.

## Volume Mounting

The `-v $(pwd):/data` flag mounts your current directory to `/data` inside the container. This allows the tool to:

- Scan your local filesystem for services
- Generate config files in your local directory
- Access your project files for discovery

## Output Files

When you run the tool with volume mounting, it will generate:

- `output/otel-config.env` - Environment variables
- `output/generated-configs/otel-collector-config.yaml` - Collector configuration
- `output/setup-instructions.md` - Setup instructions

## Examples

### Scan a Specific Directory
```bash
docker run --rm -v /path/to/your/project:/data otel-integrator:latest run --enhanced --scan-path /data
```

### Run with Custom Environment Variables
```bash
docker run --rm -v $(pwd):/data \
  -e ELASTIC_APM_ENDPOINT=http://your-elastic:8200 \
  -e INFLUXDB_URL=http://your-influxdb:8086 \
  otel-integrator:latest run --enhanced --scan-path /data
```

### Interactive Mode
```bash
docker run --rm -it -v $(pwd):/data otel-integrator:latest run --enhanced --scan-path /data
```

## Troubleshooting

### Permission Issues
If you encounter permission issues with volume mounting:
```bash
# On macOS/Linux, ensure proper permissions
chmod 755 $(pwd)
```

### Network Access
If the container needs to access network services on the host:
```bash
docker run --rm --network host -v $(pwd):/data otel-integrator:latest run --enhanced --scan-path /data
```

### View Generated Files
```bash
# List generated files
ls -la output/

# View config
cat output/generated-configs/otel-collector-config.yaml

# View environment file
cat output/otel-config.env
```

## Docker Image Details

- **Base Image:** `python:3.11-slim`
- **Size:** ~610MB
- **Entrypoint:** `python main.py`
- **Working Directory:** `/app`

## Integration with Docker Compose

You can also use this tool as part of a larger Docker Compose setup:

```yaml
version: '3.8'
services:
  otel-integrator:
    build: .
    volumes:
      - .:/data
    command: run --enhanced --scan-path /data
```

This Docker image is production-ready and includes all dependencies needed to run the OpenTelemetry Integrator tool. 