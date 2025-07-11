import json
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path("templates")

class DashboardGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        
    def generate_overview_dashboard(self, services: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Generate a high-level overview dashboard."""
        dashboard = {
            "dashboard": {
                "title": "OpenTelemetry Overview",
                "description": "High-level overview of all telemetry data",
                "panels": [
                    {
                        "title": "Service Overview",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(service_name)",
                                "legendFormat": "Total Services"
                            }
                        ]
                    },
                    {
                        "title": "Request Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Response Time",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard
    
    def generate_python_dashboard(self, services: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Generate a Python-specific dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Python Services",
                "description": "Python application telemetry",
                "panels": [
                    {
                        "title": "Python Services",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(service_name{service_language=\"python\"})",
                                "legendFormat": "Python Services"
                            }
                        ]
                    },
                    {
                        "title": "Python Request Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{service_language=\"python\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Python Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{service_language=\"python\",status_code=~\"5..\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Python Memory Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "process_resident_memory_bytes{service_language=\"python\"}",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard
    
    def generate_nodejs_dashboard(self, services: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Generate a Node.js-specific dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Node.js Services",
                "description": "Node.js application telemetry",
                "panels": [
                    {
                        "title": "Node.js Services",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(service_name{service_language=\"nodejs\"})",
                                "legendFormat": "Node.js Services"
                            }
                        ]
                    },
                    {
                        "title": "Node.js Request Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{service_language=\"nodejs\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Node.js Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{service_language=\"nodejs\",status_code=~\"5..\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Node.js Event Loop Lag",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "nodejs_eventloop_lag_seconds{service_language=\"nodejs\"}",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard
    
    def generate_java_dashboard(self, services: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Generate a Java-specific dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Java Services",
                "description": "Java application telemetry",
                "panels": [
                    {
                        "title": "Java Services",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(service_name{service_language=\"java\"})",
                                "legendFormat": "Java Services"
                            }
                        ]
                    },
                    {
                        "title": "Java Request Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{service_language=\"java\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Java Heap Memory",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "jvm_memory_used_bytes{area=\"heap\",service_language=\"java\"}",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Java GC Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(jvm_gc_collection_seconds_sum{service_language=\"java\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard
    
    def generate_infrastructure_dashboard(self, services: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Generate an infrastructure dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Infrastructure",
                "description": "Infrastructure and system metrics",
                "panels": [
                    {
                        "title": "Database Connections",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(db_connections_total[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Message Queue Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(message_queue_messages_total[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Web Server Requests",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{job=~\"nginx|apache\"}[5m])",
                                "legendFormat": "{{service_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Docker Containers",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count(container_cpu_usage_seconds_total)",
                                "legendFormat": "Running Containers"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard
    
    def generate_all_dashboards(self, services: Dict[str, List[Any]], output_dir: str = "output/dashboards") -> List[str]:
        """Generate all dashboard files based on discovered services."""
        print("📊 Generating Grafana dashboards...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Always generate overview dashboard
        overview_dashboard = self.generate_overview_dashboard(services)
        overview_file = output_path / "overview-dashboard.json"
        with open(overview_file, "w") as f:
            json.dump(overview_dashboard, f, indent=2)
        generated_files.append(str(overview_file))
        print(f"✅ Generated overview dashboard: {overview_file}")
        
        # Generate language-specific dashboards if services are detected
        if services.get("python"):
            python_dashboard = self.generate_python_dashboard(services)
            python_file = output_path / "python-services-dashboard.json"
            with open(python_file, "w") as f:
                json.dump(python_dashboard, f, indent=2)
            generated_files.append(str(python_file))
            print(f"✅ Generated Python dashboard: {python_file}")
        
        if services.get("node"):
            nodejs_dashboard = self.generate_nodejs_dashboard(services)
            nodejs_file = output_path / "nodejs-services-dashboard.json"
            with open(nodejs_file, "w") as f:
                json.dump(nodejs_dashboard, f, indent=2)
            generated_files.append(str(nodejs_file))
            print(f"✅ Generated Node.js dashboard: {nodejs_file}")
        
        if services.get("java"):
            java_dashboard = self.generate_java_dashboard(services)
            java_file = output_path / "java-services-dashboard.json"
            with open(java_file, "w") as f:
                json.dump(java_dashboard, f, indent=2)
            generated_files.append(str(java_file))
            print(f"✅ Generated Java dashboard: {java_file}")
        
        # Generate infrastructure dashboard if infrastructure services are detected
        infra_services = ["databases", "message_queues", "web_servers", "docker", "kubernetes"]
        if any(services.get(service) for service in infra_services):
            infra_dashboard = self.generate_infrastructure_dashboard(services)
            infra_file = output_path / "infrastructure-dashboard.json"
            with open(infra_file, "w") as f:
                json.dump(infra_dashboard, f, indent=2)
            generated_files.append(str(infra_file))
            print(f"✅ Generated infrastructure dashboard: {infra_file}")
        
        # Generate import instructions
        instructions_file = output_path / "dashboard-import-instructions.md"
        with open(instructions_file, "w") as f:
            f.write(self._generate_import_instructions(generated_files))
        generated_files.append(str(instructions_file))
        print(f"✅ Generated import instructions: {instructions_file}")
        
        return generated_files
    
    def _generate_import_instructions(self, dashboard_files: List[str]) -> str:
        """Generate instructions for importing dashboards into Grafana."""
        instructions = """# Grafana Dashboard Import Instructions

## Quick Import

1. **Open Grafana** in your browser (usually http://localhost:3000)

2. **Navigate to Dashboards** → **Import**

3. **Import each dashboard file:**

"""
        
        for dashboard_file in dashboard_files:
            if dashboard_file.endswith('.json'):
                dashboard_name = Path(dashboard_file).stem.replace('-', ' ').title()
                instructions += f"### {dashboard_name}\n"
                instructions += f"1. Click **Upload JSON file**\n"
                instructions += f"2. Select: `{dashboard_file}`\n"
                instructions += f"3. Click **Import**\n\n"
        
        instructions += """## Manual Import

If you prefer to copy-paste:

1. Open each `.json` file in a text editor
2. Copy the entire JSON content
3. In Grafana, go to **Dashboards** → **Import**
4. Paste the JSON into the **Import via panel json** field
5. Click **Import**

## Dashboard Features

- **Overview Dashboard**: High-level metrics across all services
- **Language-Specific Dashboards**: Detailed metrics for Python, Node.js, Java services
- **Infrastructure Dashboard**: Database, message queue, and system metrics

## Customization

After importing, you can:
- Modify panel queries to match your specific metrics
- Add new panels for custom metrics
- Adjust time ranges and refresh intervals
- Set up alerts based on dashboard metrics

## Troubleshooting

- **No data showing?** Check that your services are instrumented and sending telemetry
- **Missing metrics?** Verify that the metric names match your actual telemetry
- **Import errors?** Ensure the JSON files are valid and complete
"""
        
        return instructions 