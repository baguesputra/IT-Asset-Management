# app/utils/input_helper.py
# Tanggung jawab: semua fungsi yang berhubungan
# dengan input dari user di terminal.

from datetime import datetime
from typing import Optional


def pilih_dari_list(items: list, prompt: str = "Pilih (nomor): ") -> str:
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            print(f"  Pilih antara 1 sampai {len(items)}.")
        except ValueError:
            print("  Masukkan angka saja.")


def pilih_dari_list_opsional(items: list, nilai_saat_ini: str, prompt: str) -> Optional[str]:
    print(f"  Saat ini: {nilai_saat_ini}")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    while True:
        jawaban = input(prompt + " (Enter untuk skip): ").strip()
        if jawaban == "":
            return None
        try:
            choice = int(jawaban)
            if 1 <= choice <= len(items):
                return items[choice - 1]
            print(f"  Pilih antara 1 sampai {len(items)}.")
        except ValueError:
            print("  Masukkan angka saja, atau Enter untuk skip.")


def pilih_multi_dari_list(items: list, prompt: str = "Pilih nomor (pisah koma, contoh 1,3): ") -> list:
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    while True:
        jawaban = input(prompt).strip()
        bagian  = jawaban.split(",")
        hasil   = []
        for b in bagian:
            try:
                angka = int(b.strip())
                if 1 <= angka <= len(items):
                    hasil.append(items[angka - 1])
            except ValueError:
                pass
        if hasil:
            return hasil
        print(f"  Masukkan minimal satu nomor yang valid (1–{len(items)}).")


def input_teks(prompt: str, wajib: bool = True) -> str:
    while True:
        nilai = input(prompt).strip()
        if nilai:
            return nilai
        if wajib:
            print("  Tidak boleh kosong.")
        else:
            return nilai


def input_teks_opsional(label: str, nilai_saat_ini: str) -> Optional[str]:
    nilai = input(f"{label} [{nilai_saat_ini}] (Enter untuk skip): ").strip()
    return None if nilai == "" else nilai


def input_tanggal(prompt: str) -> str:
    while True:
        nilai = input(prompt).strip()
        try:
            datetime.strptime(nilai, "%Y-%m-%d")
            return nilai
        except ValueError:
            print("  Format salah. Gunakan YYYY-MM-DD, contoh: 2024-01-15")