import psutil
import logging
import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ResourceStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class ResourceMetrics:
    cpu_percent: float
    memory_percent: float
    load_avg: Tuple[float, float, float]  # 1min, 5min, 15min
    temperature: float  # Celsius
    status: ResourceStatus

class ResourceMonitor:
    def __init__(self, cpu_threshold_critical: float = 85.0, mem_threshold_critical: float = 90.0):
        self.cpu_threshold = cpu_threshold_critical
        self.mem_threshold = mem_threshold_critical
        
    def _get_temperature(self) -> float:
        """Get CPU temperature from thermal zone."""
        try:
            # Try psutil first (cross-platform)
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for coretemp or k10temp (AMD)
                for name in ['coretemp', 'k10temp', 'cpu_thermal']:
                    if name in temps:
                        return temps[name][0].current
                # Fallback to first available
                first_sensor = list(temps.values())[0]
                if first_sensor:
                    return first_sensor[0].current
        except Exception:
            pass
        
        # Fallback: read from thermal zone
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000.0
        except Exception:
            return 0.0
        
    def get_metrics(self) -> ResourceMetrics:
        try:
            cpu = psutil.cpu_percent(interval=None) 
            mem = psutil.virtual_memory().percent
            load = os.getloadavg()  # (1min, 5min, 15min)
            temp = self._get_temperature()
            
            status = ResourceStatus.HEALTHY
            if cpu > self.cpu_threshold or mem > self.mem_threshold:
                status = ResourceStatus.CRITICAL
            elif cpu > (self.cpu_threshold - 15) or mem > (self.mem_threshold - 10):
                status = ResourceStatus.WARNING
                
            return ResourceMetrics(
                cpu_percent=cpu,
                memory_percent=mem,
                load_avg=load,
                temperature=temp,
                status=status
            )
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return ResourceMetrics(0.0, 0.0, (0.0, 0.0, 0.0), 0.0, ResourceStatus.HEALTHY)

    def should_use_light_model(self) -> bool:
        metrics = self.get_metrics()
        return metrics.status == ResourceStatus.CRITICAL
