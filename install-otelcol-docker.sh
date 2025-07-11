#!/bin/bash

# install-otelcol-docker.sh
#
# This script runs the OpenTelemetry Collector (contrib version) using Docker with the generated config.
#
# Usage:
#   bash install-otelcol-docker.sh
#
# Requirements:
#   - Docker installed
#   - Config file at output/generated-configs/otel-collector-config.yaml

set -e

CONFIG_PATH="$(pwd)/output/generated-configs/otel-collector-config.yaml"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "❌ Config file not found at $CONFIG_PATH. Run: python main.py run"
  exit 1
fi

echo "🐳 Running OpenTelemetry Collector (contrib) in Docker..."
docker run -d \
  --name otel-collector \
  -p 4317:4317 \
  -p 4318:4318 \
  -v "$CONFIG_PATH:/etc/otel/config.yaml" \
  otel/opentelemetry-collector-contrib:latest \
  --config /etc/otel/config.yaml

echo "✅ Collector (contrib) is running in Docker. To see logs:"
echo "  docker logs -f otel-collector" 