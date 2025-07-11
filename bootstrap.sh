#!/bin/bash

echo "🚀 Bootstrapping otel-integrator..."

# Install Python and Git if needed (Debian/Ubuntu)
if ! command -v python3 &>/dev/null; then
  echo "⚙️ Installing Python3..."
  sudo apt update && sudo apt install -y python3 python3-pip
fi

if ! command -v git &>/dev/null; then
  echo "⚙️ Installing Git..."
  sudo apt install -y git
fi

# Clone and install
git clone https://github.com/your-org/otel-integrator.git
cd otel-integrator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "✅ Ready to run:"
echo "  python main.py run"
