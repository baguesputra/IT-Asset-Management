# cli/main.py
# Tanggung jawab: interface terminal.
# Ambil input user, panggil service, tampilkan hasil.
# Tidak ada logika bisnis di sini.

import os
import sys

# tambahkan root folder ke path supaya bisa import config dan app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ASSET_TYPES, ASSET_STATUS, LOCATIONS, EXPORT_DIR
)
from app.services.asset_service import (
    tambah_asset, get_semua_asset, get_asset_by_id,
    update_asset, hapus_asset, cari_asset, filter_asset,
    get_statistik, get_asset_tua, get_log,
    export_ke_csv, import_dari_csv
)
from app.utils.input_helper import (
    pilih_dari_list, pilih_dari_list_opsional,
    pilih_multi_dari_list, input_teks,
    input_teks_opsional, input_tanggal
)


def print_banner() -> None:
    print("\n" + "█"*60)
    print("█" + "   IT ASSET MANAGEMENT SYSTEM".center(58) + "█")
    print("█" + "   Sistem Inventaris Aset IT RS/Klinik".center(58) + "█")
    print("█"*60)


def print_statistik() -> None:
    stats = get_statistik()
    if not stats:
        return
    per_status = stats["per_status"]
    print("\n" + "─"*40)
    print(f"  Total asset  : {stats['total']}")
    print(f"  Aktif        : {per_status.get('Aktif', 0)}")
    print(f"  Rusak        : {per_status.get('Rusak', 0)}")
    print(f"  Perbaikan    : {per_status.get('Perbaikan', 0)}")
    print(f"  Tidak Aktif  : {per_status.get('Tidak Aktif', 0)}")
    print(f"  Dipinjam     : {per_status.get('Dipinjam', 0)}")
    print(f"  Terbanyak di : {stats['lokasi_teratas']} ({stats['lokasi_jumlah']} asset)")
    print("─"*40)


def print_menu() -> None:
    print("\n┌─────────────────────────────────┐")
    print("│          MENU UTAMA             │")
    print("├─────────────────────────────────┤")
    print("│  1. Lihat Semua Asset           │")
    print("│  2. Tambah Asset Baru           │")
    print("│  3. Cari Asset                  │")
    print("│  4. Filter Asset                │")
    print("│  5. Edit Asset                  │")
    print("│  6. Hapus Asset                 │")
    print("│  7. Export ke CSV               │")
    print("│  8. Import dari CSV             │")
    print("│  9. Reminder Asset Tua          │")
    print("│ 10. Lihat Log Aktivitas         │")
    print("│  0. Keluar                      │")
    print("└─────────────────────────────────┘")


def tampilkan_tabel(assets: list) -> None:
    """Helper untuk tampilkan list asset dalam format tabel."""
    if not assets:
        print("  Tidak ada asset.")
        return
    print(f"\n{'ID':<10} {'Nama':<20} {'Jenis':<10} {'Lokasi':<15} {'Status':<12} {'PIC':<15}")
    print("-"*80)
    for a in assets:
        print(f"{a['id']:<10} {a['name']:<20} {a['type']:<10} {a['location']:<15} {a['status']:<12} {a['pic']:<15}")
    print("-"*80)
    print(f"Total: {len(assets)} asset")


# ── Handler tiap menu ─────────────────────────────

def handle_lihat() -> None:
    print("\n" + "="*80)
    print("                    DAFTAR SEMUA ASSET")
    print("="*80)
    tampilkan_tabel(get_semua_asset())


