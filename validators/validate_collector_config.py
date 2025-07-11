import yaml

def validate_collector_config(path='output/generated-configs/otel-collector-config.yaml'):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    required_keys = ['receivers', 'exporters', 'service']
    missing = [key for key in required_keys if key not in config]
    if missing:
        print(f"❌ Missing required keys: {missing}")
        return False
    if 'pipelines' not in config.get('service', {}):
        print("❌ 'pipelines' missing in service block")
        return False
    print("✅ otel-collector-config.yaml looks valid")
    return True
