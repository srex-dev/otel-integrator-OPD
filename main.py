import os
from pathlib import Path
from typing import List
import typer
from discovery.scanner import detect_services
from generator.config_generator import generate_configs
from installer.collector_installer import CollectorInstaller
from discovery.enhanced_scanner import EnhancedServiceScanner
from jinja2 import Environment, FileSystemLoader
from validators.validate_enhanced_config import validate_enhanced_config
from validators.health_check import run_full_health_check
from validators.exporter_health_check import ExporterHealthChecker
from validators.instrumentation_check import InstrumentationChecker
from validators.tls_validator import TLSValidator
from validators.resilience_manager import ResilienceManager
from generator.env_generator import generate_all_env_outputs
from generator.dashboard_generator import DashboardGenerator
from installer.sdk_installer import SDKInstaller

app = typer.Typer()

BASE_OUTPUT_DIR = Path("output/generated-configs")
TEMPLATE_DIR = Path("templates")

ENHANCED_EXPORTERS = ["grafana", "influxdb", "loki", "elastic"]

@app.command()
def run(scan_path: str = ".", output_dir: str = str(BASE_OUTPUT_DIR), install: bool = False, enhanced: bool = False):
    """
    Run discovery and generate OTel + Grafana Agent config files.
    Use --enhanced for comprehensive service discovery and config.
    """
    if enhanced:
        typer.echo("🚀 Using enhanced service discovery...")
        scanner = EnhancedServiceScanner()
        services = scanner.detect_services(scan_path)
        typer.echo(f"✅ Enhanced detected services: {services}")
        
        # Use comprehensive template with fixed exporters
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("comprehensive-otel-collector.j2")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        config_path = output_path / "otel-collector-config.yaml"
        
        with open(config_path, "w") as f:
            f.write(template.render(services=services, exporters=ENHANCED_EXPORTERS))
        typer.echo(f"✅ Comprehensive configuration written to: {config_path}")
        
        # Validate the enhanced config
        if validate_enhanced_config(str(config_path)):
            typer.echo("✅ Enhanced configuration validation passed")
        else:
            typer.echo("❌ Enhanced configuration validation failed")
            return
        
        # Generate environment files
        env_outputs = generate_all_env_outputs(services, "output")
        typer.echo(f"✅ Environment files generated:")
        typer.echo(f"   - {env_outputs['env_file']}")
        typer.echo(f"   - {env_outputs['instructions_file']}")
        
        # Generate dashboards
        typer.echo("\n📊 Generating dashboards...")
        dashboard_generator = DashboardGenerator()
        dashboard_files = dashboard_generator.generate_all_dashboards(services, "output/dashboards")
        typer.echo(f"✅ Generated {len(dashboard_files)} dashboard files")
        
        # Check backend services health
        typer.echo("\n🏥 Checking backend services...")
        backend_checker = ExporterHealthChecker()
        backend_results = backend_checker.check_all_backends()
        
        # Check instrumentation
        typer.echo("\n🔧 Checking instrumentation...")
        instrumentation_checker = InstrumentationChecker()
        instrumentation_results = instrumentation_checker.check_all_services(services)
        
        # Show recommendations
        typer.echo("\n💡 Recommendations:")
        backend_recs = backend_checker.get_recommendations(backend_results)
        for rec in backend_recs:
            typer.echo(f"   • {rec}")
        
        for service_name, result in instrumentation_results.items():
            if result["status"] != "instrumented":
                typer.echo(f"\n📦 {service_name} instrumentation:")
                for rec in result["recommendations"]:
                    typer.echo(f"   • {rec}")
        
    else:
        typer.echo("🔍 Starting discovery...")
        services = detect_services(scan_path)
        typer.echo(f"✅ Detected services: {services}")
        typer.echo("🛠️ Generating configuration files...")
        os.makedirs(output_dir, exist_ok=True)
        generate_configs(services, output_dir)
        typer.echo(f"✅ Configuration files written to: {output_dir}")
    
    if install:
        config_path = Path(output_dir) / "otel-collector-config.yaml"
        if config_path.exists():
            typer.echo("🚀 Installing and starting OpenTelemetry Collector...")
            installer = CollectorInstaller()
            try:
                installer.install_and_start(str(config_path))
                typer.echo("✅ OpenTelemetry Collector installed and running!")
                
                # Run health check
                typer.echo("🏥 Running health check...")
                if run_full_health_check():
                    typer.echo("✅ Health check passed - collector is working correctly!")
                else:
                    typer.echo("⚠️  Health check had issues - check collector logs")
                    
            except Exception as e:
                typer.echo(f"❌ Failed to install collector: {e}")
        else:
            typer.echo("❌ Configuration file not found. Run without --install first.")

