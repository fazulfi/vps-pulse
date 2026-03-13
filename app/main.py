import sys
from app.logger import setup_logger
from app.config import load_config
from app.collector import collect_system_metrics
from app.process_collector import collect_process_metrics
from app.alerts import evaluate_alerts
from app.formatter import format_daily_report
from app.notifier import dispatch_notification

def _dispatch_alerts(alerts, notif_mode, tg_token, tg_chat_id, logger):
    """
    Helper internal untuk mengiterasi dan mengirim daftar alert.
    """
    if not alerts:
        logger.info("Semua metrik dalam batas aman. Tidak ada alert tambahan.")
        return

    triggered_alerts = [a for a in alerts if a.get("triggered")]
    if not triggered_alerts:
        return

    logger.warning(f"Ditemukan {len(triggered_alerts)} pelanggaran threshold! Mengirim alert...")
    for alert in triggered_alerts:
        alert_msg = f"=== VPS PULSE ALERT ===\n{alert.get('message', 'Peringatan tidak diketahui')}"
        
        results = dispatch_notification(
            message=alert_msg,
            mode=notif_mode,
            telegram_token=tg_token,
            telegram_chat_id=tg_chat_id,
            logger=logger
        )
        
        # Log status delivery per channel
        for channel, status in results.items():
            if status.get("success"):
                logger.info(f"Alert terkirim via {channel}.")
            else:
                logger.error(f"Gagal mengirim alert via {channel}: {status.get('message')}")

def run_cycle(logger, config_data):
    """
    Mengeksekusi satu alur penuh pengumpulan data, evaluasi, dan pengiriman.
    """
    logger.info("Memulai siklus tunggal VPS Pulse V1...")

    # 1. Tentukan parameter runtime
    top_n = config_data.get("top_process_count", 5)
    notif_mode = config_data.get("notification_mode", "cli")
    tg_token = config_data.get("telegram_token", "")
    tg_chat_id = config_data.get("telegram_chat_id", "")
    
    # Log parameter untuk audit
    logger.info(f"Runtime Parameter -> Top N: {top_n}, Mode: {notif_mode}")

    # 2. Collect System Metrics
    logger.info("Mengumpulkan system metrics...")
    sys_metrics = collect_system_metrics(logger=logger)

    # 3. Collect Process Metrics
    logger.info(f"Mengumpulkan process metrics...")
    proc_metrics = collect_process_metrics(logger=logger, top_n=top_n)

    # 4. Format Daily Report
    logger.info("Menyusun daily report...")
    daily_report = format_daily_report(system_metrics=sys_metrics, process_metrics=proc_metrics)

    # 5. Evaluate Alerts
    logger.info("Mengevaluasi threshold alerts...")
    alerts = evaluate_alerts(metrics=sys_metrics, thresholds=config_data, logger=logger)

    # 6. Kirim Daily Report via Notifier
    logger.info(f"Mengirim daily report via mode: {notif_mode}...")
    report_results = dispatch_notification(
        message=daily_report,
        mode=notif_mode,
        telegram_token=tg_token,
        telegram_chat_id=tg_chat_id,
        logger=logger
    )
    
    # Log status delivery report per channel
    for channel, status in report_results.items():
        if status.get("success"):
            logger.info(f"Daily report berhasil dikirim via {channel}.")
        else:
            logger.error(f"Daily report gagal dikirim via {channel}: {status.get('message')}")

    # 7. Kirim Alerts (Jika ada)
    _dispatch_alerts(alerts, notif_mode, tg_token, tg_chat_id, logger)

    logger.info("Siklus selesai dengan sukses.")

def main():
    # Setup Fondasi
    logger = setup_logger(name="vps_pulse_main")
    logger.info("Starting VPS Pulse V1 Orchestrator...")

    # Load Config
    config_data, config_errors = load_config()
    for err in config_errors:
        logger.warning(f"Config issue: {err}")

    # Mode eksekusi tunggal (One-off run)
    logger.info("Menjalankan mode one-off.")
    try:
        run_cycle(logger, config_data)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Terjadi kesalahan fatal pada orchestrator: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

