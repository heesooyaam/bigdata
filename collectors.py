from typing import Dict, Any, Optional

import psutil

BYTES_IN_MB = 1024 * 1024
BYTES_IN_GB = 1024 * 1024 * 1024


def _bytes_to_gb(n: int) -> float:
    return round(n / BYTES_IN_GB, 2)


def _bytes_to_mb(n: int) -> float:
    return round(n / BYTES_IN_MB, 2)


def collect_cpu() -> Dict[str, Any]:
    cpu_load = psutil.cpu_percent(interval=0.1)
    return {"cpu_load_percent": cpu_load}


def collect_ram() -> Dict[str, Any]:
    vm = psutil.virtual_memory()
    return {
        "ram_total_gb": _bytes_to_gb(vm.total),
        "ram_used_gb": _bytes_to_gb(vm.used),
        "ram_free_gb": _bytes_to_gb(vm.available),
    }


def collect_disk() -> Dict[str, Any]:
    du = psutil.disk_usage("/")
    return {
        "disk_total_gb": _bytes_to_gb(du.total),
        "disk_used_gb": _bytes_to_gb(du.used),
        "disk_free_gb": _bytes_to_gb(du.free),
    }


def collect_net(prev_counters: Optional[psutil._common.snetio]) -> Dict[str, Any]:
    """
    Кумулятивный сетевой трафик с момента загрузки системы, в мегабайтах.
    """
    net = psutil.net_io_counters()
    return {
        "net_in_total_mb": _bytes_to_mb(net.bytes_recv),
        "net_out_total_mb": _bytes_to_mb(net.bytes_sent),
    }