def handle_tambah() -> None:
    print("\n" + "="*50)
    print("       TAMBAH ASSET BARU")
    print("="*50)

    print("\nJenis Asset:")
    asset_type = pilih_dari_list(ASSET_TYPES, "Pilih jenis: ")
    name          = input_teks("\nNama Asset (contoh: PC-IGD-01): ")
    brand         = input_teks("Merk/Model: ")
    serial        = input_teks("Serial Number: ")
    purchase_date = input_tanggal("Tanggal Pembelian (YYYY-MM-DD): ")
    print("\nLokasi:")
    location = pilih_dari_list(LOCATIONS, "Pilih lokasi: ")
    pic      = input_teks("PIC (Penanggung Jawab): ")
    notes    = input_teks("Catatan (opsional): ", wajib=False)

    # kumpulkan data, kirim ke service
    asset = tambah_asset({
        "name":          name,
        "asset_type":    asset_type,
        "brand":         brand,
        "serial":        serial,
        "purchase_date": purchase_date,
        "location":      location,
        "pic":           pic,
        "notes":         notes,
    })
    print(f"\n✅ Asset berhasil ditambahkan! ID: {asset.id}")


def handle_cari() -> None:
    print("\n" + "="*50)
    print("       CARI ASSET")
    print("="*50)
    keyword = input_teks("Kata kunci: ")
    results = cari_asset(keyword)
    if not results:
        print(f"\n❌ Tidak ada asset yang cocok dengan '{keyword}'")
        return
    print(f"\nDitemukan {len(results)} asset:")
    tampilkan_tabel(results)


def handle_filter() -> None:
    print("\n" + "="*50)
    print("       FILTER ASSET")
    print("="*50)
    print("\nFilter berdasarkan:")
    kategori = pilih_dari_list(["Status", "Lokasi"], "Pilih kategori: ")

    if kategori == "Status":
        print("\nPilih status (boleh lebih dari satu, pisah koma):")
        nilai_list = pilih_multi_dari_list(ASSET_STATUS)
        key        = "status"
    else:
        print("\nPilih lokasi (boleh lebih dari satu, pisah koma):")
        nilai_list = pilih_multi_dari_list(LOCATIONS)
        key        = "location"

    results = filter_asset(key, nilai_list)
    label   = ", ".join(nilai_list)
    print(f"\nHasil filter: {kategori} = {label}")
    tampilkan_tabel(results)


def handle_edit() -> None:
    print("\n" + "="*50)
    print("       EDIT ASSET")
    print("="*50)
    asset_id = input_teks("ID Asset: ").upper()
    target   = get_asset_by_id(asset_id)

    if target is None:
        print(f"❌ Asset '{asset_id}' tidak ditemukan.")
        return

    print(f"\nAsset ditemukan: {target['name']}")
    print("Tekan Enter untuk melewati field yang tidak ingin diubah.\n")

    perubahan = {
        "name":     input_teks_opsional("Nama",    target["name"]),
        "brand":    input_teks_opsional("Merk",    target["brand"]),
        "serial":   input_teks_opsional("Serial",  target["serial"]),
        "pic":      input_teks_opsional("PIC",     target["pic"]),
        "notes":    input_teks_opsional("Catatan", target.get("notes", "")),
    }

    print("\nLokasi:")
    perubahan["location"] = pilih_dari_list_opsional(LOCATIONS, target["location"], "Pilih lokasi baru")
    print("\nStatus:")
    perubahan["status"] = pilih_dari_list_opsional(ASSET_STATUS, target["status"], "Pilih status baru")

    update_asset(asset_id, perubahan)
    print(f"\n✅ Asset berhasil diperbarui!")


def handle_hapus() -> None:
    print("\n" + "="*50)
    print("       HAPUS ASSET")
    print("="*50)
    asset_id = input_teks("ID Asset: ").upper()
    target   = get_asset_by_id(asset_id)

    if target is None:
        print(f"❌ Asset '{asset_id}' tidak ditemukan.")
        return

    print(f"\n  Nama   : {target['name']}")
    print(f"  Jenis  : {target['type']}")
    print(f"  Lokasi : {target['location']}")

    if input("\nYakin hapus? (y/n): ").strip().lower() != "y":
        print("❌ Dibatalkan.")
        return

    hapus_asset(asset_id)
    print(f"\n✅ Asset '{target['name']}' berhasil dihapus!")


