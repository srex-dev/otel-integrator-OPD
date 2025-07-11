# OpenTelemetry Integrator Installation Guide

## Prerequisites

### 1. Download OpenTelemetry Collector Binary

The OpenTelemetry Collector binary is required for telemetry processing. Download the appropriate version for your platform:

#### macOS (Intel)
```bash
curl -L -o otelcol.tar.gz https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.96.0/otelcol_0.96.0_darwin_amd64.tar.gz
tar -xzf otelcol.tar.gz
chmod +x otelcol
```

#### macOS (Apple Silicon)
```bash
curl -L -o otelcol.tar.gz https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.96.0/otelcol_0.96.0_darwin_arm64.tar.gz
tar -xzf otelcol.tar.gz
chmod +x otelcol
```

#### Linux
```bash
curl -L -o otelcol.tar.gz https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.96.0/otelcol_0.96.0_linux_amd64.tar.gz
tar -xzf otelcol.tar.gz
chmod +x otelcol
```

#### Windows
```bash
# Using PowerShell
Invoke-WebRequest -Uri "https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.96.0/otelcol_0.96.0_windows_amd64.tar.gz" -OutFile "otelcol.tar.gz"
tar -xzf otelcol.tar.gz
```

#### Docker (Alternative)
If you prefer to use Docker instead of downloading the binary:
```bash
docker pull otel/opentelemetry-collector-contrib:latest
```

### 2. Python Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Tool in Enhanced Mode
```bash
python main.py run --enhanced
```
- This generates:
  - `output/generated-configs/otel-collector-config.yaml` (collector config)
  - `output/otel-config.env` (environment variables for exporters)

### 4. Edit the `.env` File
```bash
nano output/otel-config.env
# Fill in your exporter credentials:
#   ELASTIC_APM_ENDPOINT, ELASTIC_APM_SECRET_TOKEN
#   INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
#   LOKI_URL, LOKI_USERNAME, LOKI_PASSWORD, LOKI_ORG_ID
#   GRAFANA_CLOUD_OTLP_ENDPOINT, GRAFANA_CLOUD_API_KEY
```

### 5. Start the Collector
```bash
source output/otel-config.env
./otelcol --config output/generated-configs/otel-collector-config.yaml
```

### 6. Check Health and Instrumentation
```bash
python main.py check-backends
python main.py check-instrumentation
```

---

## 🐳 Docker / Docker Compose

If you're running the full stack locally:
```bash
docker-compose up -d
```
- This starts Grafana, Loki, Elastic APM Server, and optionally InfluxDB
- The collector will read config from `output/generated-configs/otel-collector-config.yaml`
- Pass your environment variables to the collector container as needed

---

## 🔁 CI/CD Automation (One-Time Config)

### 1. Add to CI Pipeline
```bash
pip install -r requirements.txt
python main.py run --enhanced
```

### 2. Export Generated Config
```bash
cp output/generated-configs/otel-collector-config.yaml /etc/otel/config.yaml
cp output/otel-config.env /etc/otel/otel-config.env
```

- Optionally store in Git, S3, Vault, or another delivery mechanism

---

## ☁️ Baremetal or VM Installation

### 1. Install Python and Git
```bash
sudo apt update && sudo apt install python3-pip git -y
```

### 2. Bootstrap Script *(optional)*
```bash
curl -sSL https://your-url/bootstrap.sh | bash
```

*(Create this script to install Python + clone repo + run the app)*

---

## ⚠️ Prerequisites
- Python 3.8+
- Docker (optional)
- InfluxDB, Loki, Elastic APM, and Grafana accessible from this machine
- OTLP-compatible apps or OpenTelemetry SDKs emitting to collector

---

## ✅ What’s Next?
- Check output in Grafana, Elastic, InfluxDB, Loki
- Save or deploy generated config to your OTel Collector service
- Delete the tool when finished — it does not persist in memory

---

## 🧼 Cleanup
```bash
deactivate
rm -rf .venv
rm -rf output/generated-configs
```

---

For questions or updates, visit: https://github.com/your-org/otel-integrator
