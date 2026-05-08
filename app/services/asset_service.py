# app/services/asset_service.py
# Tanggung jawab: semua logika bisnis asset.
# File ini TIDAK boleh pakai input() atau print() —
# hanya terima data, proses, return hasil.

import json
import csv
import os
import shutil
from datetime import datetime
from collections import Counter
from typing import Optional

from config import (
    DATA_FILE, LOG_FILE, BACKUP_DIR,
    MAX_BACKUP, LOG_MAX_LINES
)
from app.models.asset import Asset


# ── Storage ───────────────────────────────────────

def load_assets() -> list:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_assets(assets: list) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)


def write_log(action: str, detail: str) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {detail}\n")


def backup_data() -> None:
    if not os.path.exists(DATA_FILE):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"assets_{timestamp}.json")
    shutil.copy(DATA_FILE, backup_path)
    semua_backup = sorted(os.listdir(BACKUP_DIR))
    if len(semua_backup) > MAX_BACKUP:
        for nama_file in semua_backup[:-MAX_BACKUP]:
            os.remove(os.path.join(BACKUP_DIR, nama_file))


# ── CRUD ──────────────────────────────────────────

def tambah_asset(data: dict) -> Asset:
    """
    Terima dictionary data, buat Asset, simpan.
    Return objek Asset yang baru dibuat.
    """
    asset  = Asset(**data)
    assets = load_assets()
    assets.append(asset.to_dict())
    backup_data()
    save_assets(assets)
    write_log("ADD", f"Asset '{asset.name}' (ID: {asset.id}) ditambahkan")
    return asset


def get_semua_asset() -> list:
    """Return semua asset sebagai list of dict."""
    return load_assets()


def get_asset_by_id(asset_id: str) -> Optional[dict]:
    """Cari satu asset berdasarkan ID. Return None kalau tidak ketemu."""
    assets = load_assets()
    return next((a for a in assets if a["id"] == asset_id), None)


def update_asset(asset_id: str, perubahan: dict) -> Optional[dict]:
    """
    Update field yang ada di dictionary perubahan.
    Return asset yang sudah diupdate, atau None kalau tidak ketemu.
    """
    assets = load_assets()
    target = next((a for a in assets if a["id"] == asset_id), None)
    if target is None:
        return None

    old_name = target["name"]

    # hanya update field yang ada di perubahan
    for key, value in perubahan.items():
        if value is not None:
            target[key] = value

    target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    backup_data()
    save_assets(assets)
    write_log("EDIT", f"Asset '{old_name}' (ID: {asset_id}) diperbarui")
    return target


def hapus_asset(asset_id: str) -> Optional[dict]:
    """
    Hapus asset berdasarkan ID.
    Return asset yang dihapus, atau None kalau tidak ketemu.
    """
    assets = load_assets()
    target = next((a for a in assets if a["id"] == asset_id), None)
    if target is None:
        return None

    assets = [a for a in assets if a["id"] != asset_id]
    backup_data()
    save_assets(assets)
    write_log("DELETE", f"Asset '{target['name']}' (ID: {asset_id}) dihapus")
    return target


# ── Query & Filter ────────────────────────────────

def cari_asset(keyword: str) -> list:
    """Cari asset berdasarkan keyword di beberapa field."""
    keyword = keyword.lower()
    assets  = load_assets()
    return [
        a for a in assets
        if keyword in a["name"].lower()
        or keyword in a["type"].lower()
        or keyword in a["location"].lower()
        or keyword in a["pic"].lower()
        or keyword in a.get("serial", "").lower()
    ]


def filter_asset(key: str, nilai_list: list) -> list:
    """Filter asset berdasarkan key dan list nilai."""
    assets = load_assets()
    return [a for a in assets if a.get(key) in nilai_list]


def get_statistik() -> dict:
    """Return dictionary berisi statistik asset."""
    assets = load_assets()
    if not assets:
        return {}

    hitung_status = Counter(a["status"] for a in assets)
    hitung_lokasi = Counter(a["location"] for a in assets)
    lokasi_teratas = hitung_lokasi.most_common(1)[0]

    return {
        "total":          len(assets),
        "per_status":     dict(hitung_status),
        "lokasi_teratas": lokasi_teratas[0],
        "lokasi_jumlah":  lokasi_teratas[1],
    }


def get_asset_tua(batas_tahun: int) -> list:
    """Return list asset yang umurnya melebihi batas_tahun."""
    assets = load_assets()
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
    """Return n baris terakhir dari log."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-n:]]


# ── Export & Import ───────────────────────────────

def export_ke_csv(export_dir: str) -> str:
    """
    Export semua asset ke CSV.
    Return path file yang dibuat.
    """
    assets   = load_assets()
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
    """
    Import asset dari file CSV.
    Return dict berisi list berhasil dan list gagal.
    """
    KOLOM_WAJIB     = ["name", "type", "location", "pic"]
    assets_sekarang = load_assets()
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

            asset = Asset(
                name          = nama,
                asset_type    = safe(baris.get("type"), "Lainnya"),
                brand         = safe(baris.get("brand")),
                serial        = safe(baris.get("serial")),
                purchase_date = safe(baris.get("purchase_date")),
                location      = safe(baris.get("location")),
                pic           = safe(baris.get("pic")),
                notes         = safe(baris.get("notes")),
                status        = safe(baris.get("status"), "Aktif"),
            )
            berhasil.append(asset.to_dict())
            nama_csv.add(nama.lower())

    if berhasil:
        assets_sekarang.extend(berhasil)
        backup_data()
        save_assets(assets_sekarang)
        write_log("IMPORT", f"{len(berhasil)} asset diimport dari '{path}'")

    return {"berhasil": berhasil, "gagal": gagal}