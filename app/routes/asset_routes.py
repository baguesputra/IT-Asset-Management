# app/routes/asset_routes.py
# Tanggung jawab: handle request dari browser,
# panggil service, return halaman HTML.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required, admin_required
from app.services.asset_service import (
    get_semua_asset, get_asset_by_id,
    tambah_asset, update_asset, hapus_asset,
    cari_asset, filter_asset, get_statistik,
    get_asset_tua, get_log
)
from config import ASSET_TYPES, ASSET_STATUS, LOCATIONS

# Blueprint = kumpulan route yang bisa didaftarkan ke app
# "assets" = nama blueprint
# url_prefix = semua route di sini diawali /assets
asset_bp = Blueprint("assets", __name__, url_prefix="/assets")


@asset_bp.route("/")
@login_required 
def index():
    """Halaman utama — daftar semua asset."""
    assets = get_semua_asset()
    stats  = get_statistik()
    return render_template("assets/index.html", assets=assets, stats=stats)


@asset_bp.route("/tambah", methods=["GET", "POST"])
@admin_required
def tambah():
    """
    GET  → tampilkan form tambah asset
    POST → proses form yang dikirim user
    """
    if request.method == "POST":
        # ambil data dari form HTML
        # request.form["name"] = nilai input dengan name="name"
        data = {
            "name":          request.form["name"],
            "asset_type":    request.form["type"],
            "brand":         request.form["brand"],
            "serial":        request.form["serial"],
            "purchase_date": request.form["purchase_date"],
            "location":      request.form["location"],
            "pic":           request.form["pic"],
            "notes":         request.form.get("notes", ""),
        }

        asset = tambah_asset(data)

        # flash = pesan sementara yang muncul sekali
        flash(f"Asset '{asset.name}' berhasil ditambahkan! ID: {asset.id}", "success")

        # redirect ke halaman daftar setelah berhasil
        return redirect(url_for("assets.index"))

    # GET request → tampilkan form kosong
    return render_template(
        "assets/tambah.html",
        asset_types = ASSET_TYPES,
        locations   = LOCATIONS,
    )

@asset_bp.route("/detail/<asset_id>")
@login_required 
def detail(asset_id: str):
    """Halaman detail satu asset."""
    asset = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))
    return render_template("assets/detail.html", asset=asset)


@asset_bp.route("/edit/<asset_id>", methods=["GET", "POST"])
@admin_required 
def edit(asset_id: str):
    """
    GET  → tampilkan form edit dengan nilai saat ini
    POST → proses perubahan dan simpan
    """
    asset = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    if request.method == "POST":
        # ambil semua field dari form
        # request.form.get() tidak crash kalau field tidak ada
        perubahan = {
            "name":          request.form.get("name"),
            "type":          request.form.get("type"),
            "brand":         request.form.get("brand"),
            "serial":        request.form.get("serial"),
            "purchase_date": request.form.get("purchase_date"),
            "location":      request.form.get("location"),
            "pic":           request.form.get("pic"),
            "notes":         request.form.get("notes"),
            "status":        request.form.get("status"),
        }

        # hapus field yang kosong — tidak perlu diupdate
        perubahan = {k: v for k, v in perubahan.items() if v}

        update_asset(asset_id, perubahan)
        flash(f"Asset berhasil diperbarui.", "success")
        return redirect(url_for("assets.index"))

    # GET → tampilkan form dengan data saat ini
    return render_template(
        "assets/edit.html",
        asset       = asset,
        asset_types = ASSET_TYPES,
        asset_status = ASSET_STATUS,
        locations   = LOCATIONS,
    )


@asset_bp.route("/cari")
@login_required 
def cari():
    """Cari asset berdasarkan keyword dari URL parameter."""
    # /assets/cari?q=IGD → keyword = "IGD"
    keyword = request.args.get("q", "").strip()
    results = cari_asset(keyword) if keyword else []
    return render_template("assets/cari.html", results=results, keyword=keyword)


@asset_bp.route("/hapus/<asset_id>", methods=["POST"])
@admin_required 
def hapus(asset_id: str):
    """Hapus asset — hanya terima POST request."""
    target = hapus_asset(asset_id)
    if target:
        flash(f"Asset '{target['name']}' berhasil dihapus.", "warning")
    else:
        flash("Asset tidak ditemukan.", "danger")
    return redirect(url_for("assets.index"))

@asset_bp.route("/filter")
def filter_view():
    """
    Halaman filter asset by status atau lokasi.
    Parameter diambil dari URL:
    /assets/filter?kategori=status&nilai=Aktif&nilai=Rusak
    """
    kategori   = request.args.get("kategori", "")
    nilai_list = request.args.getlist("nilai")  # getlist = ambil semua nilai dengan nama sama

    results = []
    if kategori and nilai_list:
        key     = "status" if kategori == "Status" else "location"
        results = filter_asset(key, nilai_list)

    return render_template(
        "assets/filter.html",
        results      = results,
        kategori     = kategori,
        nilai_list   = nilai_list,
        asset_status = ASSET_STATUS,
        locations    = LOCATIONS,
    )


@asset_bp.route("/statistik")
@login_required 
def statistik():
    """Halaman statistik lengkap."""
    from app.services.asset_service import get_asset_tua, get_log
    from config import ASSET_STATUS, LOCATIONS

    stats        = get_statistik()
    semua_assets = get_semua_asset()
    asset_tua    = get_asset_tua(3)   # asset lebih dari 3 tahun
    logs         = get_log(10)        # 10 log terakhir

    # hitung jumlah asset per lokasi untuk tabel
    from collections import Counter
    per_lokasi = Counter(a["location"] for a in semua_assets)
    per_lokasi = sorted(per_lokasi.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "assets/statistik.html",
        stats      = stats,
        asset_tua  = asset_tua,
        logs       = logs,
        per_lokasi = per_lokasi,
    )