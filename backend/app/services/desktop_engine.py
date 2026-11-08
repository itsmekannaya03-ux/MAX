import psutil
import platform
import os
from datetime import datetime
from typing import Dict, Any, List

class DesktopEngine:
    def __init__(self):
        pass

    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Provides non-destructive system diagnostics for the executive dashboard."""
        cpu_pct = 0.0
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
        except Exception:
            pass

        mem_used = 0.0
        mem_total = 0.0
        mem_pct = 0.0
        try:
            mem = psutil.virtual_memory()
            mem_used = round((mem.total - mem.available) / (1024**3), 2)
            mem_total = round(mem.total / (1024**3), 2)
            mem_pct = mem.percent
        except Exception:
            pass

        disk_pct = 0.0
        try:
            drive = os.path.splitdrive(os.getcwd())[0] + '\\'
            disk = psutil.disk_usage(drive)
            disk_pct = disk.percent
        except Exception:
            pass

        battery_pct = None
        battery_plugged = None
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_pct = battery.percent
                battery_plugged = battery.power_plugged
        except Exception:
            pass

        return {
            "os": f"{platform.system()} {platform.release()}",
            "hostname": platform.node(),
            "cpu_percent": cpu_pct,
            "memory_used_gb": mem_used,
            "memory_total_gb": mem_total,
            "memory_percent": mem_pct,
            "disk_percent": disk_pct,
            "battery_percent": battery_pct,
            "battery_plugged": battery_plugged,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def list_running_focus_apps(self) -> List[Dict[str, Any]]:
        """Lists common productivity apps currently open."""
        apps = []
        for p in psutil.process_iter(['name', 'cpu_percent']):
            try:
                name = p.info['name'].lower()
                if any(tool in name for tool in ['code', 'pycharm', 'cursor', 'chrome', 'edge', 'spotify', 'slack', 'discord', 'notepad']):
                    apps.append({"name": p.info['name'], "cpu": p.info['cpu_percent']})
            except Exception:
                pass
        return apps[:15]

desktop_engine = DesktopEngine()
