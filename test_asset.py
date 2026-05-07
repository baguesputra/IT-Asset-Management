# test_asset.py

import pytest
import time
from asset_manager import Asset, generate_id, load_assets, save_assets


# ============================================================
# TEST UNTUK generate_id()
# ============================================================

def test_generate_id_panjang_8():
    """ID harus selalu 8 karakter."""
    id_baru = generate_id()
    assert len(id_baru) == 8

def test_generate_id_huruf_besar():
    """ID harus huruf besar semua."""
    id_baru = generate_id()
    assert id_baru == id_baru.upper()

def test_generate_id_unik():
    """Dua ID yang dibuat berurutan harus berbeda."""
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2


# ============================================================
# TEST UNTUK class Asset
# ============================================================

# fixture = fungsi yang menyiapkan data untuk test
# @pytest.fixture dipanggil otomatis sebelum test yang membutuhkannya
@pytest.fixture
def contoh_asset():
    """Buat satu objek Asset untuk dipakai di test-test di bawah."""
    return Asset(
        name          = "PC-TEST-01",
        asset_type    = "PC",
        brand         = "HP",
        serial        = "SN-TEST-001",
        purchase_date = "2024-01-15",
        location      = "IGD",
        pic           = "Budi",
    )


def test_asset_status_default(contoh_asset):
    """Status awal asset harus Aktif."""
    assert contoh_asset.status == "Aktif"

def test_asset_punya_id(contoh_asset):
    """Asset harus punya ID setelah dibuat."""
    assert contoh_asset.id is not None
    assert len(contoh_asset.id) == 8

def test_asset_nama_tersimpan(contoh_asset):
    """Nama yang diinput harus tersimpan dengan benar."""
    assert contoh_asset.name == "PC-TEST-01"

def test_asset_update_status(contoh_asset):
    """update_status() harus ubah status dengan benar."""
    # pastikan status awal memang Aktif
    assert contoh_asset.status == "Aktif"

    # ubah status
    contoh_asset.update_status("Rusak")

    # status harus berubah jadi Rusak
    assert contoh_asset.status == "Rusak"

    # ubah lagi ke status lain
    contoh_asset.update_status("Perbaikan")
    assert contoh_asset.status == "Perbaikan"

    # pastikan tidak bisa kembali ke Aktif sendiri
    assert contoh_asset.status != "Aktif"


# ============================================================
# TEST UNTUK to_dict() dan from_dict()
# ============================================================

def test_to_dict_punya_semua_key(contoh_asset):
    """to_dict() harus menghasilkan semua field yang dibutuhkan."""
    data = contoh_asset.to_dict()

    # semua key ini harus ada
    key_wajib = [
        "id", "name", "type", "brand", "serial",
        "purchase_date", "location", "pic",
        "status", "notes", "created_at", "updated_at"
    ]
    for key in key_wajib:
        assert key in data, f"Key '{key}' tidak ada di to_dict()"

def test_from_dict_siklus_penuh(contoh_asset):
    """
    Siklus penuh: objek → dict → objek baru.
    Semua field harus sama persis.
    """
    # konversi ke dict
    data = contoh_asset.to_dict()

    # konversi balik ke objek
    asset_baru = Asset.from_dict(data)

    # semua field harus sama
    assert asset_baru.id       == contoh_asset.id
    assert asset_baru.name     == contoh_asset.name
    assert asset_baru.status   == contoh_asset.status
    assert asset_baru.location == contoh_asset.location
    assert asset_baru.pic      == contoh_asset.pic

def test_from_dict_status_ikut_terbawa():
    """from_dict() harus membawa status dari data, bukan pakai default."""
    data = {
        "id":            "ABCD1234",
        "name":          "PRINTER-01",
        "type":          "Printer",
        "brand":         "Epson",
        "serial":        "SN-001",
        "purchase_date": "2022-06-10",
        "location":      "Farmasi",
        "pic":           "Siti",
        "notes":         "",
        "status":        "Rusak",      # ← bukan "Aktif"
        "created_at":    "2022-06-10 08:00:00",
        "updated_at":    "2022-06-10 08:00:00",
    }

    asset = Asset.from_dict(data)

    assert asset.status == "Rusak"    # harus "Rusak", bukan "Aktif"
    assert asset.id     == "ABCD1234" # ID harus dari data, bukan generate baru