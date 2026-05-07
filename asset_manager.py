import json
import csv
import os
import uuid
import shutil 
from datetime import datetime
from collections import Counter 
from typing import Optional 


# ============================================================
# KONSTANTA — data yang tidak berubah selama program berjalan
# ============================================================

DATA_FILE = "data/assets.json"
LOG_FILE  = "logs/activity.log"

ASSET_TYPES  = ["PC", "Laptop", "Printer", "CCTV", "Switch", "Router", "UPS", "Monitor", "Server", "Lainnya"]
ASSET_STATUS = ["Aktif", "Rusak", "Perbaikan", "Tidak Aktif", "Dipinjam"]
LOCATIONS    = ["Poli Umum", "IGD", "Radiologi", "Lab", "Farmasi", "Administrasi", "IT", "Gudang", "Lainnya"]


# ============================================================
# HELPER FUNCTIONS — fungsi kecil yang dipakai berkali-kali
# ============================================================

def pilih_dari_list(items: list, prompt: str = "Pilih (nomor): ") -> str:
    """
    Tampilkan daftar bernomor, minta user pilih satu.
    Loop terus sampai input valid. Tidak bisa di-skip.
    """
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

def pilih_multi_dari_list(items: list, prompt: str = "Pilih nomor (pisah koma, contoh 1,3): ") -> list:
    """
    User bisa pilih lebih dari satu item dari daftar.
    Input: "1,3" → return ["Rusak", "Perbaikan"]
    Loop sampai minimal satu pilihan valid.
    """
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        jawaban = input(prompt).strip()

        # .split(",") memotong string berdasarkan koma
        # "1,3" → ["1", "3"]
        bagian = jawaban.split(",")

        hasil = []   # list kosong untuk menampung pilihan valid

        for b in bagian:
            # b.strip() buang spasi — jaga-jaga kalau user ketik "1, 3"
            try:
                angka = int(b.strip())
                if 1 <= angka <= len(items):
                    hasil.append(items[angka - 1])
                # kalau di luar range, skip saja — tidak dimasukkan
            except ValueError:
                pass   # kalau bukan angka, skip

        if hasil:          # kalau ada minimal satu pilihan valid
            return hasil   # return list, bukan satu item

        print(f"  Masukkan minimal satu nomor yang valid (1–{len(items)}).")

def pilih_dari_list_opsional(items: list, nilai_saat_ini: str, prompt: str) -> Optional[str]:
    """
    Sama seperti pilih_dari_list, tapi user boleh skip dengan Enter.
    Return None kalau skip, return item kalau user pilih.
    """
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

def input_teks(prompt: str, wajib: bool = True) -> str:
    """
    Minta input teks bebas.
    wajib=True  → loop sampai diisi, tidak boleh kosong.
    wajib=False → boleh kosong, langsung return "".
    """
    while True:
        nilai = input(prompt).strip()
        if nilai:
            return nilai
        if wajib:
            print("  Tidak boleh kosong.")
        else:
            return nilai

def input_teks_opsional(label: str, nilai_saat_ini: str) -> Optional[str]:
    """
    Untuk form EDIT. Tampilkan nilai saat ini, user boleh skip.
    Return None kalau skip, return teks baru kalau diisi.

    Prompt yang terbentuk:
        Nama [PC-IGD-01] (Enter untuk skip):
    """
    nilai = input(f"{label} [{nilai_saat_ini}] (Enter untuk skip): ").strip()
    if nilai == "":
        return None
    return nilai

def input_tanggal(prompt: str) -> str:
    """
    Minta input tanggal, validasi format YYYY-MM-DD.
    datetime.strptime() lempar ValueError kalau format salah —
    kita tangkap itu untuk validasi.
    """
    while True:
        nilai = input(prompt).strip()
        try:
            datetime.strptime(nilai, "%Y-%m-%d")
            return nilai
        except ValueError:
            print("  Format salah. Gunakan YYYY-MM-DD, contoh: 2024-01-15")


