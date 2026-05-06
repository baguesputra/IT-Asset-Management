#!/usr/bin/env python3
"""
IT Asset Management CLI
Sistem manajemen aset IT untuk lingkungan rumah sakit / klinik
"""

from asset_manager import (
    add_asset, list_assets, search_asset, filter_asset, tampilkan_statistik, reminder_asset,
    edit_asset, delete_asset, export_csv, view_log
)


def print_banner():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "   IT ASSET MANAGEMENT SYSTEM".center(58) + "█")
    print("█" + "   Sistem Inventaris Aset IT RS/Klinik".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)


def print_menu():
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
    print("│  8. Reminder Asset Lama         │")
    print("│  9. Lihat Log Aktivitas         │")
    print("│  0. Keluar                      │")
    print("└─────────────────────────────────┘")


def main():
    print_banner()

    while True:
        tampilkan_statistik()
        print_menu()
        choice = input("\nPilih menu: ").strip()

        if choice == "1":
            list_assets()
        elif choice == "2":
            add_asset()
        elif choice == "3":
            search_asset()
        elif choice == "4":          # ← tambah ini
            filter_asset()
        elif choice == "5":          # ← dulu "4"
            edit_asset()
        elif choice == "6":          # ← dulu "5"
            delete_asset()
        elif choice == "7":          # ← dulu "6"
            export_csv()
        elif choice == "8":          # ← dulu "7"
            reminder_asset()
        elif choice == "9":          # ← dulu "8"
            view_log()
        elif choice == "0":
            print("\n👋 Terima kasih! Sampai jumpa.\n")
            break
        else:
            print("❌ choice tidak valid. Silakan coba lagi.")

        input("\nTekan Enter untuk kembali ke menu...")


if __name__ == "__main__":
    main()