@app.command()
def install(output_dir: str = str(BASE_OUTPUT_DIR)):
    """
    Install and start the OpenTelemetry Collector with the generated config.
    """
    config_path = Path(output_dir) / "otel-collector-config.yaml"
    if not config_path.exists():
        typer.echo("❌ Configuration file not found. Run 'python main.py run' first.")
        return
    
    typer.echo("🚀 Installing and starting OpenTelemetry Collector...")
    installer = CollectorInstaller()
    try:
        installer.install_and_start(str(config_path))
        typer.echo("✅ OpenTelemetry Collector installed and running!")
        
        # Run health check
        typer.echo("🏥 Running health check...")
        if run_full_health_check():
            typer.echo("✅ Health check passed - collector is working correctly!")
        else:
            typer.echo("⚠️  Health check had issues - check collector logs")
            
    except Exception as e:
        typer.echo(f"❌ Failed to install collector: {e}")

@app.command()
def validate(output_dir: str = str(BASE_OUTPUT_DIR)):
    """
    Validate the generated OpenTelemetry Collector configuration.
    """
    config_path = Path(output_dir) / "otel-collector-config.yaml"
    if not config_path.exists():
        typer.echo("❌ Configuration file not found. Run 'python main.py run' first.")
        return
    
    if validate_enhanced_config(str(config_path)):
        typer.echo("✅ Configuration validation passed")
    else:
        typer.echo("❌ Configuration validation failed")

@app.command()
def health_check():
    """
    Run health check on the OpenTelemetry Collector.
    """
    typer.echo("🏥 Running health check...")
    if run_full_health_check():
        typer.echo("✅ Health check passed - collector is working correctly!")
    else:
        typer.echo("❌ Health check failed - collector may have issues")

@app.command()
def check_backends():
    """
    Check health of backend services (Elastic APM, Loki, InfluxDB, Grafana).
    """
    typer.echo("🏥 Checking backend services...")
    checker = ExporterHealthChecker()
    results = checker.check_all_backends()
    
    recommendations = checker.get_recommendations(results)
    typer.echo("\n💡 Recommendations:")
    for rec in recommendations:
        typer.echo(f"   • {rec}")

@app.command()
def check_instrumentation(scan_path: str = "."):
    """
    Check OpenTelemetry instrumentation for discovered services.
    """
    typer.echo("🔧 Checking instrumentation...")
    
    # Use enhanced scanner to discover services
    scanner = EnhancedServiceScanner()
    services = scanner.detect_services(scan_path)
    
    if not services:
        typer.echo("❌ No services discovered")
        return
    
    checker = InstrumentationChecker()
    results = checker.check_all_services(services)
    
    # Show recommendations for each service
    typer.echo("\n💡 Instrumentation Recommendations:")
    for service_name, result in results.items():
        if result["status"] != "instrumented":
            typer.echo(f"\n📦 {service_name}:")
            for rec in result["recommendations"]:
                typer.echo(f"   • {rec}")

