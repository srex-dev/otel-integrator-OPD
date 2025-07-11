import os
import platform
import subprocess
import shutil
from pathlib import Path
import requests
import tarfile
import zipfile
import uuid

class CollectorInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.collector_version = "0.96.0"  # Latest stable version
        
    def get_download_url(self):
        base_url = f"https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v{self.collector_version}"
        if self.system == "darwin":
            if "arm" in self.machine or "aarch64" in self.machine:
                return f"{base_url}/otelcol_{self.collector_version}_darwin_arm64.tar.gz"
            else:
                return f"{base_url}/otelcol_{self.collector_version}_darwin_amd64.tar.gz"
        elif self.system == "linux":
            if "arm" in self.machine or "aarch64" in self.machine:
                return f"{base_url}/otelcol_{self.collector_version}_linux_arm64.tar.gz"
            else:
                return f"{base_url}/otelcol_{self.collector_version}_linux_amd64.tar.gz"
        elif self.system == "windows":
            return f"{base_url}/otelcol_{self.collector_version}_windows_amd64.zip"
        else:
            raise ValueError(f"Unsupported system: {self.system}")
    
    def download_collector(self, download_dir="/tmp"):
        url = self.get_download_url()
        filename = url.split("/")[-1]
        filepath = Path(download_dir) / filename
        print(f"📥 Downloading OpenTelemetry Collector from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded to: {filepath}")
        return filepath
    
    def extract_collector(self, archive_path, extract_dir_base="/tmp"):
        import os
        import subprocess
        unique_dir = Path(extract_dir_base) / f"otelcol_install_{uuid.uuid4().hex[:8]}"
        unique_dir.mkdir(parents=True, exist_ok=True)
        binary_name = "otelcol"
        print(f"📦 Extracting {archive_path} to {unique_dir}")
        extracted = False
        if archive_path.suffix == ".tar.gz":
            # Try system tar first
            try:
                subprocess.run(["tar", "-xzf", str(archive_path), "-C", str(unique_dir)], check=True)
                extracted = True
            except Exception as e:
                print(f"⚠️  System tar extraction failed: {e}. Trying Python tarfile module...")
                try:
                    import tarfile
                    with tarfile.open(archive_path, 'r:gz') as tar:
                        tar.extractall(unique_dir)
                    extracted = True
                except Exception as e2:
                    print(f"❌ Python tarfile extraction also failed: {e2}")
        elif archive_path.suffix == ".zip":
            try:
                import zipfile
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(unique_dir)
                extracted = True
            except Exception as e:
                print(f"❌ Zip extraction failed: {e}")
        if not extracted:
            print(f"❌ Extraction failed for {archive_path}")
            raise RuntimeError(f"Could not extract {archive_path}")
        # Find the binary
        binary_path = unique_dir / binary_name
        if not binary_path.exists():
            for file in unique_dir.rglob(binary_name):
                binary_path = file
                break
        if not binary_path.exists():
            print(f"🔍 Files in {unique_dir} (recursive):")
            for root, dirs, files in os.walk(unique_dir):
                for name in files:
                    print(os.path.join(root, name))
            raise FileNotFoundError(f"Could not find {binary_name} in extracted files")
        print(f"✅ Extracted binary to: {binary_path}")
        return binary_path, unique_dir
    
    def install_collector(self, binary_path, install_dir="/usr/local/bin"):
        install_path = Path(install_dir) / "otelcol"
        print(f"🔧 Installing collector to: {install_path}")
        shutil.copy2(binary_path, install_path)
        os.chmod(install_path, 0o755)
        print(f"✅ Collector installed to: {install_path}")
        return install_path
    
    def create_systemd_service(self, config_path, service_name="otel-collector"):
        if self.system != "linux":
            print("⚠️  Systemd service creation only supported on Linux")
            return None
        service_content = f"""[Unit]
Description=OpenTelemetry Collector
After=network.target

[Service]
Type=simple
User=otel-collector
Group=otel-collector
ExecStart=/usr/local/bin/otelcol --config {config_path}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        service_file = Path(f"/etc/systemd/system/{service_name}.service")
        print(f"📝 Creating systemd service: {service_file}")
        try:
            subprocess.run(["useradd", "-r", "-s", "/bin/false", "otel-collector"], 
                         check=False, capture_output=True)
        except:
            pass
        with open(service_file, 'w') as f:
            f.write(service_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", service_name], check=True)
        print(f"✅ Systemd service created and enabled: {service_name}")
        return service_file
    
    def create_launchd_service(self, config_path, service_name="otel-collector"):
        if self.system != "darwin":
            print("⚠️  Launchd service creation only supported on macOS")
            return None
        plist_content = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>{service_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/otelcol</string>
        <string>--config</string>
        <string>{config_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/var/log/{service_name}.err</string>
    <key>StandardOutPath</key>
    <string>/var/log/{service_name}.out</string>
</dict>
</plist>
"""
        plist_file = Path(f"~/Library/LaunchAgents/{service_name}.plist").expanduser()
        print(f"📝 Creating launchd service: {plist_file}")
        plist_file.parent.mkdir(parents=True, exist_ok=True)
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        subprocess.run(["launchctl", "load", str(plist_file)], check=True)
        print(f"✅ Launchd service created and loaded: {service_name}")
        return plist_file
    
    def install_and_start(self, config_path):
        print("🚀 Starting OpenTelemetry Collector installation...")
        archive_path = self.download_collector()
        binary_path, extract_dir = self.extract_collector(archive_path)
        install_path = self.install_collector(binary_path)
        if self.system == "linux":
            service_file = self.create_systemd_service(config_path)
            if service_file:
                subprocess.run(["systemctl", "start", "otel-collector"], check=True)
                print("✅ OpenTelemetry Collector service started")
        elif self.system == "darwin":
            service_file = self.create_launchd_service(config_path)
            if service_file:
                subprocess.run(["launchctl", "start", "otel-collector"], check=True)
                print("✅ OpenTelemetry Collector service started")
        else:
            print(f"⚠️  Automatic service creation not supported on {self.system}")
            print(f"   You can run the collector manually with:")
            print(f"   {install_path} --config {config_path}")
        # Cleanup
        try:
            archive_path.unlink(missing_ok=True)
            shutil.rmtree(extract_dir, ignore_errors=True)
        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")
        return install_path 