# ============================================================
# FUNGSI UTILITAS — load, save, log, generate ID
# ============================================================

def load_assets() -> list:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_assets(assets: list) -> None:
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)

def write_log(action: str, detail: str) -> None:
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {detail}\n")

def generate_id() -> str:
    return str(uuid.uuid4())[:8].upper()

def backup_data() -> None:
    """
    Buat salinan file assets.json ke folder data/backups/
    dengan nama file yang menyertakan timestamp.
    Dipanggil otomatis setiap kali data berubah.
    Hanya simpan 10 backup terakhir — hapus yang lama.
    """
    # kalau file data utama belum ada, tidak perlu backup
    if not os.path.exists(DATA_FILE):
        return

    # buat folder backups kalau belum ada
    # exist_ok=True → tidak error kalau folder sudah ada
    backup_dir = "data/backups"
    os.makedirs(backup_dir, exist_ok=True)

    # nama file backup menyertakan timestamp
    # contoh: assets_20240115_083012.json
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/assets_{timestamp}.json"

    # copy file utama ke folder backup
    shutil.copy(DATA_FILE, backup_path)

    # --- hapus backup lama, simpan hanya 10 terakhir ---
    # os.listdir() return list nama file di folder itu
    semua_backup = sorted(os.listdir(backup_dir))
    # sorted() mengurutkan nama file — karena nama mengandung
    # timestamp, urutan nama = urutan waktu (lama ke baru)

    # kalau backup sudah lebih dari 10, hapus yang paling lama
    MAKS_BACKUP = 10
    if len(semua_backup) > MAKS_BACKUP:
        # slice [:-MAKS_BACKUP] → semua kecuali 10 terakhir
        yang_dihapus = semua_backup[:-MAKS_BACKUP]
        for nama_file in yang_dihapus:
            os.remove(f"{backup_dir}/{nama_file}")


# ============================================================
# FITUR UTAMA
# ============================================================
def tampilkan_statistik() -> None:
    """
    Tampilkan ringkasan data asset:
    total, jumlah per status, lokasi terbanyak.
    Dipanggil otomatis setiap menu utama tampil.
    """
    assets = load_assets()

    # kalau belum ada data, tidak tampilkan apapun
    if not assets:
        return

    # --- hitung per status ---
    # list comprehension: ambil semua nilai "status" dari tiap asset
    semua_status = [a["status"] for a in assets]

    # Counter hitung otomatis berapa kali tiap nilai muncul
    hitung_status = Counter(semua_status)

    # --- hitung per lokasi ---
    semua_lokasi = [a["location"] for a in assets]
    hitung_lokasi = Counter(semua_lokasi)

    # .most_common(1) return list berisi 1 item paling sering muncul
    # bentuknya: [("IGD", 4)]
    # [0]    → ambil item pertama: ("IGD", 4)
    # [0][0] → ambil nama lokasinya: "IGD"
    # [0][1] → ambil jumlahnya: 4
    lokasi_teratas = hitung_lokasi.most_common(1)[0]

    # --- tampilkan ---
    print("\n" + "─"*40)
    print(f"  Total asset  : {len(assets)}")
    print(f"  Aktif        : {hitung_status['Aktif']}")
    print(f"  Rusak        : {hitung_status['Rusak']}")
    print(f"  Perbaikan    : {hitung_status['Perbaikan']}")
    print(f"  Tidak Aktif  : {hitung_status['Tidak Aktif']}")
    print(f"  Dipinjam     : {hitung_status['Dipinjam']}")
    print(f"  Terbanyak di : {lokasi_teratas[0]} ({lokasi_teratas[1]} asset)")
    print("─"*40)

