import sys
from pathlib import Path

# Memastikan direktori root masuk dalam sys.path untuk absolute import 'app.x'
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_core_imports():
    """Memastikan seluruh modul inti bebas dari syntax error dan circular import."""
    try:
        import app.config
        import app.logger
        import app.collector
        import app.process_collector
        import app.formatter
        import app.notifier
        import app.alerts
        import app.main
        assert True
    except ImportError as e:
        assert False, f"Gagal mengimpor modul inti: {e}"

def test_formatter_pure_functions():
    """Memastikan helper murni berfungsi dengan benar tanpa efek samping."""
    from app.formatter import _format_bytes
    assert _format_bytes(1024) == "1.00 KB"
    assert _format_bytes(None) == "0.00 B"

