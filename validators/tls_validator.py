import ssl
import socket
import requests
import urllib3
from typing import Dict, Any, Optional
from pathlib import Path
import certifi

class TLSValidator:
    def __init__(self):
        self.verify_ssl = True
        self.ca_cert_path = None
        self.client_cert_path = None
        self.client_key_path = None
        
    def set_ca_cert(self, ca_cert_path: str):
        """Set custom CA certificate path."""
        if Path(ca_cert_path).exists():
            self.ca_cert_path = ca_cert_path
            print(f"✅ Using custom CA certificate: {ca_cert_path}")
        else:
            print(f"❌ CA certificate not found: {ca_cert_path}")
    
    def set_client_certs(self, cert_path: str, key_path: str):
        """Set client certificate and key for mutual TLS."""
        if Path(cert_path).exists() and Path(key_path).exists():
            self.client_cert_path = cert_path
            self.client_key_path = key_path
            print(f"✅ Using client certificates: {cert_path}, {key_path}")
        else:
            print(f"❌ Client certificates not found: {cert_path}, {key_path}")
    
    def disable_ssl_verification(self):
        """Disable SSL verification (for self-signed certs in dev)."""
        self.verify_ssl = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("⚠️  SSL verification disabled (development mode)")
    
    def check_tls_endpoint(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Check TLS certificate validity for an endpoint."""
        print(f"🔒 Checking TLS for: {url}")
        
        try:
            # Parse URL
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Configure requests session
            session = requests.Session()
            
            if self.ca_cert_path:
                session.verify = self.ca_cert_path
            elif not self.verify_ssl:
                session.verify = False
            
            if self.client_cert_path and self.client_key_path:
                session.cert = (self.client_cert_path, self.client_key_path)
            
            # Make request
            response = session.get(url, timeout=timeout)
            
            # Check certificate info
            cert_info = self._get_certificate_info(url)
            
            return {
                "status": "healthy",
                "url": url,
                "status_code": response.status_code,
                "certificate": cert_info,
                "tls_version": response.raw.connection.sock.version() if hasattr(response.raw.connection, 'sock') else "unknown"
            }
            
        except requests.exceptions.SSLError as e:
            return {
                "status": "ssl_error",
                "url": url,
                "error": str(e),
                "recommendation": "Check certificate validity or add custom CA cert"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "status": "connection_error",
                "url": url,
                "error": str(e),
                "recommendation": "Check network connectivity and endpoint availability"
            }
        except Exception as e:
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "recommendation": "Check endpoint configuration"
            }
    
    def _get_certificate_info(self, url: str) -> Dict[str, Any]:
        """Extract certificate information."""
        try:
            # Parse hostname and port
            if url.startswith('https://'):
                url = url[8:]
            elif url.startswith('http://'):
                url = url[7:]
            
            if ':' in url:
                hostname, port = url.split(':', 1)
                port = int(port)
            else:
                hostname = url
                port = 443
            
            # Create SSL context
            context = ssl.create_default_context()
            if self.ca_cert_path:
                context.load_verify_locations(self.ca_cert_path)
            elif not self.verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        "subject": dict(x[0] for x in cert['subject']),
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "version": cert['version'],
                        "serial_number": cert['serialNumber'],
                        "not_before": cert['notBefore'],
                        "not_after": cert['notAfter'],
                        "san": cert.get('subjectAltName', []),
                        "tls_version": ssock.version()
                    }
        except Exception as e:
            return {"error": str(e)}
    
    def validate_exporters_tls(self, exporters: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Validate TLS for all exporter endpoints."""
        print("🔒 Validating TLS for all exporters...")
        
        results = {}
        for exporter_name, endpoint in exporters.items():
            results[exporter_name] = self.check_tls_endpoint(endpoint)
        
        # Summary
        healthy_count = sum(1 for result in results.values() if result["status"] == "healthy")
        total_count = len(results)
        
        print(f"\n📊 TLS Validation Summary:")
        print(f"   Healthy: {healthy_count}/{total_count}")
        
        for exporter_name, result in results.items():
            status_icon = "✅" if result["status"] == "healthy" else "❌"
            print(f"   {status_icon} {exporter_name}: {result['status']}")
        
        return results 