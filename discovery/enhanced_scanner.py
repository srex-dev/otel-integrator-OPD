import os
import psutil
import socket
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

class EnhancedServiceScanner:
    def __init__(self, extra_processes: Optional[List[str]] = None, extra_ports: Optional[List[int]] = None):
        self.services = {
            "python": [],
            "node": [],
            "java": [],
            "go": [],
            "dotnet": [],
            "ruby": [],
            "php": [],
            "databases": [],
            "message_queues": [],
            "web_servers": [],
            "docker": [],
            "kubernetes": [],
            "logs": [],
            "ports": [],
            "cloud": [],
            "service_mesh": [],
            "custom": []
        }
        self.extra_processes = extra_processes or []
        self.extra_ports = extra_ports or []

    def scan_processes(self):
        print("🔍 Scanning running processes...")
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
            try:
                cmd = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                name = proc.info['name'].lower()
                exe = proc.info['exe']
                # Standard detections (as before)...
                if any(x in cmd.lower() for x in ["python", "pip", "django", "flask", "fastapi"]):
                    self.services["python"].append(proc.info)
                elif any(x in cmd.lower() for x in ["node", "npm", "yarn", "express", "react"]):
                    self.services["node"].append(proc.info)
                elif any(x in name for x in ["java", "jar"]) or "spring" in cmd.lower():
                    self.services["java"].append(proc.info)
                elif name.endswith(".go") or "go" in cmd.lower():
                    self.services["go"].append(proc.info)
                elif any(x in name for x in [".exe", ".dll"]) or "dotnet" in cmd.lower():
                    self.services["dotnet"].append(proc.info)
                elif any(x in cmd.lower() for x in ["ruby", "rails", "rake"]):
                    self.services["ruby"].append(proc.info)
                elif any(x in cmd.lower() for x in ["php", "apache", "nginx"]):
                    self.services["php"].append(proc.info)
                elif any(x in name for x in ["postgres", "mysql", "redis", "mongodb", "sqlite"]):
                    self.services["databases"].append(proc.info)
                elif any(x in name for x in ["rabbitmq", "kafka", "activemq"]):
                    self.services["message_queues"].append(proc.info)
                elif any(x in name for x in ["nginx", "apache", "httpd"]):
                    self.services["web_servers"].append(proc.info)
                elif "docker" in cmd.lower():
                    self.services["docker"].append(proc.info)
                # Service mesh detection
                elif any(x in name for x in ["istio-proxy", "linkerd2-proxy", "envoy", "consul"]):
                    self.services["service_mesh"].append(proc.info)
                # Custom/extra process detection
                elif any(x in cmd.lower() for x in self.extra_processes):
                    self.services["custom"].append(proc.info)
            except Exception:
                continue

    def scan_ports(self):
        print("🔍 Scanning listening ports...")
        common_ports = {
            80: "http",
            443: "https", 
            8080: "http-alt",
            3000: "node-app",
            5000: "python-app",
            5432: "postgresql",
            3306: "mysql",
            6379: "redis",
            27017: "mongodb",
            5672: "rabbitmq",
            9092: "kafka",
            9200: "elasticsearch",
            5601: "kibana",
            3001: "grafana",
            9090: "prometheus",
            4317: "otlp-grpc",
            4318: "otlp-http",
            15001: "istio-proxy",
            4143: "linkerd-proxy"
        }
        # Add user-specified extra ports
        for p in self.extra_ports:
            common_ports[p] = f"custom-{p}"
        for port, service_type in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    self.services["ports"].append({
                        "port": port,
                        "service": service_type,
                        "status": "listening"
                    })
            except:
                continue

    def scan_cloud(self):
        print("🔍 Scanning for cloud environment...")
        # AWS
        if os.environ.get("AWS_EXECUTION_ENV") or os.path.exists("/sys/hypervisor/uuid"):
            self.services["cloud"].append({"provider": "aws", "details": os.environ.get("AWS_EXECUTION_ENV", "ec2/ecs/lambda?")})
        try:
            r = requests.get("http://169.254.169.254/latest/meta-data/", timeout=1)
            if r.status_code == 200:
                self.services["cloud"].append({"provider": "aws", "details": "ec2-metadata"})
        except:
            pass
        # GCP
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            self.services["cloud"].append({"provider": "gcp", "details": os.environ["GOOGLE_CLOUD_PROJECT"]})
        try:
            r = requests.get("http://metadata.google.internal/computeMetadata/v1/", headers={"Metadata-Flavor": "Google"}, timeout=1)
            if r.status_code == 200:
                self.services["cloud"].append({"provider": "gcp", "details": "gce-metadata"})
        except:
            pass
        # Azure
        if os.environ.get("AZURE_HTTP_USER_AGENT"):
            self.services["cloud"].append({"provider": "azure", "details": os.environ["AZURE_HTTP_USER_AGENT"]})
        try:
            r = requests.get("http://169.254.169.254/metadata/instance?api-version=2021-02-01", headers={"Metadata": "true"}, timeout=1)
            if r.status_code == 200:
                self.services["cloud"].append({"provider": "azure", "details": "vm-metadata"})
        except:
            pass

    def scan_docker_compose(self, scan_path: str = "."):
        print("🔍 Scanning for Docker Compose files...")
        compose_files = ["docker-compose.yml", "docker-compose.yaml", "compose.yml"]
        for compose_file in compose_files:
            file_path = Path(scan_path) / compose_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        compose_config = yaml.safe_load(f)
                    if 'services' in compose_config:
                        for service_name, service_config in compose_config['services'].items():
                            self.services["docker"].append({
                                "name": service_name,
                                "image": service_config.get('image', 'unknown'),
                                "ports": service_config.get('ports', []),
                                "environment": service_config.get('environment', {}),
                                "source": "docker-compose"
                            })
                except Exception as e:
                    print(f"⚠️  Error parsing {compose_file}: {e}")
    def scan_kubernetes(self, scan_path: str = "."):
        print("🔍 Scanning for Kubernetes manifests...")
        k8s_extensions = ['.yaml', '.yml']
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if any(file.endswith(ext) for ext in k8s_extensions):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r') as f:
                            k8s_config = yaml.safe_load(f)
                        if k8s_config and 'kind' in k8s_config:
                            self.services["kubernetes"].append({
                                "kind": k8s_config['kind'],
                                "name": k8s_config.get('metadata', {}).get('name', 'unknown'),
                                "file": str(file_path)
                            })
                    except Exception:
                        continue
    def scan_logs(self, scan_path: str = "."):
        print("🔍 Scanning for log files...")
        log_extensions = ['.log', '.out', '.err', '.access', '.error']
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if any(file.endswith(ext) for ext in log_extensions):
                    log_path = os.path.join(root, file)
                    self.services["logs"].append(log_path)
    def detect_services(self, scan_path: str = ".") -> Dict[str, List[Any]]:
        print("🚀 Starting enhanced service discovery...")
        self.scan_processes()
        self.scan_ports()
        self.scan_cloud()
        self.scan_docker_compose(scan_path)
        self.scan_kubernetes(scan_path)
        self.scan_logs(scan_path)
        # Always return all keys, even if empty
        return {k: self.services.get(k, []) for k in [
            "python", "node", "java", "go", "dotnet", "ruby", "php", "databases", "message_queues", "web_servers", "docker", "kubernetes", "logs", "ports", "cloud", "service_mesh", "custom"
        ]} 