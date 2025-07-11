import requests
import time
from typing import Dict, List, Any

class ExporterHealthChecker:
    def __init__(self):
        self.backend_endpoints = {
            "elastic": "http://localhost:8200",
            "loki": "http://localhost:3100",
            "influxdb": "http://localhost:8086",
            "grafana": "http://localhost:3000"
        }
        self.timeout = 5

    def check_elastic_apm(self) -> Dict[str, Any]:
        """Check Elastic APM endpoint health."""
        print("🔍 Checking Elastic APM...")
        try:
            # Check if APM server is running
            response = requests.get(f"{self.backend_endpoints['elastic']}/", timeout=self.timeout)
            if response.status_code == 200:
                print("✅ Elastic APM server is responding")
                return {"status": "healthy", "endpoint": self.backend_endpoints['elastic']}
            else:
                print(f"⚠️  Elastic APM returned status {response.status_code}")
                return {"status": "warning", "endpoint": self.backend_endpoints['elastic'], "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            print("❌ Elastic APM server is not reachable")
            return {"status": "unhealthy", "endpoint": self.backend_endpoints['elastic'], "error": "connection refused"}
        except Exception as e:
            print(f"❌ Error checking Elastic APM: {e}")
            return {"status": "error", "endpoint": self.backend_endpoints['elastic'], "error": str(e)}

    def check_loki(self) -> Dict[str, Any]:
        """Check Loki endpoint health."""
        print("🔍 Checking Loki...")
        try:
            # Check Loki ready endpoint
            response = requests.get(f"{self.backend_endpoints['loki']}/ready", timeout=self.timeout)
            if response.status_code == 200:
                print("✅ Loki is ready")
                return {"status": "healthy", "endpoint": self.backend_endpoints['loki']}
            else:
                print(f"⚠️  Loki returned status {response.status_code}")
                return {"status": "warning", "endpoint": self.backend_endpoints['loki'], "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            print("❌ Loki is not reachable")
            return {"status": "unhealthy", "endpoint": self.backend_endpoints['loki'], "error": "connection refused"}
        except Exception as e:
            print(f"❌ Error checking Loki: {e}")
            return {"status": "error", "endpoint": self.backend_endpoints['loki'], "error": str(e)}

    def check_influxdb(self) -> Dict[str, Any]:
        """Check InfluxDB endpoint health."""
        print("🔍 Checking InfluxDB...")
        try:
            # Check InfluxDB ping endpoint
            response = requests.get(f"{self.backend_endpoints['influxdb']}/ping", timeout=self.timeout)
            if response.status_code == 204:  # InfluxDB returns 204 for ping
                print("✅ InfluxDB is responding")
                return {"status": "healthy", "endpoint": self.backend_endpoints['influxdb']}
            else:
                print(f"⚠️  InfluxDB returned status {response.status_code}")
                return {"status": "warning", "endpoint": self.backend_endpoints['influxdb'], "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            print("❌ InfluxDB is not reachable")
            return {"status": "unhealthy", "endpoint": self.backend_endpoints['influxdb'], "error": "connection refused"}
        except Exception as e:
            print(f"❌ Error checking InfluxDB: {e}")
            return {"status": "error", "endpoint": self.backend_endpoints['influxdb'], "error": str(e)}

    def check_grafana(self) -> Dict[str, Any]:
        """Check Grafana endpoint health."""
        print("🔍 Checking Grafana...")
        try:
            # Check Grafana health endpoint
            response = requests.get(f"{self.backend_endpoints['grafana']}/api/health", timeout=self.timeout)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("database") == "ok":
                    print("✅ Grafana is healthy")
                    return {"status": "healthy", "endpoint": self.backend_endpoints['grafana']}
                else:
                    print(f"⚠️  Grafana database status: {health_data.get('database')}")
                    return {"status": "warning", "endpoint": self.backend_endpoints['grafana'], "database": health_data.get('database')}
            else:
                print(f"⚠️  Grafana returned status {response.status_code}")
                return {"status": "warning", "endpoint": self.backend_endpoints['grafana'], "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            print("❌ Grafana is not reachable")
            return {"status": "unhealthy", "endpoint": self.backend_endpoints['grafana'], "error": "connection refused"}
        except Exception as e:
            print(f"❌ Error checking Grafana: {e}")
            return {"status": "error", "endpoint": self.backend_endpoints['grafana'], "error": str(e)}

    def check_all_backends(self) -> Dict[str, Dict[str, Any]]:
        """Check all backend services."""
        print("🏥 Checking all backend services...")
        
        results = {
            "elastic": self.check_elastic_apm(),
            "loki": self.check_loki(),
            "influxdb": self.check_influxdb(),
            "grafana": self.check_grafana()
        }
        
        # Summary
        healthy_count = sum(1 for result in results.values() if result["status"] == "healthy")
        total_count = len(results)
        
        print(f"\n📊 Backend Health Summary:")
        print(f"   Healthy: {healthy_count}/{total_count}")
        
        for backend, result in results.items():
            status_icon = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "warning" else "❌"
            print(f"   {status_icon} {backend}: {result['status']}")
        
        return results

    def get_recommendations(self, results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Get recommendations based on health check results."""
        recommendations = []
        
        for backend, result in results.items():
            if result["status"] == "unhealthy":
                recommendations.append(f"Start {backend} service: {result.get('endpoint', 'unknown endpoint')}")
            elif result["status"] == "warning":
                recommendations.append(f"Check {backend} configuration: {result.get('error', 'unknown issue')}")
        
        if not recommendations:
            recommendations.append("All backend services are healthy!")
        
        return recommendations 