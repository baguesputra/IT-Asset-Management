"""
Script untuk mengisi data contoh (sample data)
Jalankan sekali untuk testing: python seed_data.py
"""

import json
import os
from datetime import datetime

sample_assets = [
    {
        "id": "A1B2C3D4",
        "name": "PC-IGD-01",
        "type": "PC",
        "brand": "HP EliteDesk 800",
        "serial": "SN-HP-2023-001",
        "purchase_date": "2023-01-15",
        "location": "IGD",
        "pic": "Budi Santoso",
        "status": "Aktif",
        "notes": "PC utama IGD, terkoneksi ke sistem EMR",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": "E5F6G7H8",
        "name": "PRINTER-FARMASI-01",
        "type": "Printer",
        "brand": "Epson L3150",
        "serial": "SN-EP-2022-045",
        "purchase_date": "2022-06-10",
        "location": "Farmasi",
        "pic": "Siti Rahayu",
        "status": "Aktif",
        "notes": "Printer struk resep",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": "I9J0K1L2",
        "name": "CCTV-LOBBY-01",
        "type": "CCTV",
        "brand": "Hikvision DS-2CD2143G2-I",
        "serial": "SN-HK-2023-012",
        "purchase_date": "2023-03-20",
        "location": "Administrasi",
        "pic": "Ahmad Fauzi",
        "status": "Aktif",
        "notes": "CCTV pintu masuk utama",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": "M3N4O5P6",
        "name": "SWITCH-IT-CORE",
        "type": "Switch",
        "brand": "Cisco SG350-28P",
        "serial": "SN-CS-2022-003",
        "purchase_date": "2022-01-05",
        "location": "IT",
        "pic": "Rizky Pratama",
        "status": "Aktif",
        "notes": "Core switch utama jaringan RS",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": "Q7R8S9T0",
        "name": "LAPTOP-RADIOLOGI-01",
        "type": "Laptop",
        "brand": "Lenovo ThinkPad E15",
        "serial": "SN-LN-2023-007",
        "purchase_date": "2023-05-01",
        "location": "Radiologi",
        "pic": "Dewi Lestari",
        "status": "Perbaikan",
        "notes": "Keyboard rusak, sedang diperbaiki",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]

os.makedirs("data", exist_ok=True)
with open("data/assets.json", "w") as f:
    json.dump(sample_assets, f, indent=2, ensure_ascii=False)

print(f"✅ {len(sample_assets)} data contoh berhasil ditambahkan!")
print("Jalankan 'python main.py' untuk memulai aplikasi.")
