# OpenTelemetry Integrator

A Python tool for service discovery, configuration generation, validation, and telemetry simulation for OpenTelemetry Collector.

## 🚀 Quick Start

1. **Download OpenTelemetry Collector Binary:**
   ```bash
   # macOS (Intel)
   curl -L -o otelcol.tar.gz https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.96.0/otelcol_0.96.0_darwin_amd64.tar.gz
   tar -xzf otelcol.tar.gz
   chmod +x otelcol
   ```

2. **Install and Run:**
   ```bash
   pip install -r requirements.txt
   python main.py run --enhanced
   ```

3. **Import Dashboards:**
   - Open Grafana at http://localhost:3000
   - Import dashboards from `output/dashboards/`

## 📦 Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions across different platforms and environments.

## Components

The full list of components is available in the [manifest](manifest.yaml)

## Version Summary

| Component         | Version Pin/Tag         | Where Set/Documented         |
|-------------------|------------------------|------------------------------|
| OTEL Collector    | 0.96.0                 | install scripts, README      |
| Elastic APM       | 8.11.0                 | docker-compose, README       |
| InfluxDB          | 2.7.5                  | docker-compose, README       |
| Grafana           | 10.2.0                 | docker-compose, README       |

## Sample Files

- See `output/otel-config.env` for a sample environment file (Elastic is the only log backend)
- See `output/generated-configs/otel-collector-config.yaml` for a sample collector config (logs → Elastic)

## Troubleshooting

- **No logs in Elastic?**
  - Run health checks: `python main.py check-backends`
  - Check Elastic exporter endpoints and credentials in `.env`
  - Check the logs pipeline in the collector config
- **No data in backends?**
  - Run health checks: `python main.py check-backends`
  - Check exporter endpoints and credentials in `.env`
- **TLS/SSL errors?**
  - Run: `python main.py check-tls`
  - Check CA certs and endpoint URLs
- **Instrumentation missing?**
  - Run: `python main.py check-instrumentation`
  - Follow recommendations for each service
- **Pipeline failed in CI?**
  - Download artifacts and review logs in the GitHub Actions UI

## 🚀 Automatic SDK Installation

You can automatically install the required OpenTelemetry SDKs for detected Python, Node.js, and Java projects using the following command:

```bash
python main.py install-sdks --scan-path <your_project_root>
```
- Installs Python SDK system-wide if Python services are detected.
- Installs Node.js SDK in each detected Node.js project directory.
- Downloads the latest OpenTelemetry Java agent JAR into each detected Java project directory.
- Silent, no prompts. Custom project paths supported via --scan-path.

### Docker Example

You can run the same command inside Docker:

```bash
docker run --rm -v $(pwd):/data otel-integrator:latest install-sdks --scan-path /data
```

This will install SDKs in your mounted project directories as needed.

## Release Notes

See `release-notes.md`