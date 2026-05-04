def pilih_dari_list(items, prompt="Pilih (nomor): "):
    """
    Tampilkan daftar items bernomor, minta user pilih satu.
    Loop sampai input valid, return item yang dipilih.
    """
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        try:
            choice = int(input("Pilih nomor: "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                print(f"❌ Pilihan harus antara 1 dan {len(items)}. Coba lagi.")
        except ValueError:
            print("❌ Input tidak valid. Masukkan nomor yang sesuai.")

# Test :
buah = ["Apel", "Jeruk", "Pisang", "Mangga"]
hasil = pilih_dari_list(buah)
print(f"Kamu memilih: {hasil}")


def input_teks(prompt, wajib=True):
    while True:
        nilai = input(prompt).strip()   # .strip() buang spasi di awal/akhir
        
        if nilai:                       # kalau tidak kosong
            return nilai
        
        if wajib:
            print("  Tidak boleh kosong.")
        else:
            return nilai                # boleh kosong, langsung return ""