def handle_export() -> None:
    print("\n" + "="*50)
    print("       EXPORT KE CSV")
    print("="*50)
    assets = get_semua_asset()
    if not assets:
        print("❌ Tidak ada asset untuk diekspor.")
        return
    filename = export_ke_csv(EXPORT_DIR)
    print(f"\n✅ Diekspor ke: {filename}")
    print(f"   Total: {len(assets)} asset")


def handle_import() -> None:
    print("\n" + "="*50)
    print("       IMPORT DARI CSV")
    print("="*50)
    path = input_teks("\nPath file CSV: ")

    if not os.path.exists(path):
        print(f"❌ File '{path}' tidak ditemukan.")
        return

    hasil = import_dari_csv(path)
    berhasil = hasil["berhasil"]
    gagal    = hasil["gagal"]

    print(f"\n  Siap diimport : {len(berhasil)} asset")
    print(f"  Di-skip       : {len(gagal)} baris")

    if gagal:
        print("\nBaris yang di-skip:")
        for alasan in gagal:
            print(f"  ✗ {alasan}")

    if not berhasil:
        print("❌ Tidak ada data yang bisa diimport.")
        return

    print(f"\nPreview:")
    for a in berhasil[:3]:
        print(f"  {a['name']} | {a['type']} | {a['location']}")
    if len(berhasil) > 3:
        print(f"  ... dan {len(berhasil)-3} lainnya")

    if input(f"\nLanjutkan import {len(berhasil)} asset? (y/n): ").strip().lower() != "y":
        print("❌ Import dibatalkan.")
        return

    print(f"\n✅ Berhasil mengimport {len(berhasil)} asset!")


def handle_reminder() -> None:
    print("\n" + "="*50)
    print("       REMINDER ASSET TUA")
    print("="*50)
    while True:
        try:
            batas = int(input("\nTampilkan asset lebih dari berapa tahun? "))
            if batas > 0:
                break
            print("  Masukkan angka lebih dari 0.")
        except ValueError:
            print("  Masukkan angka saja.")

    hasil = get_asset_tua(batas)
    print(f"\n⚠  Asset lebih dari {batas} tahun:\n")

    if not hasil:
        print(f"  Tidak ada asset yang lebih dari {batas} tahun.")
        return

    print(f"  {'Nama':<22} {'Tgl Beli':<14} {'Umur':<12} {'Status':<12} {'Lokasi'}")
    print("  " + "-"*72)
    for item in hasil:
        a     = item["asset"]
        umur  = item["umur"]
        tahun = int(umur)
        bulan = int((umur - tahun) * 12)
        print(f"  {a['name']:<22} {a['purchase_date']:<14} {tahun} thn {bulan} bln   {a['status']:<12} {a['location']}")
    print("  " + "-"*72)
    print(f"  Total: {len(hasil)} asset")


def handle_log() -> None:
    print("\n" + "="*50)
    print("       LOG AKTIVITAS")
    print("="*50)
    lines = get_log()
    if not lines:
        print("Belum ada aktivitas tercatat.")
        return
    for line in lines:
        print(line)


# ── Main loop ─────────────────────────────────────

def main() -> None:
    print_banner()

    handlers = {
        "1":  handle_lihat,
        "2":  handle_tambah,
        "3":  handle_cari,
        "4":  handle_filter,
        "5":  handle_edit,
        "6":  handle_hapus,
        "7":  handle_export,
        "8":  handle_import,
        "9":  handle_reminder,
        "10": handle_log,
    }

    while True:
        print_statistik()
        print_menu()
        pilihan = input("\nPilih menu: ").strip()

        if pilihan == "0":
            print("\n👋 Terima kasih! Sampai jumpa.\n")
            break
        elif pilihan in handlers:
            handlers[pilihan]()
        else:
            print("❌ Pilihan tidak valid.")

        input("\nTekan Enter untuk kembali ke menu...")


if __name__ == "__main__":
    main()