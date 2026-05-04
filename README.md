# 🖥️ IT Asset Management CLI

Sistem manajemen aset IT berbasis Command Line Interface (CLI) menggunakan **Pure Python**.  
Dirancang untuk kebutuhan inventarisasi perangkat IT di lingkungan rumah sakit / klinik.

---

## 📦 Fitur

| Fitur | Keterangan |
|---|---|
| ➕ Tambah Asset | Registrasi PC, Printer, CCTV, Switch, dsb |
| 📋 Lihat Asset | Tampilkan semua asset dalam tabel |
| 🔍 Cari Asset | Pencarian berdasarkan nama, lokasi, PIC, dll |
| ✏️ Edit Asset | Update data & status asset |
| 🗑️ Hapus Asset | Hapus asset dengan konfirmasi |
| 📤 Export CSV | Export data ke file CSV siap pakai |
| 📝 Log Aktivitas | Rekam setiap perubahan data |

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Storage**: JSON (lokal, tanpa database)
- **Library**: Standard Library only (tidak perlu `pip install`)

---

## 🚀 Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/USERNAME/it-asset-management.git
cd it-asset-management
```

### 2. (Opsional) Isi data contoh
```bash
python seed_data.py
```

### 3. Jalankan aplikasi
```bash
python main.py
```

---

## 📁 Struktur Project

```
it-asset-management/
├── main.py              # Entry point & menu utama
├── asset_manager.py     # Semua fungsi CRUD
├── seed_data.py         # Script data contoh
├── requirements.txt     # Dependencies (none)
├── .gitignore
├── README.md
├── data/                # ← Tidak di-push (di .gitignore)
│   └── assets.json
├── logs/                # ← Tidak di-push
│   └── activity.log
└── exports/             # ← Tidak di-push
    └── assets_*.csv
```

---

## 📸 Preview

```
████████████████████████████████████████████████████████████
█                                                          █
█           IT ASSET MANAGEMENT SYSTEM                    █
█           Sistem Inventaris Aset IT RS/Klinik            █
█                                                          █
████████████████████████████████████████████████████████████

┌─────────────────────────────────┐
│          MENU UTAMA             │
├─────────────────────────────────┤
│  1. Lihat Semua Asset           │
│  2. Tambah Asset Baru           │
│  3. Cari Asset                  │
│  4. Edit Asset                  │
│  5. Hapus Asset                 │
│  6. Export ke CSV               │
│  7. Lihat Log Aktivitas         │
│  0. Keluar                      │
└─────────────────────────────────┘
```

---

## 👨‍💻 Author

Dibuat untuk kebutuhan manajemen aset IT rumah sakit.

---

## 📄 License

MIT License
