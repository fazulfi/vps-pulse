import time
import psutil

def collect_process_metrics(logger=None, top_n=5):
    """
    Mengumpulkan metrik proses untuk mendapatkan ranking Top N berdasarkan CPU dan RAM.
    
    Argumen:
        logger: Objek logger yang diinjeksi dari orchestrator.
        top_n: Jumlah maksimal proses yang dikembalikan per kategori. Akan divalidasi.
        
    Catatan Latensi:
        Fungsi ini memiliki latency cost disengaja sebesar ~0.5 detik karena 
        menggunakan jeda (sleep) untuk mengakumulasi delta waktu CPU dari psutil.
    """
    
    # 1. Validasi Input top_n
    try:
        top_n = int(top_n)
        if top_n < 1:
            raise ValueError(f"Nilai harus >= 1, diterima: {top_n}")
    except (ValueError, TypeError) as e:
        if logger:
            logger.warning(f"Parameter top_n tidak valid. Fallback ke 5. Detail: {e}")
        top_n = 5

    processes = []
    
    # 2. Pre-fetch CPU (Priming pass)
    # Panggilan cpu_percent(None) pertama menginisialisasi timer internal psutil
    for proc in psutil.process_iter(['pid']):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Jeda singkat agar OS bisa mengakumulasi delta waktu CPU
    # Ini adalah trade-off sadar demi akurasi CPU snapshot
    time.sleep(0.5)
    
    # 3. Collection pass
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'memory_info']):
        pid = "unknown"
        try:
            p_info = proc.info
            pid = p_info.get("pid", "unknown")
            
            # Ambil cpu_percent setelah jeda
            cpu_pct = proc.cpu_percent(interval=None)
            
            # Ekstraksi nilai absolut RAM (Resident Set Size) dalam bytes
            mem_info = p_info.get("memory_info")
            ram_rss_bytes = mem_info.rss if mem_info else 0
            
            # Normalisasi data
            process_data = {
                "pid": pid,
                "name": p_info.get("name", "unknown") or "unknown",
                "user": p_info.get("username", "unknown") or "unknown",
                "cpu_percent": round(cpu_pct, 2) if cpu_pct else 0.0,
                "ram_percent": round(p_info.get("memory_percent", 0.0) or 0.0, 2),
                "ram_rss_bytes": ram_rss_bytes
            }
            processes.append(process_data)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Graceful degradation: Abaikan diam-diam proses yang mati di tengah jalan
            # atau tidak bisa diakses
            continue
        except Exception as e:
            if logger:
                # Menyertakan konteks PID untuk mempermudah debugging
                logger.warning(f"Kegagalan tak terduga saat membaca metrik PID {pid}: {e}")
            continue

    # 4. Urutkan berdasarkan CPU (Descending)
    top_cpu = sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)[:top_n]
    
    # 5. Urutkan berdasarkan RAM (Descending)
    top_ram = sorted(processes, key=lambda p: p["ram_percent"], reverse=True)[:top_n]
    
    return {
        "top_cpu": top_cpu,
        "top_ram": top_ram
    }

