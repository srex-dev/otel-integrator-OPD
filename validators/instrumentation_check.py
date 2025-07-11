import os
import re
from typing import Dict, List, Any, Set
from pathlib import Path

class InstrumentationChecker:
    def __init__(self):
        self.language_instrumentation = {
            "python": {
                "auto": "opentelemetry-instrumentation",
                "manual": ["opentelemetry-api", "opentelemetry-sdk"],
                "frameworks": {
                    "flask": "opentelemetry-instrumentation-flask",
                    "django": "opentelemetry-instrumentation-django",
                    "fastapi": "opentelemetry-instrumentation-fastapi",
                    "requests": "opentelemetry-instrumentation-requests",
                    "sqlalchemy": "opentelemetry-instrumentation-sqlalchemy",
                    "redis": "opentelemetry-instrumentation-redis"
                }
            },
            "nodejs": {
                "auto": "@opentelemetry/auto-instrumentations-node",
                "manual": ["@opentelemetry/api", "@opentelemetry/sdk-node"],
                "frameworks": {
                    "express": "@opentelemetry/instrumentation-express",
                    "http": "@opentelemetry/instrumentation-http",
                    "mysql": "@opentelemetry/instrumentation-mysql",
                    "redis": "@opentelemetry/instrumentation-redis",
                    "mongodb": "@opentelemetry/instrumentation-mongodb"
                }
            },
            "java": {
                "auto": "opentelemetry-javaagent",
                "manual": ["opentelemetry-api", "opentelemetry-sdk"],
                "frameworks": {
                    "spring": "opentelemetry-instrumentation-spring",
                    "servlet": "opentelemetry-instrumentation-servlet",
                    "jdbc": "opentelemetry-instrumentation-jdbc",
                    "redis": "opentelemetry-instrumentation-redis"
                }
            },
            "go": {
                "auto": "go.opentelemetry.io/otel",
                "manual": ["go.opentelemetry.io/otel/api", "go.opentelemetry.io/otel/sdk"],
                "frameworks": {
                    "gin": "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin",
                    "http": "go.opentelemetry.io/contrib/instrumentation/net/http",
                    "grpc": "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc"
                }
            },
            "dotnet": {
                "auto": "OpenTelemetry.AutoInstrumentation",
                "manual": ["OpenTelemetry.Api", "OpenTelemetry.Sdk"],
                "frameworks": {
                    "aspnetcore": "OpenTelemetry.Instrumentation.AspNetCore",
                    "http": "OpenTelemetry.Instrumentation.Http",
                    "sqlclient": "OpenTelemetry.Instrumentation.SqlClient"
                }
            }
        }

    def check_python_instrumentation(self, project_path: str) -> Dict[str, Any]:
        """Check Python project for OpenTelemetry instrumentation."""
        print("🔍 Checking Python instrumentation...")
        
        requirements_files = ["requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py"]
        found_instrumentation = set()
        missing_instrumentation = set()
        
        for req_file in requirements_files:
            req_path = os.path.join(project_path, req_file)
            if os.path.exists(req_path):
                with open(req_path, 'r') as f:
                    content = f.read().lower()
                    
                    # Check for auto-instrumentation
                    if "opentelemetry-instrumentation" in content:
                        found_instrumentation.add("auto")
                    
                    # Check for manual instrumentation
                    if "opentelemetry-api" in content and "opentelemetry-sdk" in content:
                        found_instrumentation.add("manual")
                    
                    # Check for framework-specific instrumentation
                    for framework, package in self.language_instrumentation["python"]["frameworks"].items():
                        if package.lower() in content:
                            found_instrumentation.add(f"framework:{framework}")
        
        # Check for instrumentation in code
        python_files = list(Path(project_path).rglob("*.py"))
        for py_file in python_files[:10]:  # Limit to first 10 files
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if "opentelemetry" in content.lower():
                        found_instrumentation.add("code_imports")
            except:
                continue
        
        if not found_instrumentation:
            missing_instrumentation.add("auto")
            missing_instrumentation.add("manual")
        
        return {
            "status": "instrumented" if found_instrumentation else "not_instrumented",
            "found": list(found_instrumentation),
            "missing": list(missing_instrumentation),
            "recommendations": self._get_python_recommendations(found_instrumentation)
        }

    def check_nodejs_instrumentation(self, project_path: str) -> Dict[str, Any]:
        """Check Node.js project for OpenTelemetry instrumentation."""
        print("🔍 Checking Node.js instrumentation...")
        
        package_files = ["package.json", "package-lock.json", "yarn.lock"]
        found_instrumentation = set()
        missing_instrumentation = set()
        
        for pkg_file in package_files:
            pkg_path = os.path.join(project_path, pkg_file)
            if os.path.exists(pkg_path):
                with open(pkg_path, 'r') as f:
                    content = f.read().lower()
                    
                    # Check for auto-instrumentation
                    if "@opentelemetry/auto-instrumentations-node" in content:
                        found_instrumentation.add("auto")
                    
                    # Check for manual instrumentation
                    if "@opentelemetry/api" in content and "@opentelemetry/sdk-node" in content:
                        found_instrumentation.add("manual")
                    
                    # Check for framework-specific instrumentation
                    for framework, package in self.language_instrumentation["nodejs"]["frameworks"].items():
                        if package.lower() in content:
                            found_instrumentation.add(f"framework:{framework}")
        
        # Check for instrumentation in code
        js_files = list(Path(project_path).rglob("*.js")) + list(Path(project_path).rglob("*.ts"))
        for js_file in js_files[:10]:  # Limit to first 10 files
            try:
                with open(js_file, 'r') as f:
                    content = f.read()
                    if "opentelemetry" in content.lower():
                        found_instrumentation.add("code_imports")
            except:
                continue
        
        if not found_instrumentation:
            missing_instrumentation.add("auto")
            missing_instrumentation.add("manual")
        
        return {
            "status": "instrumented" if found_instrumentation else "not_instrumented",
            "found": list(found_instrumentation),
            "missing": list(missing_instrumentation),
            "recommendations": self._get_nodejs_recommendations(found_instrumentation)
        }

    def check_java_instrumentation(self, project_path: str) -> Dict[str, Any]:
        """Check Java project for OpenTelemetry instrumentation."""
        print("🔍 Checking Java instrumentation...")
        
        build_files = ["pom.xml", "build.gradle", "build.gradle.kts"]
        found_instrumentation = set()
        missing_instrumentation = set()
        
        for build_file in build_files:
            build_path = os.path.join(project_path, build_file)
            if os.path.exists(build_path):
                with open(build_path, 'r') as f:
                    content = f.read().lower()
                    
                    # Check for auto-instrumentation
                    if "opentelemetry-javaagent" in content:
                        found_instrumentation.add("auto")
                    
                    # Check for manual instrumentation
                    if "opentelemetry-api" in content and "opentelemetry-sdk" in content:
                        found_instrumentation.add("manual")
                    
                    # Check for framework-specific instrumentation
                    for framework, package in self.language_instrumentation["java"]["frameworks"].items():
                        if package.lower() in content:
                            found_instrumentation.add(f"framework:{framework}")
        
        if not found_instrumentation:
            missing_instrumentation.add("auto")
            missing_instrumentation.add("manual")
        
        return {
            "status": "instrumented" if found_instrumentation else "not_instrumented",
            "found": list(found_instrumentation),
            "missing": list(missing_instrumentation),
            "recommendations": self._get_java_recommendations(found_instrumentation)
        }

    def check_go_instrumentation(self, project_path: str) -> Dict[str, Any]:
        """Check Go project for OpenTelemetry instrumentation."""
        print("🔍 Checking Go instrumentation...")
        
        go_files = list(Path(project_path).rglob("*.go"))
        found_instrumentation = set()
        missing_instrumentation = set()
        
        for go_file in go_files[:20]:  # Check first 20 Go files
            try:
                with open(go_file, 'r') as f:
                    content = f.read()
                    if "go.opentelemetry.io/otel" in content:
                        found_instrumentation.add("manual")
                    if "go.opentelemetry.io/contrib" in content:
                        found_instrumentation.add("framework")
            except:
                continue
        
        if not found_instrumentation:
            missing_instrumentation.add("manual")
            missing_instrumentation.add("framework")
        
        return {
            "status": "instrumented" if found_instrumentation else "not_instrumented",
            "found": list(found_instrumentation),
            "missing": list(missing_instrumentation),
            "recommendations": self._get_go_recommendations(found_instrumentation)
        }

    def check_dotnet_instrumentation(self, project_path: str) -> Dict[str, Any]:
        """Check .NET project for OpenTelemetry instrumentation."""
        print("🔍 Checking .NET instrumentation...")
        
        project_files = list(Path(project_path).rglob("*.csproj")) + list(Path(project_path).rglob("*.vbproj"))
        found_instrumentation = set()
        missing_instrumentation = set()
        
        for proj_file in project_files:
            try:
                with open(proj_file, 'r') as f:
                    content = f.read()
                    if "OpenTelemetry.AutoInstrumentation" in content:
                        found_instrumentation.add("auto")
                    if "OpenTelemetry.Api" in content and "OpenTelemetry.Sdk" in content:
                        found_instrumentation.add("manual")
                    if "OpenTelemetry.Instrumentation" in content:
                        found_instrumentation.add("framework")
            except:
                continue
        
        if not found_instrumentation:
            missing_instrumentation.add("auto")
            missing_instrumentation.add("manual")
            missing_instrumentation.add("framework")
        
        return {
            "status": "instrumented" if found_instrumentation else "not_instrumented",
            "found": list(found_instrumentation),
            "missing": list(missing_instrumentation),
            "recommendations": self._get_dotnet_recommendations(found_instrumentation)
        }

    def check_all_services(self, discovered_services: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Check instrumentation for all discovered services."""
        print("🔧 Checking instrumentation for all services...")
        
        results = {}
        
        # Handle enhanced scanner format (dict with lists)
        for service_type, service_list in discovered_services.items():
            if not isinstance(service_list, list):
                continue
                
            for i, service_info in enumerate(service_list):
                if not isinstance(service_info, dict):
                    continue
                    
                # Try to determine language from service type or process info
                language = service_type.lower()
                if language == "node":
                    language = "nodejs"
                elif language in ["databases", "message_queues", "web_servers", "docker", "kubernetes", "logs", "ports", "cloud", "service_mesh", "custom"]:
                    continue  # Skip non-language services
                
                # Try to get path from process info
                service_path = ""
                if "exe" in service_info:
                    service_path = os.path.dirname(service_info["exe"])
                elif "cmdline" in service_info and service_info["cmdline"]:
                    # Try to get working directory from command line
                    cmdline = service_info["cmdline"]
                    if len(cmdline) > 1:
                        potential_path = os.path.dirname(cmdline[1])
                        if os.path.exists(potential_path):
                            service_path = potential_path
                
                service_name = f"{service_type}_{i}"
                if "name" in service_info:
                    service_name = service_info["name"]
                
                if not service_path or not os.path.exists(service_path):
                    # Use current directory as fallback
                    service_path = "."
                
                print(f"\n📦 Checking {service_name} ({language}) at {service_path}...")
                
                if language == "python":
                    results[service_name] = self.check_python_instrumentation(service_path)
                elif language == "nodejs":
                    results[service_name] = self.check_nodejs_instrumentation(service_path)
                elif language == "java":
                    results[service_name] = self.check_java_instrumentation(service_path)
                elif language == "go":
                    results[service_name] = self.check_go_instrumentation(service_path)
                elif language == "dotnet":
                    results[service_name] = self.check_dotnet_instrumentation(service_path)
                else:
                    results[service_name] = {
                        "status": "unknown_language",
                        "found": [],
                        "missing": ["instrumentation"],
                        "recommendations": [f"Unknown language: {language}"]
                    }
        
        # Summary
        instrumented_count = sum(1 for result in results.values() if result["status"] == "instrumented")
        total_count = len(results)
        
        print(f"\n📊 Instrumentation Summary:")
        print(f"   Instrumented: {instrumented_count}/{total_count}")
        
        for service_name, result in results.items():
            status_icon = "✅" if result["status"] == "instrumented" else "❌"
            print(f"   {status_icon} {service_name}: {result['status']}")
        
        return results

    def _get_python_recommendations(self, found_instrumentation: Set[str]) -> List[str]:
        """Get Python instrumentation recommendations."""
        recommendations = []
        
        if "auto" not in found_instrumentation:
            recommendations.append("Install auto-instrumentation: pip install opentelemetry-instrumentation")
        
        if "manual" not in found_instrumentation:
            recommendations.append("Install manual instrumentation: pip install opentelemetry-api opentelemetry-sdk")
        
        # Framework-specific recommendations
        frameworks_needed = ["flask", "django", "fastapi", "requests"]
        for framework in frameworks_needed:
            if f"framework:{framework}" not in found_instrumentation:
                package = self.language_instrumentation["python"]["frameworks"][framework]
                recommendations.append(f"Install {framework} instrumentation: pip install {package}")
        
        return recommendations

    def _get_nodejs_recommendations(self, found_instrumentation: Set[str]) -> List[str]:
        """Get Node.js instrumentation recommendations."""
        recommendations = []
        
        if "auto" not in found_instrumentation:
            recommendations.append("Install auto-instrumentation: npm install @opentelemetry/auto-instrumentations-node")
        
        if "manual" not in found_instrumentation:
            recommendations.append("Install manual instrumentation: npm install @opentelemetry/api @opentelemetry/sdk-node")
        
        # Framework-specific recommendations
        frameworks_needed = ["express", "http"]
        for framework in frameworks_needed:
            if f"framework:{framework}" not in found_instrumentation:
                package = self.language_instrumentation["nodejs"]["frameworks"][framework]
                recommendations.append(f"Install {framework} instrumentation: npm install {package}")
        
        return recommendations

    def _get_java_recommendations(self, found_instrumentation: Set[str]) -> List[str]:
        """Get Java instrumentation recommendations."""
        recommendations = []
        
        if "auto" not in found_instrumentation:
            recommendations.append("Add Java agent to JVM args: -javaagent:opentelemetry-javaagent.jar")
        
        if "manual" not in found_instrumentation:
            recommendations.append("Add manual instrumentation dependencies to pom.xml or build.gradle")
        
        return recommendations

    def _get_go_recommendations(self, found_instrumentation: Set[str]) -> List[str]:
        """Get Go instrumentation recommendations."""
        recommendations = []
        
        if "manual" not in found_instrumentation:
            recommendations.append("Install OpenTelemetry Go: go get go.opentelemetry.io/otel")
        
        if "framework" not in found_instrumentation:
            recommendations.append("Install HTTP instrumentation: go get go.opentelemetry.io/contrib/instrumentation/net/http")
        
        return recommendations

    def _get_dotnet_recommendations(self, found_instrumentation: Set[str]) -> List[str]:
        """Get .NET instrumentation recommendations."""
        recommendations = []
        
        if "auto" not in found_instrumentation:
            recommendations.append("Install OpenTelemetry.AutoInstrumentation NuGet package")
        
        if "manual" not in found_instrumentation:
            recommendations.append("Install OpenTelemetry.Api and OpenTelemetry.Sdk NuGet packages")
        
        return recommendations 