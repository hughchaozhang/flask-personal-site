import platform
import psutil
import os

def get_system_stats():
    """Get system statistics for Raspberry Pi"""
    
    # Get hostname, platform, and architecture
    hostname = platform.node()
    os_platform = platform.platform()
    architecture = platform.machine()
    
    # Get CPU temperature (specific to Raspberry Pi)
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000  # Convert millicelsius to celsius
    except:
        temp = None
    
    # Get CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Get memory information
    memory = psutil.virtual_memory()
    memory_total = memory.total / (1024 * 1024 * 1024)  # Convert to GB
    memory_used = memory.used / (1024 * 1024 * 1024)    # Convert to GB
    memory_percent = memory.percent
    
    return {
        'hostname': hostname,
        'platform': os_platform,
        'architecture': architecture,
        'cpu_temp': f"{temp:.1f}°C" if temp is not None else "N/A",
        'cpu_usage': f"{cpu_usage:.1f}%",
        'memory_total': f"{memory_total:.1f}GB",
        'memory_used': f"{memory_used:.1f}GB",
        'memory_percent': f"{memory_percent:.1f}%"
    }