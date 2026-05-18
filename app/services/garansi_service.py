# app/services/garansi_service.py
# Logika bisnis untuk tracking garansi asset.

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional
from app.services.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("garansi")


def hitung_tgl_berakhir(tgl_mulai: str,
                         masa_bulan: int) -> Optional[str]:
    """
    Hitung tanggal berakhir garansi.
    Pakai relativedelta supaya perhitungan bulan akurat.

    Contoh:
        tgl_mulai  = "2024-01-15"
        masa_bulan = 12
        hasil      = "2025-01-15"
    """
    if not tgl_mulai or not masa_bulan:
        return None
    try:
        tgl = datetime.strptime(tgl_mulai, "%Y-%m-%d").date()
        tgl_berakhir = tgl + relativedelta(months=masa_bulan)
        return tgl_berakhir.strftime("%Y-%m-%d")
    except ValueError:
        return None


def hitung_status_garansi(tgl_berakhir: str) -> dict:
    """
    Hitung status garansi berdasarkan tanggal berakhir.

    Return dict:
        status  : "Aktif" / "Mau Habis" / "Habis" / "Tidak Ada"
        sisa    : jumlah hari tersisa (negatif kalau sudah habis)
        label   : teks untuk ditampilkan
        warna   : warna Bootstrap untuk badge
    """
    if not tgl_berakhir:
        return {
            "status": "Tidak Ada",
            "sisa":   None,
            "label":  "Tidak Ada Garansi",
            "warna":  "secondary",
        }

    try:
        tgl    = datetime.strptime(tgl_berakhir, "%Y-%m-%d").date()
        hari_ini = date.today()
        sisa   = (tgl - hari_ini).days

        if sisa < 0:
            return {
                "status": "Habis",
                "sisa":   sisa,
                "label":  f"Habis {abs(sisa)} hari lalu",
                "warna":  "danger",
            }
        elif sisa <= 30:
            return {
                "status": "Mau Habis",
                "sisa":   sisa,
                "label":  f"Habis {sisa} hari lagi",
                "warna":  "warning",
            }
        else:
            return {
                "status": "Aktif",
                "sisa":   sisa,
                "label":  f"Aktif ({sisa} hari)",
                "warna":  "success",
            }
    except ValueError:
        return {
            "status": "Tidak Ada",
            "sisa":   None,
            "label":  "Format tanggal salah",
            "warna":  "secondary",
        }


def get_semua_dengan_garansi() -> list:
    """
    Ambil semua asset yang punya data garansi.
    Tambahkan info status garansi yang dihitung.
    """
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT * FROM assets
        WHERE masa_garansi_bulan > 0
        AND tgl_garansi_mulai IS NOT NULL
        AND tgl_garansi_mulai != ''
        ORDER BY tgl_garansi_mulai ASC
    """)
    assets = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # tambahkan info garansi yang dihitung
    for a in assets:
        tgl_berakhir = hitung_tgl_berakhir(
            a["tgl_garansi_mulai"],
            a["masa_garansi_bulan"]
        )
        a["tgl_garansi_berakhir"] = tgl_berakhir
        a["info_garansi"]         = hitung_status_garansi(
            tgl_berakhir
        )

    return assets


def get_garansi_mau_habis(hari: int = 30) -> list:
    """
    Ambil asset yang garansinya akan habis dalam N hari.
    Default 30 hari.
    """
    semua = get_semua_dengan_garansi()
    return [
        a for a in semua
        if a["info_garansi"]["status"] in ["Mau Habis", "Habis"]
        or (
            a["info_garansi"]["sisa"] is not None
            and 0 <= a["info_garansi"]["sisa"] <= hari
        )
    ]


def get_statistik_garansi() -> dict:
    """Statistik ringkas status garansi semua asset."""
    semua = get_semua_dengan_garansi()

    aktif     = sum(1 for a in semua if a["info_garansi"]["status"] == "Aktif")
    mau_habis = sum(1 for a in semua if a["info_garansi"]["status"] == "Mau Habis")
    habis     = sum(1 for a in semua if a["info_garansi"]["status"] == "Habis")
    tidak_ada = len([]) # hitung asset tanpa garansi

    # hitung asset tanpa garansi
    conn      = get_connection()
    total_all = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    conn.close()
    tidak_ada = total_all - len(semua)

    return {
        "aktif":     aktif,
        "mau_habis": mau_habis,
        "habis":     habis,
        "tidak_ada": tidak_ada,
        "total":     total_all,
    }