# app/services/database.py
# Tanggung jawab: koneksi dan inisialisasi database SQLite.
# File ini yang "tahu" tentang database —
# service lain tidak boleh buat koneksi sendiri.

import sqlite3
import os
from config import BASE_DIR

# path file database
DB_FILE = os.path.join(BASE_DIR, "data", "assets.db")


def get_connection() -> sqlite3.Connection:
    """
    Buat dan return koneksi ke database.
    
    row_factory = sqlite3.Row membuat hasil query bisa
    diakses seperti dictionary: row["name"] bukan row[0]
    """
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row   # ← ini penting
    # aktifkan foreign key — penting untuk relasi antar tabel
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Buat tabel kalau belum ada.
    Dipanggil sekali saat aplikasi pertama jalan.
    
    IF NOT EXISTS → tidak error kalau tabel sudah ada
    TEXT          → tipe data string di SQLite
    """
    conn = get_connection()

    # cursor = "pena" untuk menulis perintah SQL
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id            TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            type          TEXT NOT NULL,
            brand         TEXT,
            serial        TEXT,
            purchase_date TEXT,
            location      TEXT NOT NULL,
            pic           TEXT NOT NULL,
            notes         TEXT,
            status        TEXT DEFAULT 'Aktif',
            created_at    TEXT,
            updated_at    TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT NOT NULL,
            action     TEXT NOT NULL,
            detail     TEXT NOT NULL
        )
    """)

    # tabel baru — riwayat servis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servis (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id    TEXT NOT NULL,
            tanggal     TEXT NOT NULL,
            jenis       TEXT NOT NULL,
            deskripsi   TEXT NOT NULL,
            teknisi     TEXT NOT NULL,
            biaya       INTEGER DEFAULT 0,
            created_at  TEXT NOT NULL,

            -- foreign key — asset_id harus ada di tabel assets
            FOREIGN KEY (asset_id) REFERENCES assets(id)
        )
    """)

    # commit = simpan perubahan ke file
    conn.commit()

    # selalu tutup koneksi setelah selesai
    conn.close()