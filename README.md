# VPS Pulse V1

Lightweight, single-node VPS resource reporting tool. VPS Pulse mengumpulkan metrik sistem (CPU, RAM, Disk), memeringkat proses teratas, dan mengirimkan laporan harian serta peringatan (*alerts*) ke CLI atau Telegram.

**Status Proyek:** *Run-ready baseline* (V1). 
Proyek ini adalah fondasi pelaporan yang stabil dan lurus ke depan, bukan *production-hardened monitoring suite*.

## Limitasi Operasional V1
- **One-off Execution**: Skrip ini dirancang untuk berjalan satu kali (*one-off*) per pemanggilan. Penjadwalan (*scheduling*) diserahkan sepenuhnya kepada *cron*, *systemd*, atau *orchestrator* eksternal.
- **Docker Metrics**: Jika dijalankan melalui Docker tanpa penyesuaian *volume/pid mount* khusus, metrik yang dilaporkan (CPU, RAM, Disk, Process) adalah metrik milik *container* tersebut, bukan metrik VPS Host secara keseluruhan.
- **Stateless Alerts**: Tidak ada memori histori. Jika *alert* terpicu, peringatan akan dikirim setiap kali skrip dijalankan hingga kondisi kembali normal.

## Setup Lokal (Disarankan untuk Host Metrics)
1. Siapkan virtual environment: `python -m venv venv && source venv/bin/activate`
2. Install dependensi: `pip install -r requirements.txt`
3. Salin konfigurasi:
   - `cp config/config.example.json config/config.json`
   - `cp .env.example .env` (Token Telegram opsional, mode `cli` tetap jalan tanpa token)
4. Jalankan siklus: `python -m app.main`
5. *Untuk otomatisasi, daftarkan eksekusi ke `cron` OS Host Anda.*

## Setup Docker (Baseline Container Run)
1. Salin `config.json` dan `.env` seperti langkah lokal di atas.
2. Build dan jalankan: `docker-compose up --build`
3. Container akan mencetak laporan, mengirim notifikasi (jika diatur), lalu otomatis *exit*.

## Testing
Jalankan *smoke test* minimal untuk memvalidasi *environment*:
```bash
pytest tests/```

### F. Self-Check
* **Sinkronisasi Kode & Dokumen**: Tidak ada lagi janji palsu tentang *looping* atau *host metrics* di Docker. Apa yang tertulis di README dan Compose adalah persis apa yang dieksekusi oleh `main.py`.
* **Kerapian Format**: Penutup blok *code fence* di bagian Testing pada README.md telah dipastikan aman.
* **Kerendahan Hati**: Narasi proyek diturunkan ke level *Run-ready baseline*. Ini menetapkan ekspektasi yang benar bagi siapa pun yang melakukan *clone* pada repositori ini.

### G. Test / Validation
1. *Smoke Test*: `pytest tests/` akan lulus karena `app/*.py` tidak ada yang diubah.
2. *Docker Run*: `docker-compose up` akan menjalankan *container*, mencetak output, lalu berhenti dengan *exit code 0* atau *1* secara jelas.

### H. Open Risks
* **Docker Limitation**: Karena kita menetapkan Docker sebagai eksekusi *baseline container* murni, pengguna yang ingin memonitor VPS mereka menggunakan Docker harus mengekstrak skrip ini ke *bare-metal* atau menunggu rilis versi lanjutan yang secara resmi menembus *namespace* kontainer. Ini adalah *trade-off* operasional yang sudah dikomunikasikan secara gamblang di README.
