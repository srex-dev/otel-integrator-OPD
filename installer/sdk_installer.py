import os
import subprocess
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any

OTEL_JAVA_AGENT_URL = "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar"

class SDKInstaller:
    def __init__(self, services: Dict[str, List[Any]]):
        self.services = services

    def install_python_sdk(self):
        if not self.services.get("python"):
            return
        print("🐍 Installing OpenTelemetry Python SDK system-wide...")
        try:
            subprocess.run([
                sys.executable.replace("pythonw", "python"), "-m", "pip", "install", "--upgrade",
                "opentelemetry-api", "opentelemetry-sdk", "opentelemetry-exporter-otlp"
            ], check=True)
            print("✅ Python SDK installed.")
        except Exception as e:
            print(f"❌ Failed to install Python SDK: {e}")

    def install_node_sdk(self):
        if not self.services.get("node"):
            return
        print("🟩 Installing OpenTelemetry Node.js SDK in detected project directories...")
        project_dirs = set()
        for proc in self.services["node"]:
            # Try to find the working directory or project root
            cwd = proc.get("cwd") or proc.get("exe")
            if cwd:
                cwd_path = Path(cwd)
                # Look for package.json in cwd or parent directories
                for parent in [cwd_path] + list(cwd_path.parents):
                    if (parent / "package.json").exists():
                        project_dirs.add(str(parent))
                        break
        # Also scan for package.json in scan path if not found from processes
        if not project_dirs:
            for root, dirs, files in os.walk("."):
                if "package.json" in files:
                    project_dirs.add(root)
        for project_dir in project_dirs:
            try:
                print(f"  📦 Installing Node.js SDK in {project_dir} ...")
                subprocess.run([
                    "npm", "install", "--save",
                    "@opentelemetry/api", "@opentelemetry/sdk-trace-base", "@opentelemetry/exporter-otlp-http"
                ], cwd=project_dir, check=True)
                print(f"  ✅ Node.js SDK installed in {project_dir}.")
            except Exception as e:
                print(f"  ❌ Failed in {project_dir}: {e}")

    def install_java_agent(self):
        if not self.services.get("java"):
            return
        print("☕ Downloading OpenTelemetry Java agent to detected project directories...")
        project_dirs = set()
        for proc in self.services["java"]:
            cwd = proc.get("cwd") or proc.get("exe")
            if cwd:
                cwd_path = Path(cwd)
                # Look for pom.xml or build.gradle in cwd or parent directories
                for parent in [cwd_path] + list(cwd_path.parents):
                    if (parent / "pom.xml").exists() or (parent / "build.gradle").exists():
                        project_dirs.add(str(parent))
                        break
        # Also scan for pom.xml/build.gradle in scan path if not found from processes
        if not project_dirs:
            for root, dirs, files in os.walk("."):
                if "pom.xml" in files or "build.gradle" in files:
                    project_dirs.add(root)
        for project_dir in project_dirs:
            try:
                dest = Path(project_dir) / "opentelemetry-javaagent.jar"
                print(f"  ☁️ Downloading Java agent to {dest} ...")
                r = requests.get(OTEL_JAVA_AGENT_URL, stream=True)
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✅ Java agent downloaded to {dest}.")
            except Exception as e:
                print(f"  ❌ Failed to download Java agent to {project_dir}: {e}")

    def install_all(self):
        self.install_python_sdk()
        self.install_node_sdk()
        self.install_java_agent() 