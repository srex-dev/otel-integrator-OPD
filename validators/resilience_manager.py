import time
import asyncio
import threading
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._can_execute():
            raise Exception(f"Circuit breaker is {self.state.value}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _can_execute(self) -> bool:
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False
    
    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN

class RetryHandler:
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_attempts - 1:
                    raise last_exception
                
                delay = self._calculate_delay(attempt)
                print(f"⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay

class ResilienceManager:
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if name not in self.circuit_breakers:
            config = config or CircuitBreakerConfig()
            self.circuit_breakers[name] = CircuitBreaker(config)
        return self.circuit_breakers[name]
    
    def get_retry_handler(self, name: str, config: Optional[RetryConfig] = None) -> RetryHandler:
        """Get or create a retry handler for a service."""
        if name not in self.retry_handlers:
            config = config or RetryConfig()
            self.retry_handlers[name] = RetryHandler(config)
        return self.retry_handlers[name]
    
    def execute_with_resilience(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with both circuit breaker and retry protection."""
        circuit_breaker = self.get_circuit_breaker(service_name)
        retry_handler = self.get_retry_handler(service_name)
        
        def protected_func():
            return circuit_breaker.call(func, *args, **kwargs)
        
        return retry_handler.execute_with_retry(protected_func)
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health status of a service."""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if not circuit_breaker:
            return {"status": "unknown", "service": service_name}
        
        return {
            "status": circuit_breaker.state.value,
            "service": service_name,
            "failure_count": circuit_breaker.failure_count,
            "last_failure": circuit_breaker.last_failure_time
        }
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all monitored services."""
        return {
            service_name: self.check_service_health(service_name)
            for service_name in self.circuit_breakers.keys()
        }
    
    def reset_circuit_breaker(self, service_name: str):
        """Manually reset a circuit breaker."""
        if service_name in self.circuit_breakers:
            cb = self.circuit_breakers[service_name]
            with cb.lock:
                cb.state = CircuitState.CLOSED
                cb.failure_count = 0
            print(f"✅ Reset circuit breaker for {service_name}")
        else:
            print(f"❌ No circuit breaker found for {service_name}")
    
    def graceful_degradation(self, exporters: Dict[str, Callable], fallback_exporters: Dict[str, Callable] = None) -> Dict[str, Any]:
        """Execute exporters with graceful degradation."""
        results = {}
        fallback_exporters = fallback_exporters or {}
        
        for exporter_name, exporter_func in exporters.items():
            try:
                result = self.execute_with_resilience(exporter_name, exporter_func)
                results[exporter_name] = {"status": "success", "result": result}
            except Exception as e:
                # Try fallback if available
                if exporter_name in fallback_exporters:
                    try:
                        fallback_result = self.execute_with_resilience(
                            f"{exporter_name}_fallback", 
                            fallback_exporters[exporter_name]
                        )
                        results[exporter_name] = {
                            "status": "fallback_success", 
                            "fallback_result": fallback_result,
                            "original_error": str(e)
                        }
                    except Exception as fallback_e:
                        results[exporter_name] = {
                            "status": "failed", 
                            "error": str(e),
                            "fallback_error": str(fallback_e)
                        }
                else:
                    results[exporter_name] = {"status": "failed", "error": str(e)}
        
        return results 