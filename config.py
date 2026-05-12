# Config.py
# Semua konfigurasi dan pengaturan untuk aplikasi Asset Manager ada di sini.
# File lain import dari sini — tidak boleh ada path
# yang hardcoded ke file lain.

import os

# ── Path ──────────────────────────────────────────
# os.path.dirname(__file__) = folder tempat config.py berada
# Ini memastikan path selalu benar meski dijalankan
# dari folder manapun
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))

DATA_DIR   = os.path.join(BASE_DIR, "data")
LOG_DIR    = os.path.join(BASE_DIR, "logs")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

DATA_FILE  = os.path.join(DATA_DIR, "assets.json")
LOG_FILE   = os.path.join(LOG_DIR, "activity.log")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# ── Setting ───────────────────────────────────────
MAX_BACKUP    = 10
LOG_MAX_LINES = 20

# ── Pilihan data ──────────────────────────────────
ASSET_TYPES = [
    "PC", "Laptop", "Printer", "CCTV",
    "Switch", "Router", "UPS", "Monitor",
    "Server", "Lainnya"
]

ASSET_STATUS = [
    "Aktif", "Rusak", "Perbaikan",
    "Tidak Aktif", "Dipinjam"
]

LOCATIONS = [
    "Poli Umum", "IGD", "Radiologi", "Lab",
    "Farmasi", "Administrasi", "IT", "Gudang", "Lainnya"
]

# config.py
# tambahkan di bagian bawah
