# app/services/asset_service.py
# Tanggung jawab: semua logika bisnis asset.
# File ini TIDAK boleh pakai input() atau print() —
# hanya terima data, proses, return hasil.

import csv
import os
import shutil
from datetime import datetime
from collections import Counter
from typing import Optional

from config import (
   LOG_MAX_LINES,EXPORT_DIR
)
from app.models.asset import Asset
from app.services.database import get_connection, init_db

# inisialisasi database saat module pertama kali diimport
init_db()

# ── Storage ───────────────────────────────────────

def write_log(action: str, detail: str) -> None:
    """
    Simpan log ke tabel activity_log di database.
    Lebih rapi dari file .log — bisa di-query nanti.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn      = get_connection()

    conn.execute(
        # ? adalah placeholder — nilai diisi dari tuple di bawah
        # JANGAN pernah pakai f-string untuk query SQL
        # karena rentan SQL injection
        "INSERT INTO activity_log (timestamp, action, detail) VALUES (?, ?, ?)",
        (timestamp, action, detail)
    )

    conn.commit()
    conn.close()

# ── CRUD ──────────────────────────────────────────

def tambah_asset(data: dict) -> Asset:
    asset  = Asset(**data)
    conn   = get_connection()

    conn.execute("""
        INSERT INTO assets (
            id, name, type, brand, serial, purchase_date,
            location, pic, notes, status,
            harga_beli, vendor, no_kontrak,
            masa_garansi_bulan, tgl_garansi_mulai,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        asset.id, asset.name, asset.type, asset.brand,
        asset.serial, asset.purchase_date, asset.location,
        asset.pic, asset.notes, asset.status,
        asset.harga_beli, asset.vendor, asset.no_kontrak,
        asset.masa_garansi_bulan, asset.tgl_garansi_mulai,
        asset.created_at, asset.updated_at
    ))

    conn.commit()
    conn.close()
    write_log("ADD", f"Asset '{asset.name}' (ID: {asset.id}) ditambahkan")
    return asset


def get_semua_asset() -> list:
    """Ambil semua asset dari database."""
    conn   = get_connection()
    cursor = conn.execute("SELECT * FROM assets ORDER BY created_at DESC")

    # fetchall() ambil semua baris hasil query
    # dict(row) konversi sqlite3.Row ke dictionary biasa
    assets = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return assets


def get_asset_by_id(asset_id: str) -> Optional[dict]:
    """Cari satu asset berdasarkan ID."""
    conn   = get_connection()
    cursor = conn.execute(
        "SELECT * FROM assets WHERE id = ?",
        (asset_id,)   # ← tuple dengan satu elemen, koma wajib ada
    )

    # fetchone() ambil satu baris saja
    # return None kalau tidak ketemu
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_asset(asset_id: str, perubahan: dict) -> Optional[dict]:
    """Update field yang tidak None di dictionary perubahan."""
    target = get_asset_by_id(asset_id)
    if target is None:
        return None

    old_name = target["name"]

    # bangun query dinamis — hanya update field yang tidak None
    fields = []    # kolom yang akan diupdate
    values = []    # nilai barunya

    for key, value in perubahan.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        return target   # tidak ada yang berubah

    # tambahkan updated_at
    fields.append("updated_at = ?")
    values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # tambahkan id di akhir untuk WHERE clause
    values.append(asset_id)

    # gabungkan: "name = ?, status = ?, updated_at = ?"
    query = f"UPDATE assets SET {', '.join(fields)} WHERE id = ?"

    conn = get_connection()
    conn.execute(query, values)
    conn.commit()
    conn.close()

    write_log("EDIT", f"Asset '{old_name}' (ID: {asset_id}) diperbarui")
    return get_asset_by_id(asset_id)


def hapus_asset(asset_id: str) -> Optional[dict]:
    """Hapus asset berdasarkan ID."""
    target = get_asset_by_id(asset_id)
    if target is None:
        return None

    conn = get_connection()
    conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()

    write_log("DELETE", f"Asset '{target['name']}' (ID: {asset_id}) dihapus")
    return target


# ── Query & Filter ────────────────────────────────

