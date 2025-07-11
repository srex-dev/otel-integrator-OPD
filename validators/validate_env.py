import os

REQUIRED_VARS = [
    'ELASTIC_APM_ENDPOINT',
    'INFLUXDB_URL',
    'LOKI_URL'
]

def validate_env():
    missing = [var for var in REQUIRED_VARS if var not in os.environ]
    if missing:
        print(f"❌ Missing env vars: {missing}")
        return False
    print("✅ All required env vars are set")
    return True
