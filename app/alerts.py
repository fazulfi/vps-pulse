def _validate_threshold(resource_name, raw_val, logger=None):
    """
    Helper internal untuk memvalidasi angka threshold.
    Memastikan tipe data float dan berada dalam range 0.0 - 100.0.
    """
    try:
        val = float(raw_val)
        if val < 0.0 or val > 100.0:
            clamped = max(0.0, min(100.0, val))
            if logger:
                logger.warning(
                    f"Alerts: Threshold {resource_name} ({val}) di luar batas 0-100. "
                    f"Dikoreksi ke {clamped:.2f}"
                )
            return clamped
        return val
    except (ValueError, TypeError):
        if logger:
            logger.warning(
                f"Alerts: Threshold {resource_name} tidak valid: '{raw_val}'. "
                f"Fallback ke aman (100.0)"
            )
        return 100.0

def evaluate_alerts(metrics, thresholds, logger=None):
    """
    Mengevaluasi metrik sistem terhadap ambang batas yang diberikan.
    
    Argumen:
        metrics (dict): Data dari app/collector.py
        thresholds (dict): Konfigurasi threshold dari app/config.py (lewat orchestrator)
        logger: Objek logger opsional.
        
    Returns:
        list: Daftar alert yang terpicu dengan kontrak data eksplisit.
    """
    triggered_alerts = []
    
    if not isinstance(metrics, dict) or not isinstance(thresholds, dict):
        if logger:
            logger.error("Alerts: Input metrics atau thresholds bukan dictionary. Evaluasi dibatalkan.")
        return triggered_alerts

    # Pemetaan resource ke key pada metrics dan thresholds
    monitoring_map = {
        "CPU": ("cpu", "percent", "cpu_threshold_percent"),
        "RAM": ("ram", "percent", "ram_threshold_percent"),
        "DISK": ("disk", "percent", "disk_threshold_percent")
    }

    for resource_name, (m_key, sub_key, t_key) in monitoring_map.items():
        try:
            # 1. Ekstraksi Metrik Aktual
            raw_current = metrics.get(m_key, {}).get(sub_key)
            if raw_current is None:
                if logger:
                    logger.debug(f"Alerts: Metrik {resource_name} tidak tersedia untuk dievaluasi.")
                continue
                
            current_val = float(raw_current)
            
            # 2. Ekstraksi dan Validasi Threshold
            raw_threshold = thresholds.get(t_key, 100.0)
            threshold_val = _validate_threshold(resource_name, raw_threshold, logger)

            # 3. Evaluasi Pelanggaran
            if current_val > threshold_val:
                # Membuat pesan yang netral dan langsung pakai
                msg = f"Penggunaan {resource_name} ({current_val:.2f}%) melampaui ambang batas ({threshold_val:.2f}%)"
                
                alert_data = {
                    "resource": resource_name,
                    "current": round(current_val, 2),
                    "threshold": round(threshold_val, 2),
                    "triggered": True,
                    "message": msg
                }
                triggered_alerts.append(alert_data)
                
                if logger:
                    logger.info(f"ALERT TRIGGERED: {msg}")

        except Exception as e:
            if logger:
                logger.error(f"Alerts: Error tak terduga saat mengevaluasi {resource_name}: {e}")
            continue

    return triggered_alerts

