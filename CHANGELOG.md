IT Asset Management CLI — Feature Log
Project: it-asset-management
Stack: Pure Python · JSON Storage · CSV Export/Import

CRUD — Operasi Data Dasar

Tambah Asset — input wizard step by step, pilih jenis/lokasi dari daftar bernomor, validasi tanggal format YYYY-MM-DD, auto-generate ID unik 8 karakter
Lihat Asset — tampilkan semua asset dalam format tabel dengan kolom ID, Nama, Jenis, Lokasi, Status, PIC
Cari Asset — pencarian keyword di nama, jenis, lokasi, PIC, dan serial number
Edit Asset — update field manapun, Enter untuk skip field yang tidak ingin diubah, semua field opsional
Hapus Asset — tampilkan detail asset sebelum hapus, konfirmasi y/n sebelum eksekusi


Filter & Pencarian

Filter by Status — pilih satu atau lebih status sekaligus (Aktif, Rusak, Perbaikan, Tidak Aktif, Dipinjam), input multi-select dengan koma
Filter by Lokasi — pilih satu atau lebih lokasi sekaligus, logika sama dengan filter status


Statistik & Monitoring

Statistik Ringkas — tampil otomatis di menu utama setiap saat: total asset, jumlah per status, lokasi dengan asset terbanyak
Reminder Asset Tua — tampilkan asset yang umurnya melebihi batas tahun yang ditentukan user, diurutkan dari yang paling tua, format tampil "X thn Y bln"


Import & Export

Export ke CSV — ekspor semua data ke file CSV dengan timestamp di nama file, encoding UTF-8 BOM agar Excel bisa buka dengan benar
Import dari CSV — baca file CSV, validasi kolom wajib, deteksi duplikat internal dan dengan data yang sudah ada, preview sebelum konfirmasi import, skip baris bermasalah dengan laporan alasan


Sistem & Log

Log Aktivitas — setiap operasi ADD, EDIT, DELETE, EXPORT, IMPORT dicatat otomatis dengan timestamp ke file logs/activity.log, tampilkan 20 entri terakhir


Helper Functions (Internal)

pilih_dari_list() — tampilkan daftar bernomor, validasi input, loop sampai valid
pilih_dari_list_opsional() — sama tapi bisa di-skip dengan Enter, return None
pilih_multi_dari_list() — pilih lebih dari satu item, input dipisah koma
input_teks() — input teks wajib atau opsional, strip whitespace
input_teks_opsional() — untuk form edit, tampilkan nilai saat ini, bisa di-skip
input_tanggal() — validasi format YYYY-MM-DD dengan datetime.strptime


Konsep Python yang Sudah Dipelajari
try/except · while True · default parameter · list comprehension · None vs "" · is not None · enumerate() · .strip() · .split() · set() · collections.Counter · datetime · timedelta · lambda · sorted() · continue · extend() vs append() · csv.DictReader · csv.DictWriter · nested function · os.path.exists() · json.load/dump