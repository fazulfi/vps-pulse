import requests

def send_cli_notification(message, logger=None):
    """
    Mengirimkan pesan/laporan ke Command Line Interface (CLI).
    """
    if logger:
        logger.info("Mengirim notifikasi via CLI.")
    
    # Cetak ke terminal dengan spasi wajar
    print(f"\n{message}")
    
    return True, "Berhasil dicetak ke CLI"

def send_telegram_notification(message, token, chat_id, logger=None):
    """
    Mengirimkan pesan/laporan ke Telegram.
    Membaca body JSON untuk memastikan status pengiriman.
    """
    if not token or not chat_id:
        err_msg = "Telegram token atau chat_id kosong. Pengiriman dibatalkan."
        if logger:
            logger.warning(err_msg)
        return False, err_msg
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": str(chat_id),
        "text": message
    }
    
    try:
        # Timeout 10 detik untuk mencegah aplikasi hang
        response = requests.post(url, json=payload, timeout=10.0)
        
        # Ekstrak JSON body dari Telegram
        data = response.json()
        
        if not data.get("ok"):
            # Telegram secara eksplisit menolak request (misal chat_id salah)
            tg_error = data.get("description", "Unknown Telegram API Error")
            err_msg = f"Telegram API menolak pengiriman: {tg_error}"
            if logger:
                logger.error(err_msg)
            return False, err_msg
            
        if logger:
            logger.info("Notifikasi Telegram berhasil dikirim.")
        return True, "Berhasil dikirim ke Telegram"
        
    except requests.exceptions.RequestException as e:
        # Menangkap error jaringan level bawah (Timeout, Connection Refused, dll)
        err_msg = f"Kegagalan jaringan saat menghubungi Telegram: {e}"
        if logger:
            logger.error(err_msg)
        return False, err_msg
    except ValueError:
        # Menangkap kasus di mana respons dari server bukan JSON yang valid
        err_msg = f"Gagal membaca respons dari Telegram (Status: {response.status_code})"
        if logger:
            logger.error(err_msg)
        return False, err_msg

def dispatch_notification(message, mode="cli", telegram_token=None, telegram_chat_id=None, logger=None):
    """
    Dispatcher utama untuk merutekan pesan ke channel yang sesuai.
    
    Mengembalikan:
        dict: Status pengiriman per channel, contoh:
              {"cli": {"success": True, "message": "Berhasil dicetak ke CLI"}}
    """
    results = {}
    
    # 1. Validasi pesan kosong
    if not message or not str(message).strip():
        err_msg = "Pesan kosong. Notifikasi dibatalkan."
        if logger:
            logger.warning(err_msg)
        return {"all": {"success": False, "message": err_msg}}
    
    # 2. Validasi mode
    safe_mode = str(mode).lower()
    if safe_mode not in ["cli", "telegram", "both"]:
        if logger:
            logger.warning(f"Mode notifikasi '{safe_mode}' tidak dikenal. Fallback ke 'cli'.")
        safe_mode = "cli"
        
    # 3. Rute CLI
    if safe_mode in ["cli", "both"]:
        success, msg = send_cli_notification(message, logger)
        results["cli"] = {"success": success, "message": msg}
        
    # 4. Rute Telegram
    if safe_mode in ["telegram", "both"]:
        success, msg = send_telegram_notification(message, telegram_token, telegram_chat_id, logger)
        results["telegram"] = {"success": success, "message": msg}
        
    return results

