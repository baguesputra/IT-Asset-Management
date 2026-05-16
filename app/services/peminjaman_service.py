# app/services/peminjaman_service.py
# Logika bisnis untuk modul peminjaman asset.

from datetime import datetime
from typing import Optional
from app.services.database import get_connection
from app.services.asset_service import write_log, update_asset
from app.utils.logger import get_logger

logger = get_logger("peminjaman")

# unit / departemen RS
UNIT_RS = [
    "IGD", "Poli Umum", "Poli Spesialis",
    "Radiologi", "Laboratorium", "Farmasi",
    "Kamar Operasi", "ICU", "Rawat Inap",
    "Administrasi", "Keuangan", "HRD",
    "IT", "Manajemen", "Lainnya"
]


def catat_peminjaman(asset_id: str, data: dict,
                     dicatat_oleh: str) -> Optional[dict]:
    """
    Catat peminjaman asset baru.
    Otomatis update status asset jadi 'Dipinjam'.
    Return data peminjaman yang baru dibuat.
    """
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO peminjaman (
                asset_id, nama_peminjam, unit_peminjam,
                tanggal_pinjam, tanggal_rencana_kembali,
                keperluan, status, dicatat_oleh, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'Dipinjam', ?, ?)
        """, (
            asset_id,
            data["nama_peminjam"],
            data["unit_peminjam"],
            data["tanggal_pinjam"],
            data["tanggal_rencana_kembali"],
            data.get("keperluan", ""),
            dicatat_oleh,
            now,
        ))

        peminjaman_id = cursor.lastrowid
        conn.commit()

        # update status asset jadi Dipinjam
        update_asset(asset_id, {"status": "Dipinjam"})

        write_log(
            "PINJAM",
            f"Asset {asset_id} dipinjam oleh "
            f"{data['nama_peminjam']} ({data['unit_peminjam']})"
        )

        logger.info(
            "Peminjaman baru: asset=%s peminjam=%s",
            asset_id, data["nama_peminjam"]
        )

        return get_peminjaman_by_id(peminjaman_id)

    except Exception as e:
        logger.error("Gagal catat peminjaman: %s", str(e))
        conn.rollback()
        return None
    finally:
        conn.close()


def konfirmasi_kembali(peminjaman_id: int,
                       dicatat_oleh: str) -> Optional[dict]:
    """
    Konfirmasi asset sudah dikembalikan.
    Otomatis update status asset kembali jadi 'Aktif'.
    """
    peminjaman = get_peminjaman_by_id(peminjaman_id)
    if peminjaman is None:
        return None

    if peminjaman["status"] == "Sudah Kembali":
        return peminjaman   # sudah dikembalikan sebelumnya

    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tgl  = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()

    try:
        conn.execute("""
            UPDATE peminjaman
            SET status          = 'Sudah Kembali',
                tanggal_kembali = ?
            WHERE id = ?
        """, (tgl, peminjaman_id))
        conn.commit()

        # update status asset kembali jadi Aktif
        update_asset(peminjaman["asset_id"], {"status": "Aktif"})

        write_log(
            "KEMBALI",
            f"Asset {peminjaman['asset_id']} dikembalikan oleh "
            f"{peminjaman['nama_peminjam']}"
        )

        logger.info(
            "Asset dikembalikan: peminjaman_id=%s asset=%s",
            peminjaman_id, peminjaman["asset_id"]
        )

        return get_peminjaman_by_id(peminjaman_id)

    except Exception as e:
        logger.error("Gagal konfirmasi kembali: %s", str(e))
        conn.rollback()
        return None
    finally:
        conn.close()


def get_peminjaman_by_id(peminjaman_id: int) -> Optional[dict]:
    """Ambil satu data peminjaman berdasarkan ID."""
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT p.*, a.name as asset_name, a.type as asset_type
        FROM peminjaman p
        JOIN assets a ON p.asset_id = a.id
        WHERE p.id = ?
    """, (peminjaman_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_peminjaman_aktif() -> list:
    """
    Ambil semua peminjaman yang statusnya masih 'Dipinjam'.
    Tandai yang sudah terlambat dikembalikan.
    """
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT p.*, a.name as asset_name,
               a.type as asset_type,
               a.location as asset_location
        FROM peminjaman p
        JOIN assets a ON p.asset_id = a.id
        WHERE p.status = 'Dipinjam'
        ORDER BY p.tanggal_rencana_kembali ASC
    """)
    hasil = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # tandai yang terlambat
    hari_ini = datetime.now().date()
    for p in hasil:
        tgl_rencana    = datetime.strptime(
            p["tanggal_rencana_kembali"], "%Y-%m-%d"
        ).date()
        p["terlambat"] = tgl_rencana < hari_ini
        p["hari_sisa"] = (tgl_rencana - hari_ini).days

    return hasil


def get_peminjaman_by_asset(asset_id: str) -> list:
    """Ambil semua riwayat peminjaman untuk satu asset."""
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT * FROM peminjaman
        WHERE asset_id = ?
        ORDER BY tanggal_pinjam DESC
    """, (asset_id,))
    hasil = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hasil


def get_statistik_peminjaman() -> dict:
    """Statistik ringkas untuk dashboard."""
    conn = get_connection()

    aktif = conn.execute("""
        SELECT COUNT(*) FROM peminjaman
        WHERE status = 'Dipinjam'
    """).fetchone()[0]

    terlambat = conn.execute("""
        SELECT COUNT(*) FROM peminjaman
        WHERE status = 'Dipinjam'
        AND tanggal_rencana_kembali < date('now')
    """).fetchone()[0]

    total = conn.execute(
        "SELECT COUNT(*) FROM peminjaman"
    ).fetchone()[0]

    conn.close()

    return {
        "aktif":     aktif,
        "terlambat": terlambat,
        "total":     total,
    }