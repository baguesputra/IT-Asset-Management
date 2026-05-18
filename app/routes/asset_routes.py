# app/routes/asset_routes.py
# Tanggung jawab: handle request dari browser,
# panggil service, return halaman HTML.

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response 
from app.utils.auth import login_required, admin_required
from app.services.asset_service import (
    get_semua_asset, get_asset_by_id,
    tambah_asset, update_asset, hapus_asset,
    cari_asset, filter_asset, get_statistik,
    get_asset_tua, get_log
)
from app.services.pdf_service import (
    generate_laporan_asset,
    generate_laporan_semua
)
from config import ASSET_TYPES, ASSET_STATUS, LOCATIONS
from datetime import datetime

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
            "harga_beli":         int(request.form.get("harga_beli") or 0),
            "vendor":             request.form.get("vendor", ""),
            "no_kontrak":         request.form.get("no_kontrak", ""),
            "masa_garansi_bulan": int(request.form.get("masa_garansi_bulan") or 0),
            "tgl_garansi_mulai":  request.form.get("tgl_garansi_mulai", ""),
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
    asset = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    # hitung depresiasi untuk ditampilkan di detail
    from app.services.depresiasi_service import hitung_depresiasi
    depresiasi = hitung_depresiasi(asset)

    return render_template(
        "assets/detail.html",
        asset      = asset,
        depresiasi = depresiasi,
    )


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


@asset_bp.route("/api/statistik")
@login_required
def api_statistik():
    """
    Return data statistik dalam format JSON.
    Dikonsumsi Chart.js di browser — bukan untuk manusia.
    """
    assets = get_semua_asset()

    # hitung per status
    from collections import Counter
    per_status = Counter(a["status"] for a in assets)
    per_lokasi = Counter(a["location"] for a in assets)
    per_jenis  = Counter(a["type"] for a in assets)

    return jsonify({
        "per_status": {
            "labels": list(per_status.keys()),
            "data":   list(per_status.values()),
        },
        "per_lokasi": {
            "labels": list(per_lokasi.keys()),
            "data":   list(per_lokasi.values()),
        },
        "per_jenis": {
            "labels": list(per_jenis.keys()),
            "data":   list(per_jenis.values()),
        },
        "total": len(assets),
    })


@asset_bp.route("/dashboard")
@login_required
def dashboard():
    """Halaman dashboard dengan chart visual."""
    stats  = get_statistik()
    assets = get_semua_asset()

    # data untuk tabel ringkasan
    from collections import Counter
    per_lokasi = sorted(
        Counter(a["location"] for a in assets).items(),
        key=lambda x: x[1],
        reverse=True
    )

    return render_template(
        "assets/dashboard.html",
        stats      = stats,
        per_lokasi = per_lokasi,
        total      = len(assets),
    )

@asset_bp.route("/api/cari")
@login_required
def api_cari():
    """
    API endpoint untuk pencarian live.
    Return JSON — dikonsumsi JavaScript, bukan browser langsung.

    URL: /assets/api/cari?q=keyword
    """
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return jsonify([])
    
    results = cari_asset(keyword)

    # batasi 20 hasil
    return jsonify(results[:20])

@asset_bp.route("/pdf/<asset_id>")
@login_required
def pdf_asset(asset_id: str):
    """
    Generate dan download PDF untuk satu asset.
    Response dengan header khusus supaya browser
    otomatis download file — bukan tampilkan di tab.
    """
    from app.services.servis_service import get_servis_by_asset

    asset   = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    riwayat = get_servis_by_asset(asset_id)

    # generate PDF
    pdf_bytes = generate_laporan_asset(asset, riwayat)

    # nama file PDF
    nama_file = f"laporan_{asset['name']}_{datetime.now().strftime('%Y%m%d')}.pdf"

    # Response dengan header yang memberitahu browser
    # ini file yang harus didownload, bukan ditampilkan
    return Response(
        pdf_bytes,
        mimetype    = "application/pdf",
        headers     = {
            "Content-Disposition": f"attachment; filename={nama_file}"
        }
    )


@asset_bp.route("/pdf-semua")
@admin_required
def pdf_semua():
    """Generate dan download PDF laporan semua asset."""
    from datetime import datetime

    assets    = get_semua_asset()
    pdf_bytes = generate_laporan_semua(assets)
    nama_file = f"laporan_semua_asset_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        pdf_bytes,
        mimetype = "application/pdf",
        headers  = {
            "Content-Disposition": f"attachment; filename={nama_file}"
        }
    )