def add_asset() -> None:
    print("\n" + "="*50)
    print("       TAMBAH ASSET BARU")
    print("="*50)

    assets = load_assets()

    print("\nJenis Asset:")
    asset_type = pilih_dari_list(ASSET_TYPES, "Pilih jenis: ")

    name          = input_teks("\nNama Asset (contoh: PC-IGD-01): ")
    brand         = input_teks("Merk/Model: ")
    serial        = input_teks("Serial Number: ")
    purchase_date = input_tanggal("Tanggal Pembelian (YYYY-MM-DD): ")

    print("\nLokasi:")
    location = pilih_dari_list(LOCATIONS, "Pilih lokasi: ")

    pic   = input_teks("PIC (Penanggung Jawab): ")
    notes = input_teks("Catatan (opsional): ", wajib=False)

    asset = {
        "id":            generate_id(),
        "name":          name,
        "type":          asset_type,
        "brand":         brand,
        "serial":        serial,
        "purchase_date": purchase_date,
        "location":      location,
        "pic":           pic,
        "status":        "Aktif",
        "notes":         notes,
        "created_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    assets.append(asset)
    backup_data()
    save_assets(assets)
    write_log("ADD", f"Asset '{name}' (ID: {asset['id']}) ditambahkan")

    print(f"\n✅ Asset berhasil ditambahkan! ID: {asset['id']}")

def list_assets() -> None:
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

def filter_asset() -> None:
    print("\n" + "="*50)
    print("       FILTER ASSET")
    print("="*50)

    # Langkah 1: pilih kategori
    print("\nFilter berdasarkan:")
    kategori = pilih_dari_list(["Status", "Lokasi"], "Pilih kategori: ")

    # Langkah 2: pilih nilai — sekarang bisa lebih dari satu
    if kategori == "Status":
        print("\nPilih status (boleh lebih dari satu, pisah koma):")
        nilai_list = pilih_multi_dari_list(ASSET_STATUS)
        key        = "status"
    elif kategori == "Lokasi":
        print("\nPilih lokasi (boleh lebih dari satu, pisah koma):")
        nilai_list = pilih_multi_dari_list(LOCATIONS)
        key        = "location"

    # Langkah 3: filter
    # dulu:  a[key] == nilai          → satu nilai
    # baru:  a[key] in nilai_list     → cek apakah ada di list
    assets  = load_assets()
    results = [a for a in assets if a[key] in nilai_list]

    # Langkah 4: tampilkan
    # ", ".join(nilai_list) gabungkan list jadi string
    # ["Rusak", "Perbaikan"] → "Rusak, Perbaikan"
    label = ", ".join(nilai_list)

    print(f"\nHasil filter: {kategori} = {label}")
    print("-"*70)

    if not results:
        print(f"Tidak ada asset dengan {kategori.lower()} '{label}'.")
        return

    print(f"{'ID':<10} {'Nama':<20} {'Jenis':<10} {'Status':<12} {'Lokasi':<15}")
    print("-"*70)
    for a in results:
        print(f"{a['id']:<10} {a['name']:<20} {a['type']:<10} {a['status']:<12} {a['location']:<15}")
    print("-"*70)
    print(f"Ditemukan: {len(results)} asset")

def search_asset() -> None:
    print("\n" + "="*50)
    print("       CARI ASSET")
    print("="*50)

    keyword = input_teks("Kata kunci (nama/jenis/lokasi/PIC): ").lower()
    assets  = load_assets()

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
        print(f"  ID        : {a['id']}")
        print(f"  Nama      : {a['name']}")
        print(f"  Jenis     : {a['type']}")
        print(f"  Merk      : {a['brand']}")
        print(f"  Serial    : {a['serial']}")
        print(f"  Lokasi    : {a['location']}")
        print(f"  Status    : {a['status']}")
        print(f"  PIC       : {a['pic']}")
        print(f"  Catatan   : {a.get('notes', '-')}")
        print(f"  Dibuat    : {a['created_at']}")
        print("-"*40)

def edit_asset() -> None:
    print("\n" + "="*50)
    print("       EDIT ASSET")
    print("="*50)

    asset_id = input_teks("ID Asset yang ingin diedit: ").upper()
    assets   = load_assets()

    target = next((a for a in assets if a["id"] == asset_id), None)

    if target is None:
        print(f"❌ Asset dengan ID '{asset_id}' tidak ditemukan.")
        return

    print(f"\nAsset ditemukan: {target['name']}")
    print("Tekan Enter untuk melewati field yang tidak ingin diubah.\n")

    nama_baru   = input_teks_opsional("Nama",    target["name"])
    brand_baru  = input_teks_opsional("Merk",    target["brand"])
    serial_baru = input_teks_opsional("Serial",  target["serial"])
    pic_baru    = input_teks_opsional("PIC",     target["pic"])
    notes_baru  = input_teks_opsional("Catatan", target.get("notes", ""))

    print("\nLokasi:")
    lokasi_baru = pilih_dari_list_opsional(LOCATIONS, target["location"], "Pilih lokasi baru")

    print("\nStatus:")
    status_baru = pilih_dari_list_opsional(ASSET_STATUS, target["status"], "Pilih status baru")

    # terapkan perubahan — hanya field yang tidak None
    old_name = target["name"]

    if nama_baru   is not None: target["name"]     = nama_baru
    if brand_baru  is not None: target["brand"]    = brand_baru
    if serial_baru is not None: target["serial"]   = serial_baru
    if pic_baru    is not None: target["pic"]      = pic_baru
    if notes_baru  is not None: target["notes"]    = notes_baru
    if lokasi_baru is not None: target["location"] = lokasi_baru
    if status_baru is not None: target["status"]   = status_baru

    target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    backup_data()
    save_assets(assets)
    write_log("EDIT", f"Asset '{old_name}' (ID: {asset_id}) diperbarui")

    print(f"\n✅ Asset berhasil diperbarui!")

def delete_asset() -> None:
    print("\n" + "="*50)
    print("       HAPUS ASSET")
    print("="*50)

    asset_id = input_teks("ID Asset yang ingin dihapus: ").upper()
    assets   = load_assets()

    target = next((a for a in assets if a["id"] == asset_id), None)

    if target is None:
        print(f"❌ Asset dengan ID '{asset_id}' tidak ditemukan.")
        return

    print(f"\nAsset ditemukan:")
    print(f"  Nama   : {target['name']}")
    print(f"  Jenis  : {target['type']}")
    print(f"  Lokasi : {target['location']}")

    konfirmasi = input("\nYakin ingin menghapus? (y/n): ").strip().lower()

    if konfirmasi != "y":
        print("❌ Penghapusan dibatalkan.")
        return

    assets = [a for a in assets if a["id"] != asset_id]
    backup_data()
    save_assets(assets)
    write_log("DELETE", f"Asset '{target['name']}' (ID: {asset_id}) dihapus")

    print(f"\n✅ Asset '{target['name']}' berhasil dihapus!")

def export_csv() -> None:
    print("\n" + "="*50)
    print("       EXPORT KE CSV")
    print("="*50)

    assets = load_assets()

    if not assets:
        print("❌ Tidak ada asset untuk diekspor.")
        return

    os.makedirs("exports", exist_ok=True)
    filename = f"exports/assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    fieldnames = [
        "id", "name", "type", "brand", "serial", "purchase_date",
        "location", "pic", "status", "notes", "created_at", "updated_at"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assets)

    write_log("EXPORT", f"Data diekspor ke '{filename}' ({len(assets)} asset)")

    print(f"\n✅ Berhasil diekspor ke: {filename}")
    print(f"   Total: {len(assets)} asset")

