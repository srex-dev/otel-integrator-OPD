# OpenTelemetry Collector Installation Options

This project generates a config for the OpenTelemetry Collector, but does not install the collector binary automatically. You can use either the provided installer script or Docker. See below for both options.

---

## Option 1: Using the Installer Script (Recommended for Development)

1. **Ensure you have generated a config:**
   ```sh
   python main.py run
   ```
   This will create `output/generated-configs/otel-collector-config.yaml`.

2. **Run the install script:**
   ```sh
   bash install-otelcol.sh
   ```
   This will:
   - Download the OpenTelemetry Collector binary
   - Extract it
   - Run it with your generated config

3. **(Optional) Make the collector available system-wide:**
   Uncomment the lines at the end of `install-otelcol.sh` to move the binary to `/usr/local/bin`.

---

## Option 2: Using Docker (Recommended for Production)

1. **Ensure you have generated a config:**
   ```sh
   python main.py run
   ```
   This will create `output/generated-configs/otel-collector-config.yaml`.

2. **Run the Docker install script:**
   ```sh
   bash install-otelcol-docker.sh
   ```
   This will:
   - Pull the latest OpenTelemetry Collector Docker image
   - Mount your generated config
   - Expose ports 4317 (gRPC) and 4318 (HTTP)

3. **View logs:**
   ```sh
   docker logs -f otel-collector
   ```

4. **Stop the collector:**
   ```sh
   docker stop otel-collector && docker rm otel-collector
   ```

---

## Troubleshooting
- Make sure you have `curl`, `tar`, and `chmod` installed for the installer script.
- Make sure you have Docker installed for the Docker script.
- The config file must exist at `output/generated-configs/otel-collector-config.yaml`.
- For other platforms, adjust the download URL or Docker image accordingly.

---

For more details, see the official [OpenTelemetry Collector releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases). 