def cari_asset(keyword: str) -> list:
    """Cari asset berdasarkan keyword."""
    k      = f"%{keyword.lower()}%"
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT * FROM assets
        WHERE LOWER(name)     LIKE ?
           OR LOWER(type)     LIKE ?
           OR LOWER(location) LIKE ?
           OR LOWER(pic)      LIKE ?
           OR LOWER(serial)   LIKE ?
        ORDER BY name
    """, (k, k, k, k, k))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def filter_asset(key: str, nilai_list: list) -> list:
    """
    Filter asset berdasarkan key dan beberapa nilai.
    IN (?, ?, ?) = salah satu dari nilai ini.
    """
    # buat placeholder ? sebanyak jumlah nilai
    # ["Aktif", "Rusak"] → "?, ?"
    placeholders = ", ".join("?" * len(nilai_list))

    conn   = get_connection()
    cursor = conn.execute(
        f"SELECT * FROM assets WHERE {key} IN ({placeholders})",
        nilai_list
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_statistik() -> dict:
    """Ambil statistik langsung dari database pakai SQL."""
    conn = get_connection()

    # COUNT(*) hitung jumlah baris
    total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]

    if total == 0:
        conn.close()
        return {}

    # GROUP BY — kelompokkan berdasarkan kolom, hitung tiap kelompok
    cursor = conn.execute("""
        SELECT status, COUNT(*) as jumlah
        FROM assets
        GROUP BY status
    """)
    per_status = {row["status"]: row["jumlah"] for row in cursor.fetchall()}

    cursor = conn.execute("""
        SELECT location, COUNT(*) as jumlah
        FROM assets
        GROUP BY location
        ORDER BY jumlah DESC
        LIMIT 1
    """)
    top = cursor.fetchone()
    conn.close()

    return {
        "total":          total,
        "per_status":     per_status,
        "lokasi_teratas": top["location"] if top else "-",
        "lokasi_jumlah":  top["jumlah"] if top else 0,
    }


def get_asset_tua(batas_tahun: int) -> list:
    """Ambil asset yang umurnya melebihi batas_tahun."""
    assets = get_semua_asset()
    hasil  = []

    for a in assets:
        if not a.get("purchase_date"):
            continue
        tgl_beli   = datetime.strptime(a["purchase_date"], "%Y-%m-%d")
        umur_tahun = (datetime.now() - tgl_beli).days / 365.25
        if umur_tahun > batas_tahun:
            hasil.append({"asset": a, "umur": umur_tahun})

    return sorted(hasil, key=lambda x: x["umur"], reverse=True)


def get_log(n: int = LOG_MAX_LINES) -> list:
    """Ambil n log aktivitas terakhir dari database."""
    conn   = get_connection()
    cursor = conn.execute("""
        SELECT timestamp, action, detail
        FROM activity_log
        ORDER BY id DESC
        LIMIT ?
    """, (n,))

    # format sama seperti file log lama
    logs = [
        f"[{row['timestamp']}] {row['action']}: {row['detail']}"
        for row in cursor.fetchall()
    ]
    conn.close()
    return logs


# ── Export & Import ───────────────────────────────

def export_ke_csv(export_dir: str) -> str:
    assets   = get_semua_asset()    # ← ganti ini
    os.makedirs(export_dir, exist_ok=True)
    filename = os.path.join(
        export_dir,
        f"assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    fieldnames = [
        "id", "name", "type", "brand", "serial",
        "purchase_date", "location", "pic",
        "status", "notes", "created_at", "updated_at"
    ]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assets)

    write_log("EXPORT", f"Data diekspor ke '{filename}' ({len(assets)} asset)")
    return filename


def import_dari_csv(path: str) -> dict:
    KOLOM_WAJIB     = ["name", "type", "location", "pic"]
    assets_sekarang = get_semua_asset()    # ← ganti ini
    nama_existing   = {a["name"].lower() for a in assets_sekarang}
    berhasil        = []
    gagal           = []
    nama_csv        = set()

    def safe(val, default=""):
        return (val or default).strip()

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return {"berhasil": [], "gagal": ["File CSV kosong"]}

        kolom_tidak_ada = [k for k in KOLOM_WAJIB if k not in reader.fieldnames]
        if kolom_tidak_ada:
            return {"berhasil": [], "gagal": [f"Kolom tidak ada: {', '.join(kolom_tidak_ada)}"]}

        for nomor, baris in enumerate(reader, 1):
            if all(v is None for v in baris.values()):
                continue

            nama = (baris.get("name", "") or "").strip()

            if not nama:
                gagal.append(f"Baris {nomor}: nama kosong")
                continue
            if nama.lower() in nama_csv:
                gagal.append(f"Baris {nomor}: '{nama}' duplikat di CSV")
                continue
            if nama.lower() in nama_existing:
                gagal.append(f"Baris {nomor}: '{nama}' sudah ada di data")
                continue

            # langsung simpan ke database lewat tambah_asset
            try:
                tambah_asset({
                    "name":          nama,
                    "asset_type":    safe(baris.get("type"), "Lainnya"),
                    "brand":         safe(baris.get("brand")),
                    "serial":        safe(baris.get("serial")),
                    "purchase_date": safe(baris.get("purchase_date")),
                    "location":      safe(baris.get("location")),
                    "pic":           safe(baris.get("pic")),
                    "notes":         safe(baris.get("notes")),
                    "status":        safe(baris.get("status"), "Aktif"),
                })
                berhasil.append(nama)
                nama_csv.add(nama.lower())
            except Exception as e:
                gagal.append(f"Baris {nomor}: error — {e}")

    return {"berhasil": berhasil, "gagal": gagal}