# app/services/servis_service.py
# Logika bisnis untuk riwayat servis asset.

from datetime import datetime
from typing import Optional
from app.services.database import get_connection
from app.services.asset_service import write_log

# jenis servis yang tersedia
JENIS_SERVIS = [
    "Servis Rutin",
    "Perbaikan Hardware",
    "Perbaikan Software",
    "Upgrade Komponen",
    "Instalasi Ulang",
    "Penggantian Unit",
    "Lainnya",
]


def tambah_servis(asset_id: str, data: dict) -> dict:
    """
    Tambah catatan servis baru untuk satu asset.
    Return dictionary servis yang baru dibuat.
    """
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO servis (
            asset_id, tanggal, jenis, deskripsi,
            teknisi, biaya, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        asset_id,
        data["tanggal"],
        data["jenis"],
        data["deskripsi"],
        data["teknisi"],
        data.get("biaya", 0),
        now,
    ))

    # lastrowid = ID yang baru dibuat (AUTOINCREMENT)
    servis_id = cursor.lastrowid
    conn.commit()
    conn.close()

    write_log(
        "SERVIS",
        f"Servis baru untuk asset {asset_id}: {data['jenis']}"
    )

    return get_servis_by_id(servis_id)


def get_servis_by_asset(asset_id: str) -> list:
    """
    Ambil semua riwayat servis untuk satu asset.
    Diurutkan dari yang terbaru.
    """
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT * FROM servis
        WHERE asset_id = ?
        ORDER BY tanggal DESC, id DESC
    """, (asset_id,))

    hasil = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hasil


def get_servis_by_id(servis_id: int) -> Optional[dict]:
    """Ambil satu catatan servis berdasarkan ID."""
    conn   = get_connection()
    cursor = conn.execute(
        "SELECT * FROM servis WHERE id = ?",
        (servis_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def hapus_servis(servis_id: int) -> bool:
    """
    Hapus satu catatan servis.
    Return True kalau berhasil, False kalau tidak ketemu.
    """
    if not get_servis_by_id(servis_id):
        return False

    conn = get_connection()
    conn.execute("DELETE FROM servis WHERE id = ?", (servis_id,))
    conn.commit()
    conn.close()
    return True


def get_total_biaya(asset_id: str) -> int:
    """Hitung total biaya servis untuk satu asset."""
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT COALESCE(SUM(biaya), 0) as total
        FROM servis
        WHERE asset_id = ?
    """, (asset_id,))

    # COALESCE(SUM(biaya), 0) → kalau tidak ada data, return 0
    # tanpa COALESCE, SUM dari tabel kosong return NULL
    total = cursor.fetchone()["total"]
    conn.close()
    return total


def get_semua_servis_recent(limit: int = 10) -> list:
    """
    Ambil servis terbaru dari semua asset.
    Pakai JOIN untuk gabungkan data dari dua tabel.
    """
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT
            s.*,
            a.name as asset_name,
            a.location as asset_location
        FROM servis s
        JOIN assets a ON s.asset_id = a.id
        ORDER BY s.tanggal DESC, s.id DESC
        LIMIT ?
    """, (limit,))

    hasil = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hasil