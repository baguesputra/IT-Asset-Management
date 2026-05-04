import json
import csv
import os
import uuid
from datetime import datetime

# ── Helper functions ──────────────────────────────────────
def pilih_dari_list(items, prompt="Pilih (nomor):"):
    """
    Tampilkan daftar items bernomor, minta user pilih satu.
    Loop sampai input valid, return item yang dipilih.
    """
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                print(f"❌ Pilihan harus antara 1 dan {len(items)}. Coba lagi.")
        except ValueError:
            print("❌ Input tidak valid. Masukkan nomor yang sesuai.")

def input_teks(prompt, wajib=True):
    """Minta input teks. Kalau wajib=True, tidak boleh kosong."""
    while True:
        nilai = input(prompt).strip()
        if nilai:
            return nilai
        if wajib:
            print("  Tidak boleh kosong.")
        else:
            return nilai

def input_tanggal(prompt):
    """Minta input tanggal format YYYY-MM-DD, validasi format-nya."""
    while True:
        nilai = input(prompt).strip()
        try:
            # datetime.strptime akan ERROR kalau format tidak cocok
            datetime.strptime(nilai, "%Y-%m-%d")
            return nilai                   # format valid, return string-nya
        except ValueError:
            print("  Format salah. Gunakan YYYY-MM-DD, contoh: 2023-01-15")

# ── Data constants ────────────────────────────────────────

ASSET_TYPES = ["PC", "Laptop", "Printer", ...]  # biarkan seperti semula


DATA_FILE = "data/assets.json"
LOG_FILE = "logs/activity.log"

ASSET_TYPES = ["PC", "Laptop", "Printer", "CCTV", "Switch", "Router", "UPS", "Monitor", "Server", "Lainnya"]
ASSET_STATUS = ["Aktif", "Rusak", "Perbaikan", "Tidak Aktif", "Dipinjam"]
LOCATIONS = ["Poli Umum", "IGD", "Radiologi", "Lab", "Farmasi", "Administrasi", "IT", "Gudang", "Lainnya"]


def load_assets():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_assets(assets):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)


def write_log(action, detail):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {detail}\n")


def generate_id():
    return str(uuid.uuid4())[:8].upper()


