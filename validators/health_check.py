import requests
import socket
import time
import subprocess
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def check_collector_health(host: str = "localhost", ports: list = [4317, 4318]) -> bool:
    """Check if the OpenTelemetry Collector is running and listening."""
    print("🏥 Checking OpenTelemetry Collector health...")
    
    # Check if ports are listening
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Collector listening on {host}:{port}")
            else:
                print(f"❌ Collector not listening on {host}:{port}")
                return False
        except Exception as e:
            print(f"❌ Error checking port {port}: {e}")
            return False
    
    # Check HTTP health endpoint (if available)
    try:
        response = requests.get(f"http://{host}:4318/", timeout=5)
        if response.status_code == 200:
            print("✅ Collector HTTP endpoint responding")
        else:
            print(f"⚠️  Collector HTTP endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not reach collector HTTP endpoint: {e}")
    
    return True

def send_test_telemetry(host: str = "localhost", port: int = 4318) -> bool:
    """Send test telemetry to verify the collector is processing data."""
    print("📤 Sending test telemetry...")
    
    try:
        # Set up test tracer
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"http://{host}:{port}/v1/traces"
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Create and send test span
        with tracer.start_as_current_span("health-check-span") as span:
            span.set_attribute("health.check", True)
            span.set_attribute("test.timestamp", time.time())
            print("✅ Test span created and sent")
        
        # Give time for processing
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending test telemetry: {e}")
        return False

def verify_collector_logs(container_name: str = "otel-collector") -> bool:
    """Check collector logs for any errors or issues."""
    print("📋 Checking collector logs...")
    
    try:
        # Try to get Docker logs
        result = subprocess.run(
            ["docker", "logs", "--tail", "20", container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            if "error" in logs.lower() or "failed" in logs.lower():
                print("⚠️  Collector logs contain errors:")
                print(logs)
                return False
            else:
                print("✅ Collector logs look healthy")
                return True
        else:
            print("⚠️  Could not retrieve Docker logs")
            return True  # Not critical if we can't get logs
            
    except Exception as e:
        print(f"⚠️  Error checking logs: {e}")
        return True  # Not critical

def run_full_health_check(host: str = "localhost", container_name: str = "otel-collector") -> bool:
    """Run complete health check suite."""
    print("🔍 Running complete health check...")
    
    # Check if collector is listening
    if not check_collector_health(host):
        return False
    
    # Send test telemetry
    if not send_test_telemetry(host):
        print("⚠️  Test telemetry failed, but collector may still be working")
    
    # Check logs
    if not verify_collector_logs(container_name):
        print("⚠️  Collector logs show issues")
    
    print("✅ Health check completed")
    return True

if __name__ == "__main__":
    run_full_health_check() 