def import_csv() -> None:
    """
    Import data asset dari file CSV.
    Validasi tiap baris sebelum dimasukkan ke data.
    Baris yang bermasalah di-skip dan dilaporkan.
    """
    print("\n" + "="*50)
    print("       IMPORT DARI CSV")
    print("="*50)

    # minta path file dari user
    path = input_teks("\nPath file CSV (contoh: imports/data.csv): ")

    # cek apakah file ada
    # os.path.exists() return True/False
    if not os.path.exists(path):
        print(f"❌ File '{path}' tidak ditemukan.")
        return

    # kolom yang WAJIB ada di CSV
    KOLOM_WAJIB = ["name", "type", "location", "pic"]

    assets_sekarang = load_assets()

    # kumpulkan nama asset yang sudah ada — untuk cek duplikat
    # set() seperti list tapi tidak boleh ada nilai yang sama
    # dan pengecekan "in" jauh lebih cepat dari list
    nama_existing = {a["name"].lower() for a in assets_sekarang}

    berhasil  = []   # asset yang lolos validasi
    gagal     = []   # baris yang di-skip beserta alasannya
    nama_csv  = set()  # nama dari CSV — untuk cek duplikat internal

    def safe(val, default=""):
            return (val or default).strip()

    # baca file CSV
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # cek apakah kolom wajib ada di header CSV
        # reader.fieldnames berisi list nama kolom
        if not reader.fieldnames:
            print("❌ File CSV kosong atau tidak punya header.")
            return

        kolom_tidak_ada = [
            k for k in KOLOM_WAJIB
            if k not in reader.fieldnames
        ]
        if kolom_tidak_ada:
            print(f"❌ Kolom berikut tidak ada di CSV: {', '.join(kolom_tidak_ada)}")
            print(f"   Kolom wajib: {', '.join(KOLOM_WAJIB)}")
            return

        # proses tiap baris
        for nomor, baris in enumerate(reader, 1):

            # skip baris kosong
            if all(v is None for v in baris.values()):
                continue

            # INI yang perlu diindent masuk ke dalam for
            nama = baris.get("name", "") or ""
            nama = nama.strip()

            # validasi 1: nama tidak boleh kosong
            if not nama:
                gagal.append(f"Baris {nomor}: nama kosong")
                continue

            # validasi 2: duplikat di dalam file CSV itu sendiri
            if nama.lower() in nama_csv:
                gagal.append(f"Baris {nomor}: '{nama}' duplikat di dalam CSV")
                continue

            # validasi 3: sudah ada di data sekarang
            if nama.lower() in nama_existing:
                gagal.append(f"Baris {nomor}: '{nama}' sudah ada di data")
                continue

            # lolos semua validasi — buat asset baru
            # .get() dengan default "" agar tidak crash kalau kolom tidak ada
            def safe(val, default=""):
                """Konversi None ke string kosong, lalu strip."""
                return (val or default).strip()
            asset = {
                "id":            generate_id(),
                "name":          nama,
                "type":          safe(baris.get("type"), "Lainnya"),
                "brand":         safe(baris.get("brand")),
                "serial":        safe(baris.get("serial")),
                "purchase_date": safe(baris.get("purchase_date")),
                "location":      safe(baris.get("location")),
                "pic":           safe(baris.get("pic")),
                "status":        safe(baris.get("status"), "Aktif"),
                "notes":         safe(baris.get("notes")),
                "created_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            berhasil.append(asset)
            nama_csv.add(nama.lower())   # catat nama ini sudah diproses

    # --- konfirmasi sebelum simpan ---
    print(f"\nHasil pembacaan CSV:")
    print(f"  Siap diimport : {len(berhasil)} asset")
    print(f"  Di-skip       : {len(gagal)} baris")

    if gagal:
        print("\nBaris yang di-skip:")
        for alasan in gagal:
            print(f"  ✗ {alasan}")

    if not berhasil:
        print("\n❌ Tidak ada data yang bisa diimport.")
        return

    # tampilkan preview asset yang akan masuk
    print(f"\nPreview asset yang akan diimport:")
    print(f"  {'Nama':<22} {'Jenis':<12} {'Lokasi':<15} {'PIC'}")
    print("  " + "-"*60)
    for a in berhasil[:5]:    # tampilkan maksimal 5 dulu
        print(f"  {a['name']:<22} {a['type']:<12} {a['location']:<15} {a['pic']}")
    if len(berhasil) > 5:
        print(f"  ... dan {len(berhasil) - 5} asset lainnya")

    # konfirmasi
    konfirmasi = input(f"\nLanjutkan import {len(berhasil)} asset? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("❌ Import dibatalkan.")
        return

    # simpan
    assets_sekarang.extend(berhasil)
    backup_data()
    save_assets(assets_sekarang)
    write_log("IMPORT", f"{len(berhasil)} asset diimport dari '{path}'")

    print(f"\n✅ Berhasil mengimport {len(berhasil)} asset!")

def reminder_asset() -> None:
    """
    Tampilkan asset yang sudah lebih dari N tahun sejak tanggal beli.
    User bisa tentukan sendiri batas tahunnya.
    """
    print("\n" + "="*50)
    print("       REMINDER ASSET TUA")
    print("="*50)

    # tanya user mau berapa tahun batasnya
    # pakai try/except karena input bisa saja bukan angka
    while True:
        try:
            batas = int(input("\nTampilkan asset lebih dari berapa tahun? "))
            if batas > 0:
                break
            print("  Masukkan angka lebih dari 0.")
        except ValueError:
            print("  Masukkan angka saja.")

    assets = load_assets()
    tua    = []   # list untuk menampung asset yang memenuhi syarat

    for a in assets:

        # skip asset yang tidak punya tanggal pembelian
        # .get() aman — tidak crash kalau key tidak ada
        if not a.get("purchase_date"):
            continue   # lanjut ke asset berikutnya

        # hitung umur asset dalam tahun
        tgl_beli     = datetime.strptime(a["purchase_date"], "%Y-%m-%d")
        tgl_sekarang = datetime.now()
        selisih_hari = (tgl_sekarang - tgl_beli).days
        umur_tahun   = selisih_hari / 365.25

        # kalau umurnya melebihi batas, masukkan ke list tua
        # sekalian simpan umurnya untuk ditampilkan nanti
        if umur_tahun > batas:
            tua.append({
                "asset":  a,
                "umur":   umur_tahun,
            })

    # --- tampilkan hasilnya ---
    print(f"\n⚠  Asset lebih dari {batas} tahun:\n")

    if not tua:
        print(f"  Tidak ada asset yang lebih dari {batas} tahun.")
        return

    # urutkan dari yang paling tua dulu
    # sorted() mengurutkan list
    # key=lambda x: x["umur"] → urutkan berdasarkan field "umur"
    # reverse=True → dari besar ke kecil (tua ke muda)
    tua = sorted(tua, key=lambda x: x["umur"], reverse=True)

    print(f"  {'Nama':<22} {'Tgl Beli':<14} {'Umur':<10} {'Status':<12} {'Lokasi'}")
    print("  " + "-"*72)

    for item in tua:
        a    = item["asset"]
        umur = item["umur"]

        # konversi umur ke format "X thn Y bln"
        tahun = int(umur)
        bulan = int((umur - tahun) * 12)

        print(f"  {a['name']:<22} {a['purchase_date']:<14} {tahun} thn {bulan} bln   {a['status']:<12} {a['location']}")

    print("  " + "-"*72)
    print(f"  Total: {len(tua)} asset")

def view_log() -> None:
    print("\n" + "="*50)
    print("       LOG AKTIVITAS")
    print("="*50)

    if not os.path.exists(LOG_FILE):
        print("Belum ada aktivitas tercatat.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    recent = lines[-20:]
    for line in recent:
        print(line.strip())

    print(f"\nTotal log: {len(lines)} entri")