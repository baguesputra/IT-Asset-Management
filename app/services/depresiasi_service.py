# app/services/depresiasi_service.py
# Kalkulasi depresiasi asset IT metode garis lurus.

from datetime import date, datetime
from typing import Optional
from app.services.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("depresiasi")

# Umur ekonomis default (tahun) per jenis asset
UMUR_EKONOMIS = {
    "PC":      4,
    "Laptop":  4,
    "Printer": 4,
    "UPS":     4,
    "Monitor": 5,
    "CCTV":    5,
    "Switch":  5,
    "Router":  5,
    "Server":  5,
    "Lainnya": 4,
}

# Nilai sisa = persentase dari harga beli
PERSEN_NILAI_SISA = 0.10   # 10%


def hitung_depresiasi(asset: dict) -> Optional[dict]:
    """
    Hitung depresiasi satu asset.

    Return None kalau data tidak cukup
    (tidak ada harga beli atau tanggal pembelian).

    Return dict berisi:
        harga_beli         : harga saat dibeli
        nilai_sisa         : nilai minimum (10% harga beli)
        umur_ekonomis      : umur ekonomis dalam tahun
        depresiasi_per_thn : penurunan nilai per tahun
        umur_sekarang      : umur asset saat ini (tahun, desimal)
        nilai_sekarang     : nilai saat ini
        persen_tersisa     : persentase nilai yang tersisa
        sudah_habis        : True kalau sudah melewati umur ekonomis
    """
    harga_beli    = asset.get("harga_beli") or 0
    purchase_date = asset.get("purchase_date") or ""
    jenis         = asset.get("type", "Lainnya")

    # tidak bisa hitung kalau tidak ada harga atau tanggal
    if not harga_beli or not purchase_date:
        return None

    try:
        tgl_beli = datetime.strptime(
            purchase_date, "%Y-%m-%d"
        ).date()
    except ValueError:
        return None

    # umur ekonomis — dari konstanta, default 4 tahun
    umur_ekonomis = UMUR_EKONOMIS.get(jenis, 4)

    # nilai sisa = 10% dari harga beli
    nilai_sisa = int(harga_beli * PERSEN_NILAI_SISA)

    # depresiasi per tahun
    depresiasi_per_thn = (harga_beli - nilai_sisa) / umur_ekonomis

    # umur asset sekarang dalam tahun (desimal)
    hari_ini      = date.today()
    selisih_hari  = (hari_ini - tgl_beli).days
    umur_sekarang = selisih_hari / 365.25

    # nilai sekarang
    # kalau sudah melewati umur ekonomis → nilai sisa
    if umur_sekarang >= umur_ekonomis:
        nilai_sekarang = nilai_sisa
        sudah_habis    = True
    else:
        nilai_sekarang = harga_beli - (depresiasi_per_thn * umur_sekarang)
        nilai_sekarang = max(int(nilai_sekarang), nilai_sisa)
        sudah_habis    = False

    # persentase nilai yang masih tersisa
    persen_tersisa = (nilai_sekarang / harga_beli * 100) if harga_beli else 0

    return {
        "harga_beli":         harga_beli,
        "nilai_sisa":         nilai_sisa,
        "umur_ekonomis":      umur_ekonomis,
        "depresiasi_per_thn": int(depresiasi_per_thn),
        "umur_sekarang":      round(umur_sekarang, 1),
        "nilai_sekarang":     int(nilai_sekarang),
        "persen_tersisa":     round(persen_tersisa, 1),
        "sudah_habis":        sudah_habis,
    }


def get_semua_dengan_depresiasi() -> list:
    """
    Ambil semua asset yang punya data harga beli.
    Tambahkan info depresiasi yang dihitung.
    """
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT * FROM assets
        WHERE harga_beli > 0
        AND purchase_date IS NOT NULL
        AND purchase_date != ''
        ORDER BY purchase_date ASC
    """)
    assets = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # tambahkan kalkulasi depresiasi
    for a in assets:
        a["depresiasi"] = hitung_depresiasi(a)

    return assets


def get_statistik_depresiasi() -> dict:
    """
    Statistik ringkas untuk dashboard depresiasi.

    Return:
        total_harga_beli  : total harga beli semua asset
        total_nilai_skrg  : total nilai sekarang semua asset
        total_susut       : total nilai yang sudah susut
        jumlah_habis      : asset yang sudah habis umur ekonomis
        jumlah_data       : asset yang punya data depresiasi
    """
    assets = get_semua_dengan_depresiasi()

    total_harga_beli = sum(
        a["harga_beli"] for a in assets
        if a["depresiasi"]
    )
    total_nilai_skrg = sum(
        a["depresiasi"]["nilai_sekarang"] for a in assets
        if a["depresiasi"]
    )
    jumlah_habis = sum(
        1 for a in assets
        if a["depresiasi"] and a["depresiasi"]["sudah_habis"]
    )

    return {
        "total_harga_beli": total_harga_beli,
        "total_nilai_skrg": total_nilai_skrg,
        "total_susut":      total_harga_beli - total_nilai_skrg,
        "jumlah_habis":     jumlah_habis,
        "jumlah_data":      len(assets),
        "persen_tersisa":   round(
            total_nilai_skrg / total_harga_beli * 100
            if total_harga_beli else 0, 1
        ),
    }


def get_proyeksi_penggantian() -> list:
    """
    Asset yang sudah habis atau akan habis umur ekonomisnya
    dalam 1 tahun ke depan — untuk perencanaan anggaran.
    """
    assets = get_semua_dengan_depresiasi()
    hasil  = []

    for a in assets:
        dep = a.get("depresiasi")
        if not dep:
            continue

        sisa_tahun = dep["umur_ekonomis"] - dep["umur_sekarang"]

        # sudah habis atau akan habis dalam 1 tahun
        if sisa_tahun <= 1:
            a["sisa_tahun"] = round(sisa_tahun, 1)
            hasil.append(a)

    # urutkan dari yang paling perlu diganti
    return sorted(hasil, key=lambda x: x["sisa_tahun"])