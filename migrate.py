# migrate.py
# Pindahkan data dari assets.json ke assets.db
# Jalankan SEKALI saja: python migrate.py

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.database import init_db, get_connection
from app.services.asset_service import tambah_asset

JSON_FILE = "data/assets.json"

def migrate():
    print("=" * 50)
    print("  MIGRASI DATA: JSON → SQLite")
    print("=" * 50)

    # cek file JSON ada
    if not os.path.exists(JSON_FILE):
        print(f"❌ File '{JSON_FILE}' tidak ditemukan.")
        print("   Tidak ada data yang perlu dimigrasi.")
        return

    # baca data JSON
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        assets = json.load(f)

    if not assets:
        print("❌ File JSON kosong.")
        return

    print(f"\nDitemukan {len(assets)} asset di JSON.")

    # inisialisasi database
    init_db()

    # cek apakah database sudah punya data
    conn   = get_connection()
    total  = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    conn.close()

    if total > 0:
        print(f"\n⚠  Database sudah punya {total} asset.")
        jawab = input("Lanjutkan migrasi? Data duplikat akan di-skip. (y/n): ")
        if jawab.lower() != "y":
            print("❌ Migrasi dibatalkan.")
            return

    # ambil ID yang sudah ada di database — untuk skip duplikat
    conn          = get_connection()
    existing_ids  = {
        row[0] for row in
        conn.execute("SELECT id FROM assets").fetchall()
    }
    conn.close()

    berhasil = 0
    diskip   = 0
    gagal    = 0

    for a in assets:
        # skip kalau ID sudah ada
        if a["id"] in existing_ids:
            print(f"  ⟳ Skip: '{a['name']}' (ID sudah ada)")
            diskip += 1
            continue

        try:
            # insert langsung ke database tanpa lewat tambah_asset
            # karena kita mau pakai ID dan timestamp yang lama
            conn = get_connection()
            conn.execute("""
                INSERT INTO assets (
                    id, name, type, brand, serial, purchase_date,
                    location, pic, notes, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                a["id"],
                a["name"],
                a["type"],
                a.get("brand", ""),
                a.get("serial", ""),
                a.get("purchase_date", ""),
                a["location"],
                a["pic"],
                a.get("notes", ""),
                a.get("status", "Aktif"),
                a.get("created_at", ""),
                a.get("updated_at", ""),
            ))
            conn.commit()
            conn.close()

            print(f"  ✅ '{a['name']}' berhasil dimigrasi")
            berhasil += 1

        except Exception as e:
            print(f"  ❌ '{a['name']}' gagal: {e}")
            gagal += 1

    print(f"\n{'='*50}")
    print(f"  Selesai!")
    print(f"  Berhasil : {berhasil} asset")
    print(f"  Di-skip  : {diskip} asset")
    print(f"  Gagal    : {gagal} asset")
    print(f"{'='*50}")

    if berhasil > 0:
        print(f"\n✅ Data berhasil dipindah ke assets.db")
        print(f"   File assets.json tetap ada sebagai backup.")
        print(f"   Setelah yakin data aman, boleh dihapus manual.")


if __name__ == "__main__":
    migrate()