# config.py
# Semua konfigurasi project dikumpulkan di sini.
# Nilai sensitif dibaca dari .env — tidak hardcode.

import os
from dotenv import load_dotenv

# load_dotenv() membaca file .env dan memasukkan
# isinya ke environment variable Python
load_dotenv()

# ── Path ──────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
LOG_DIR    = os.path.join(BASE_DIR, "logs")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# ── Informasi RS ──────────────────────────────────
# Dibaca dari .env — berbeda tiap instalasi RS
RS_NAMA   = os.getenv("RS_NAMA", "Nama Rumah Sakit")
RS_ALAMAT = os.getenv("RS_ALAMAT", "Alamat Rumah Sakit")

# ── Flask ─────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-ganti-ini-di-production")
FLASK_ENV  = os.getenv("FLASK_ENV", "development")
DEBUG      = FLASK_ENV == "development"

# ── Database ──────────────────────────────────────
DB_NAME = os.getenv("DB_NAME", "assets.db")

# ── Setting aplikasi ──────────────────────────────
LOG_MAX_LINES = 20
MAX_BACKUP    = 10

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