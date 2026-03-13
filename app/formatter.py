from datetime import datetime

def _format_bytes(size_in_bytes):
    """Mengonversi bytes ke satuan yang mudah dibaca (KB, MB, GB, dst)."""
    if size_in_bytes is None or size_in_bytes < 0:
        return "0.00 B"
    
    size = float(size_in_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def _format_uptime(seconds):
    """Mengonversi detik ke format hari, jam, menit yang ringkas."""
    if seconds is None or seconds < 0:
        return "0m"
        
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m"

def _format_section_header(title):
    """Helper untuk mencetak judul section yang seragam."""
    return f"\n--- {title.upper()} ---"

def format_daily_report(system_metrics, process_metrics, generated_at=None):
    """
    Merakit teks laporan harian berupa plain text netral.
    Tangguh terhadap data yang hilang atau kosong (graceful parsing).
    """
    # Defensive fallback jika generated_at bukan instance datetime
    if not isinstance(generated_at, datetime):
        generated_at = datetime.now()
        
    now_str = generated_at.strftime("%Y-%m-%d %H:%M:%S")
    
    # Ekstraksi aman dengan fallback
    sys = system_metrics or {}
    cpu = sys.get("cpu", {}).get("percent", 0.0)
    ram = sys.get("ram", {})
    disk = sys.get("disk", {})
    swap = sys.get("swap", {})
    uptime_sec = sys.get("uptime_seconds", 0.0)
    la = sys.get("load_average", {"1m": 0.0, "5m": 0.0, "15m": 0.0})
    
    lines = []
    
    # HEADER & UPTIME
    lines.append("=== VPS PULSE - DAILY REPORT ===")
    lines.append(f"Time   : {now_str}")
    lines.append(f"Uptime : {_format_uptime(uptime_sec)}")
    lines.append(f"Load   : {la.get('1m', 0.0):.2f}, {la.get('5m', 0.0):.2f}, {la.get('15m', 0.0):.2f}")
    
    # SYSTEM HEALTH
    lines.append(_format_section_header("System Health"))
    lines.append(f"CPU  : {cpu:.2f}%")
    
    ram_pct = ram.get('percent', 0.0)
    ram_used = _format_bytes(ram.get('used', 0))
    ram_avail = _format_bytes(ram.get('available', 0))
    ram_total = _format_bytes(ram.get('total', 0))
    lines.append(f"RAM  : {ram_pct:.2f}% (Used: {ram_used} | Avail: {ram_avail} | Total: {ram_total})")
    
    disk_pct = disk.get('percent', 0.0)
    disk_used = _format_bytes(disk.get('used', 0))
    disk_free = _format_bytes(disk.get('free', 0))
    disk_total = _format_bytes(disk.get('total', 0))
    lines.append(f"DISK : {disk_pct:.2f}% (Used: {disk_used} | Free: {disk_free} | Total: {disk_total})")
    
    swap_pct = swap.get('percent', 0.0)
    lines.append(f"SWAP : {swap_pct:.2f}%")
    
    # TOP CPU PROCESSES
    lines.append(_format_section_header("Top CPU Processes"))
    proc = process_metrics or {}
    top_cpu = proc.get("top_cpu", [])
    
    if not top_cpu:
        lines.append("  (Tidak ada data)")
    else:
        for i, p in enumerate(top_cpu, 1):
            name = p.get("name", "unknown")
            pid = p.get("pid", "-")
            pct = p.get("cpu_percent", 0.0)
            lines.append(f"{i}. {name} (PID: {pid}) - {pct:.2f}%")
    
    # TOP RAM PROCESSES
    lines.append(_format_section_header("Top RAM Processes"))
    top_ram = proc.get("top_ram", [])
    
    if not top_ram:
        lines.append("  (Tidak ada data)")
    else:
        for i, p in enumerate(top_ram, 1):
            name = p.get("name", "unknown")
            pid = p.get("pid", "-")
            pct = p.get("ram_percent", 0.0)
            rss = p.get("ram_rss_bytes", 0)
            lines.append(f"{i}. {name} (PID: {pid}) - {pct:.2f}% ({_format_bytes(rss)})")
            
    return "\n".join(lines)

