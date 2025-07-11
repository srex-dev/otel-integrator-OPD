#!/bin/bash

# install-otelcol.sh
#
# This script downloads, extracts, and runs the OpenTelemetry Collector using the generated config.
#
# Usage:
#   bash install-otelcol.sh
#
# Optional: Move the otelcol binary to /usr/local/bin for global use.
#
# Requirements:
#   - curl, tar, chmod
#   - Config file at output/generated-configs/otel-collector-config.yaml

OTELCOL_VERSION="0.96.0"
PLATFORM="darwin_amd64"
BINARY_NAME="otelcol"
TARBALL="otelcol_${OTELCOL_VERSION}_${PLATFORM}.tar.gz"
DOWNLOAD_URL="https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${OTELCOL_VERSION}/${TARBALL}"

set -e

echo "📥 Downloading OpenTelemetry Collector..."
curl -LO "$DOWNLOAD_URL"

echo "📦 Extracting..."
tar -xzf "$TARBALL"

chmod +x "$BINARY_NAME"

echo "🚀 Running OpenTelemetry Collector with generated config..."
./otelcol --config output/generated-configs/otel-collector-config.yaml

# Uncomment the following lines to move the binary to /usr/local/bin for global use:
# echo "🔧 Moving otelcol to /usr/local/bin (requires sudo)"
# sudo mv otelcol /usr/local/bin/
# echo "✅ otelcol is now available system-wide. Run with: otelcol --config output/generated-configs/otel-collector-config.yaml" 