import os
import time
import psutil

def collect_system_metrics(logger=None, disk_path="/", proc_path=None):
    """
    Mengumpulkan metrik inti sistem.
    Tangguh terhadap kegagalan parsial dan mengembalikan output dictionary yang konsisten.
    
    Argumen:
        logger: Objek logger yang diinjeksi dari orchestrator.
        disk_path: Path untuk mengecek disk usage (berguna jika di-mount dari host Docker).
        proc_path: Path /proc kustom (berguna jika membaca proc host dari dalam Docker).
    """
    
    # Docker-awareness: Jika proc_path diinjeksi oleh main.py, arahkan psutil ke sana.
    if proc_path and os.path.exists(proc_path):
        psutil.PROCFS_PATH = proc_path

    # Struktur output statis dan simetris. 
    # Menjamin konsistensi schema bagi modul formatter/alerts nanti.
    metrics = {
        "cpu": {"percent": 0.0},
        "ram": {"total": 0, "used": 0, "available": 0, "percent": 0.0},
        "disk": {"total": 0, "used": 0, "free": 0, "percent": 0.0},
        "swap": {"total": 0, "used": 0, "free": 0, "percent": 0.0},
        "uptime_seconds": 0.0,
        "load_average": {"1m": 0.0, "5m": 0.0, "15m": 0.0}
    }

    # 1. Collect CPU Usage
    try:
        # Pilihan sadar: interval=1.0 memblokir eksekusi selama 1 detik penuh
        # agar mendapatkan rata-rata penggunaan CPU yang akurat dan stabil.
        metrics["cpu"]["percent"] = psutil.cpu_percent(interval=1.0)
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil metrik CPU: {e}")

    # 2. Collect RAM Usage
    try:
        mem = psutil.virtual_memory()
        metrics["ram"] = {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent
        }
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil metrik RAM: {e}")

    # 3. Collect Disk Usage
    try:
        disk = psutil.disk_usage(disk_path)
        metrics["disk"] = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil metrik Disk pada path '{disk_path}': {e}")

    # 4. Collect Swap Usage
    try:
        swap = psutil.swap_memory()
        metrics["swap"] = {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil metrik Swap: {e}")

    # 5. Collect Uptime
    try:
        boot_time = psutil.boot_time()
        metrics["uptime_seconds"] = time.time() - boot_time
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil Uptime: {e}")

    # 6. Collect Load Average
    try:
        if hasattr(os, 'getloadavg'):
            la = os.getloadavg()
            metrics["load_average"] = {"1m": la[0], "5m": la[1], "15m": la[2]}
        else:
            if logger:
                logger.warning("Fungsi os.getloadavg() tidak didukung di sistem ini.")
    except Exception as e:
        if logger:
            logger.error(f"Collector gagal mengambil Load Average: {e}")

    return metrics

