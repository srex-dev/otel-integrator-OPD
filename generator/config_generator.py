from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path

TEMPLATE_DIR = Path("templates")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_configs(service_data, output_dir="output/generated-configs"):
    print("⚙️ Generating OTel Collector config...")
    template = env.get_template("otel-collector.j2")
    # Always provide all supported exporters in the context
    exporters = ["elastic", "influxdb", "grafana"]
    output = template.render(services=service_data, exporters=exporters)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    config_path = output_path / "otel-collector-config.yaml"
    
    with open(config_path, "w") as f:
        f.write(output)
    print(f"✅ Config written to {config_path}")
