# tests/test_asset.py
# tambahkan import ini di atas
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.asset import Asset, generate_id

# ── test yang sudah ada tetap di sini ──────────────

# ── test baru untuk service + SQLite ───────────────

# fixture khusus untuk test database
# pakai database sementara — tidak ganggu data asli
@pytest.fixture
def test_db(monkeypatch, tmp_path):
    """
    Buat database sementara untuk test.
    tmp_path = folder temporary yang dibuat pytest,
    otomatis dihapus setelah test selesai.
    monkeypatch = ganti nilai variable sementara selama test.
    """
    import app.services.database as db_module
    import app.services.asset_service as svc

    # arahkan DB_FILE ke file temporary
    test_db_path = str(tmp_path / "test_assets.db")
    monkeypatch.setattr(db_module, "DB_FILE", test_db_path)

    # inisialisasi tabel di database test
    db_module.init_db()

    return test_db_path


def test_tambah_dan_get_asset(test_db):
    """Tambah asset lalu ambil — harus ketemu."""
    from app.services.asset_service import tambah_asset, get_asset_by_id

    asset = tambah_asset({
        "name":          "PC-TEST-99",
        "asset_type":    "PC",
        "brand":         "HP",
        "serial":        "SN-999",
        "purchase_date": "2024-01-01",
        "location":      "IGD",
        "pic":           "Tester",
        "notes":         "",
    })

    # ambil dari database
    result = get_asset_by_id(asset.id)

    assert result is not None
    assert result["name"]     == "PC-TEST-99"
    assert result["location"] == "IGD"
    assert result["status"]   == "Aktif"


def test_update_asset(test_db):
    """Update status asset — harus berubah di database."""
    from app.services.asset_service import tambah_asset, update_asset, get_asset_by_id

    asset = tambah_asset({
        "name":          "PRINTER-TEST-01",
        "asset_type":    "Printer",
        "brand":         "Epson",
        "serial":        "SN-001",
        "purchase_date": "2023-06-01",
        "location":      "Farmasi",
        "pic":           "Siti",
        "notes":         "",
    })

    # update status
    update_asset(asset.id, {"status": "Rusak"})

    # ambil dari database — status harus berubah
    result = get_asset_by_id(asset.id)
    assert result["status"] == "Rusak"


def test_hapus_asset(test_db):
    """Hapus asset — tidak boleh ketemu lagi di database."""
    from app.services.asset_service import tambah_asset, hapus_asset, get_asset_by_id

    asset = tambah_asset({
        "name":          "CCTV-TEST-01",
        "asset_type":    "CCTV",
        "brand":         "Hikvision",
        "serial":        "SN-CCTV-01",
        "purchase_date": "2022-01-01",
        "location":      "IGD",
        "pic":           "Ahmad",
        "notes":         "",
    })

    # hapus
    hapus_asset(asset.id)

    # cari lagi — harus None
    result = get_asset_by_id(asset.id)
    assert result is None


def test_cari_asset(test_db):
    """Cari asset berdasarkan keyword — harus ketemu."""
    from app.services.asset_service import tambah_asset, cari_asset

    tambah_asset({
        "name":          "SWITCH-IT-CORE",
        "asset_type":    "Switch",
        "brand":         "Cisco",
        "serial":        "SN-SW-001",
        "purchase_date": "2023-01-01",
        "location":      "IT",
        "pic":           "Rizky",
        "notes":         "",
    })

    # cari pakai keyword
    results = cari_asset("switch")
    assert len(results) >= 1
    assert results[0]["name"] == "SWITCH-IT-CORE"

    # cari yang tidak ada
    kosong = cari_asset("xyzxyzxyz")
    assert len(kosong) == 0