import os
import psutil

def detect_services(scan_path: str = "."):
    print("🔍 Scanning for services...")
    services = {
        "python": [],
        "node": [],
        "docker": [],
        "logs": [],
    }

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline'])
            if "python" in cmd:
                services["python"].append(proc.info)
            elif "node" in cmd:
                services["node"].append(proc.info)
            elif "docker" in cmd:
                services["docker"].append(proc.info)
        except Exception:
            continue

    # Simulate finding logs
    for root, dirs, files in os.walk(scan_path):
        for file in files:
            if file.endswith(".log"):
                services["logs"].append(os.path.join(root, file))

    return services
