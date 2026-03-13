import logging
import sys
from pathlib import Path

def setup_logger(name="vps_pulse", log_file_path=None, level=logging.INFO):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(level)
        logger.propagate = False 

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(module)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if not log_file_path:
            base_dir = Path(__file__).resolve().parent.parent
            log_file_path = base_dir / "logs" / "vps_pulse.log"

        try:
            path = Path(log_file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Gagal membuat file log di {log_file_path}: {e}. Berjalan dengan console only.")

    return logger

