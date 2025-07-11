import yaml
import os
from pathlib import Path
from typing import Dict, List, Any

def validate_enhanced_config(path: str = 'output/generated-configs/otel-collector-config.yaml') -> bool:
    """Validate the enhanced OpenTelemetry Collector configuration."""
    print("🔍 Validating enhanced OpenTelemetry Collector configuration...")
    
    # Check if file exists
    if not os.path.exists(path):
        print(f"❌ Config file not found: {path}")
        return False
    
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax: {e}")
        return False
    
    # Required top-level keys
    required_keys = ['receivers', 'exporters', 'service']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        print(f"❌ Missing required keys: {missing_keys}")
        return False
    
    # Validate receivers
    if not config.get('receivers'):
        print("❌ No receivers defined")
        return False
    
    # Validate exporters
    if not config.get('exporters'):
        print("❌ No exporters defined")
        return False
    
    # Validate service and pipelines
    service = config.get('service', {})
    if 'pipelines' not in service:
        print("❌ No pipelines defined in service block")
        return False
    
    pipelines = service['pipelines']
    required_pipelines = ['traces', 'metrics', 'logs']
    missing_pipelines = [p for p in required_pipelines if p not in pipelines]
    if missing_pipelines:
        print(f"⚠️  Missing pipelines: {missing_pipelines}")
    
    # Validate each pipeline
    for pipeline_name, pipeline_config in pipelines.items():
        if not isinstance(pipeline_config, dict):
            print(f"❌ Invalid pipeline config for {pipeline_name}")
            return False
        
        required_pipeline_keys = ['receivers', 'exporters']
        missing_pipeline_keys = [key for key in required_pipeline_keys if key not in pipeline_config]
        if missing_pipeline_keys:
            print(f"❌ Pipeline {pipeline_name} missing keys: {missing_pipeline_keys}")
            return False
        
        # Check that pipeline references exist
        receivers = pipeline_config.get('receivers', [])
        exporters = pipeline_config.get('exporters', [])
        
        for receiver in receivers:
            if receiver not in config.get('receivers', {}):
                print(f"❌ Pipeline {pipeline_name} references unknown receiver: {receiver}")
                return False
        
        for exporter in exporters:
            if exporter not in config.get('exporters', {}):
                print(f"❌ Pipeline {pipeline_name} references unknown exporter: {exporter}")
                return False
    
    # Validate specific exporters for our stack
    expected_exporters = ['otlphttp/elastic', 'otlphttp/grafana', 'otlphttp/influxdb', 'loki']
    available_exporters = list(config.get('exporters', {}).keys())
    
    print(f"✅ Available exporters: {available_exporters}")
    
    # Check for required exporters (at least one should be present)
    found_exporters = [exp for exp in expected_exporters if exp in available_exporters]
    if not found_exporters:
        print("⚠️  No expected exporters found. Config may not work with your backend stack.")
    else:
        print(f"✅ Found expected exporters: {found_exporters}")
    
    print("✅ Enhanced configuration validation passed")
    return True

if __name__ == "__main__":
    validate_enhanced_config() 