@app.command()
def check_tls():
    """
    Check TLS certificate validity for exporter endpoints.
    """
    typer.echo("🔒 Checking TLS certificates...")
    
    # Get exporter endpoints from environment
    exporters = {
        "elastic": os.environ.get("ELASTIC_APM_ENDPOINT", "http://localhost:8200"),
        "loki": os.environ.get("LOKI_URL", "http://localhost:3100"),
        "influxdb": os.environ.get("INFLUXDB_URL", "http://localhost:8086"),
        "grafana": os.environ.get("GRAFANA_CLOUD_OTLP_ENDPOINT", "https://otlp-gateway-prod-us-central-0.grafana.net/otlp")
    }
    
    tls_validator = TLSValidator()
    
    # Check if custom CA cert is provided
    ca_cert = os.environ.get("CA_CERT_PATH")
    if ca_cert:
        tls_validator.set_ca_cert(ca_cert)
    
    # Check if client certs are provided
    client_cert = os.environ.get("CLIENT_CERT_PATH")
    client_key = os.environ.get("CLIENT_KEY_PATH")
    if client_cert and client_key:
        tls_validator.set_client_certs(client_cert, client_key)
    
    # Check if SSL verification should be disabled (dev mode)
    if os.environ.get("DISABLE_SSL_VERIFICATION", "").lower() == "true":
        tls_validator.disable_ssl_verification()
    
    results = tls_validator.validate_exporters_tls(exporters)
    
    # Show recommendations
    typer.echo("\n💡 TLS Recommendations:")
    for exporter_name, result in results.items():
        if result["status"] != "healthy":
            typer.echo(f"\n🔒 {exporter_name}:")
            typer.echo(f"   • {result.get('recommendation', 'Check endpoint configuration')}")

@app.command()
def check_resilience():
    """
    Check resilience status of monitored services.
    """
    typer.echo("🛡️ Checking resilience status...")
    
    resilience_manager = ResilienceManager()
    health_status = resilience_manager.get_all_health_status()
    
    if not health_status:
        typer.echo("ℹ️  No services being monitored for resilience")
        return
    
    typer.echo("\n📊 Resilience Status:")
    for service_name, status in health_status.items():
        status_icon = "✅" if status["status"] == "closed" else "⚠️" if status["status"] == "half_open" else "❌"
        typer.echo(f"   {status_icon} {service_name}: {status['status']}")
        if status["failure_count"] > 0:
            typer.echo(f"      Failures: {status['failure_count']}")
    
    # Show reset option
    typer.echo("\n💡 To reset a circuit breaker:")
    typer.echo("   python main.py reset-circuit-breaker <service_name>")

@app.command()
def reset_circuit_breaker(service_name: str):
    """
    Reset circuit breaker for a specific service.
    """
    typer.echo(f"🔄 Resetting circuit breaker for {service_name}...")
    
    resilience_manager = ResilienceManager()
    resilience_manager.reset_circuit_breaker(service_name)

@app.command()
def generate_dashboards(scan_path: str = ".", output_dir: str = "output/dashboards"):
    """
    Generate Grafana dashboards based on discovered services.
    """
    typer.echo("📊 Generating dashboards...")
    
    # Use enhanced scanner to discover services
    scanner = EnhancedServiceScanner()
    services = scanner.detect_services(scan_path)
    
    if not services:
        typer.echo("❌ No services discovered")
        return
    
    # Generate dashboards
    dashboard_generator = DashboardGenerator()
    generated_files = dashboard_generator.generate_all_dashboards(services, output_dir)
    
    typer.echo(f"\n✅ Generated {len(generated_files)} dashboard files:")
    for file_path in generated_files:
        typer.echo(f"   - {file_path}")
    
    typer.echo(f"\n📋 Next steps:")
    typer.echo(f"   1. Open Grafana at http://localhost:3000")
    typer.echo(f"   2. Go to Dashboards → Import")
    typer.echo(f"   3. Import each .json file from {output_dir}")
    typer.echo(f"   4. See {output_dir}/dashboard-import-instructions.md for detailed instructions")

@app.command()
def install_sdks(scan_path: str = "."):
    """
    Automatically install OpenTelemetry SDKs for detected Python, Node.js, and Java projects.
    Installs system-wide (Python) and in each project directory (Node.js, Java). Silent, no prompts.
    """
    typer.echo("🔎 Discovering services for SDK installation...")
    scanner = EnhancedServiceScanner()
    services = scanner.detect_services(scan_path)
    installer = SDKInstaller(services)
    installer.install_all()
    typer.echo("\n✅ SDK installation complete.")

if __name__ == "__main__":
    app()