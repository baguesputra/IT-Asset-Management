# 🖥️ IT Asset Management System

Sistem manajemen aset IT berbasis CLI untuk lingkungan rumah sakit / klinik.  
Dibangun dengan **Pure Python** menggunakan arsitektur **MVC**.

---

## 🏗️ Arsitektur
it-asset-management/
├── app/
│   ├── models/          → Struktur data (class Asset)
│   ├── services/        → Logika bisnis (CRUD, filter, export)
│   └── utils/           → Helper functions (input validation)
├── cli/
│   └── main.py          → Interface terminal
├── tests/               → Unit test (pytest)
├── config.py            → Konfigurasi terpusat
└── seed_data.py         → Data contoh

---

## ⚙️ Tech Stack

- **Language** : Python 3.8+
- **Storage**  : JSON (akan migrate ke SQLite)
- **Pattern**  : MVC + Service Layer
- **Test**     : pytest

---

## 🚀 Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/USERNAME/it-asset-management.git
cd it-asset-management
```

### 2. Install dependencies
```bash
pip install pytest
```

### 3. Isi data contoh (opsional)
```bash
python seed_data.py
```

### 4. Jalankan aplikasi
```bash
python cli/main.py
```

### 5. Jalankan test
```bash
pytest tests/ -v
```

---

## ✅ Fitur

### CRUD
- Tambah asset dengan wizard input step by step
- Lihat semua asset dalam format tabel
- Cari asset berdasarkan keyword
- Edit asset — semua field opsional
- Hapus asset dengan konfirmasi

### Filter & Monitoring
- Filter by status atau lokasi — bisa multi-select
- Statistik ringkas tampil otomatis di menu utama
- Reminder asset tua — tentukan batas tahun sendiri

### Import & Export
- Export ke CSV — siap buka di Excel
- Import dari CSV — validasi duplikat dan kolom wajib
- Backup otomatis setiap ada perubahan data

### Sistem
- Log aktivitas dengan timestamp
- Auto-backup — simpan 10 backup terakhir

---

## 🧠 Konsep Python yang Digunakan

`OOP` · `MVC Architecture` · `Type Hints` · `pytest` ·
`try/except` · `list comprehension` · `collections.Counter` ·
`datetime` · `csv` · `json` · `shutil` · `os.path`

---

## 🗺️ Roadmap

- [x] CLI dengan fitur lengkap
- [x] Arsitektur MVC
- [x] Unit testing
- [ ] Migrate ke SQLite
- [ ] Web interface dengan Flask
- [ ] Deploy ke jaringan lokal RS
- [ ] Login & role user

---

## 👨‍💻 Author

Dibuat untuk kebutuhan manajemen aset IT rumah sakit.