def add_asset():
    print("\n" + "="*50)
    print("       TAMBAH ASSET BARU")
    print("="*50)

    assets = load_assets()

    # BARU — 1 baris, bersih
    print("\nJenis Asset:")
    asset_type = pilih_dari_list(ASSET_TYPES, "Pilih jenis: ")

    name         = input_teks("\nNama Asset (contoh: PC-IGD-01): ")
    brand        = input_teks("Merk/Model: ")
    serial       = input_teks("Serial Number: ")
    purchase_date = input_tanggal("Tanggal Pembelian (YYYY-MM-DD), contoh 2023-01-15: ")

    print("\nLokasi:")
    location = pilih_dari_list(LOCATIONS, "Pilih lokasi: ")

    pic   = input_teks("PIC (Penanggung Jawab): ")
    notes = input_teks("Catatan (opsional): ", wajib=False)

    asset = {
        "id": generate_id(),
        "name": name,
        "type": asset_type,
        "brand": brand,
        "serial": serial,
        "purchase_date": purchase_date,
        "location": location,
        "pic": pic,
        "status": "Aktif",
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    assets.append(asset)
    save_assets(assets)
    write_log("ADD", f"Asset '{name}' (ID: {asset['id']}) ditambahkan")

    print(f"\n✅ Asset berhasil ditambahkan! ID: {asset['id']}")


def list_assets():
    print("\n" + "="*80)
    print("                         DAFTAR SEMUA ASSET")
    print("="*80)

    assets = load_assets()
    if not assets:
        print("Belum ada asset terdaftar.")
        return

    print(f"{'ID':<10} {'Nama':<20} {'Jenis':<10} {'Lokasi':<15} {'Status':<12} {'PIC':<15}")
    print("-"*80)
    for a in assets:
        print(f"{a['id']:<10} {a['name']:<20} {a['type']:<10} {a['location']:<15} {a['status']:<12} {a['pic']:<15}")
    print("-"*80)
    print(f"Total: {len(assets)} asset")


def search_asset():
    print("\n" + "="*50)
    print("       CARI ASSET")
    print("="*50)

    keyword = input("Masukkan kata kunci (nama/jenis/lokasi/PIC): ").strip().lower()
    assets = load_assets()

    results = [
        a for a in assets
        if keyword in a["name"].lower()
        or keyword in a["type"].lower()
        or keyword in a["location"].lower()
        or keyword in a["pic"].lower()
        or keyword in a.get("serial", "").lower()
    ]

    if not results:
        print(f"\n❌ Tidak ada asset yang cocok dengan '{keyword}'")
        return

    print(f"\nDitemukan {len(results)} asset:\n")
    for a in results:
        print(f"  ID       : {a['id']}")
        print(f"  Nama     : {a['name']}")
        print(f"  Jenis    : {a['type']}")
        print(f"  Merk     : {a['brand']}")
        print(f"  Serial   : {a['serial']}")
        print(f"  Lokasi   : {a['location']}")
        print(f"  Status   : {a['status']}")
        print(f"  PIC      : {a['pic']}")
        print(f"  Catatan  : {a.get('notes', '-')}")
        print(f"  Dibuat   : {a['created_at']}")
        print("-"*40)


def edit_asset():
    print("\n" + "="*50)
    print("       EDIT ASSET")
    print("="*50)

    asset_id = input("Masukkan ID Asset yang ingin diedit: ").strip().upper()
    assets = load_assets()

    target = next((a for a in assets if a["id"] == asset_id), None)
    if not target:
        print(f"❌ Asset dengan ID '{asset_id}' tidak ditemukan.")
        return

    print(f"\nAsset ditemukan: {target['name']}")
    print("Kosongkan field jika tidak ingin mengubah.\n")

    new_name = input(f"Nama [{target['name']}]: ").strip()
    new_brand = input(f"Merk [{target['brand']}]: ").strip()
    new_serial = input(f"Serial [{target['serial']}]: ").strip()
    new_location = input(f"Lokasi [{target['location']}] (ketik baru atau enter): ").strip()
    new_pic = input(f"PIC [{target['pic']}]: ").strip()
    new_notes = input(f"Catatan [{target.get('notes','-')}]: ").strip()

    print("\nStatus:")
    for i, s in enumerate(ASSET_STATUS, 1):
        print(f"  {i}. {s}")
    status_input = input(f"Status [{target['status']}] (nomor atau enter): ").strip()

    old_name = target["name"]
    if new_name:
        target["name"] = new_name
    if new_brand:
        target["brand"] = new_brand
    if new_serial:
        target["serial"] = new_serial
    if new_location:
        target["location"] = new_location
    if new_pic:
        target["pic"] = new_pic
    if new_notes:
        target["notes"] = new_notes
    if status_input:
        try:
            target["status"] = ASSET_STATUS[int(status_input) - 1]
        except (ValueError, IndexError):
            pass

    target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_assets(assets)
    write_log("EDIT", f"Asset '{old_name}' (ID: {asset_id}) diperbarui")

    print(f"\n✅ Asset berhasil diperbarui!")


def delete_asset():
    print("\n" + "="*50)
    print("       HAPUS ASSET")
    print("="*50)

    asset_id = input("Masukkan ID Asset yang ingin dihapus: ").strip().upper()
    assets = load_assets()

    target = next((a for a in assets if a["id"] == asset_id), None)
    if not target:
        print(f"❌ Asset dengan ID '{asset_id}' tidak ditemukan.")
        return

    print(f"\nAsset ditemukan:")
    print(f"  Nama   : {target['name']}")
    print(f"  Jenis  : {target['type']}")
    print(f"  Lokasi : {target['location']}")

    confirm = input("\nApakah yakin ingin menghapus? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Penghapusan dibatalkan.")
        return

    assets = [a for a in assets if a["id"] != asset_id]
    save_assets(assets)
    write_log("DELETE", f"Asset '{target['name']}' (ID: {asset_id}) dihapus")

    print(f"\n✅ Asset '{target['name']}' berhasil dihapus!")


def export_csv():
    print("\n" + "="*50)
    print("       EXPORT KE CSV")
    print("="*50)

    assets = load_assets()
    if not assets:
        print("❌ Tidak ada asset untuk diekspor.")
        return

    os.makedirs("exports", exist_ok=True)
    filename = f"exports/assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = ["id", "name", "type", "brand", "serial", "purchase_date",
                  "location", "pic", "status", "notes", "created_at", "updated_at"]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assets)

    write_log("EXPORT", f"Data diekspor ke '{filename}' ({len(assets)} asset)")
    print(f"\n✅ Berhasil diekspor ke: {filename}")
    print(f"   Total: {len(assets)} asset")


def view_log():
    print("\n" + "="*50)
    print("       LOG AKTIVITAS")
    print("="*50)

    if not os.path.exists(LOG_FILE):
        print("Belum ada aktivitas tercatat.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Show last 20 lines
    recent = lines[-20:] if len(lines) > 20 else lines
    for line in recent:
        print(line.strip())

    print(f"\nTotal log: {len(lines)} entri")
