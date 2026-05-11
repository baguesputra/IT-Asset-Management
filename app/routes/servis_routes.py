# app/routes/servis_routes.py

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from app.utils.auth import login_required
from app.services.asset_service import get_asset_by_id
from app.services.servis_service import (
    tambah_servis, get_servis_by_asset,
    hapus_servis, get_total_biaya, JENIS_SERVIS
)
from datetime import date

servis_bp = Blueprint("servis", __name__, url_prefix="/servis")


@servis_bp.route("/asset/<asset_id>")
@login_required
def riwayat(asset_id: str):
    """Halaman riwayat servis satu asset."""
    asset  = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    riwayat     = get_servis_by_asset(asset_id)
    total_biaya = get_total_biaya(asset_id)

    return render_template(
        "servis/riwayat.html",
        asset        = asset,
        riwayat      = riwayat,
        total_biaya  = total_biaya,
        jenis_servis = JENIS_SERVIS,
        today        = date.today().isoformat(),
    )


@servis_bp.route("/tambah/<asset_id>", methods=["POST"])
@login_required
def tambah(asset_id: str):
    """Tambah catatan servis baru — hanya POST."""
    asset = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    data = {
        "tanggal":    request.form.get("tanggal"),
        "jenis":      request.form.get("jenis"),
        "deskripsi":  request.form.get("deskripsi"),
        "teknisi":    request.form.get("teknisi"),
        "biaya":      int(request.form.get("biaya") or 0),
    }

    tambah_servis(asset_id, data)
    flash("Catatan servis berhasil ditambahkan.", "success")
    return redirect(url_for("servis.riwayat", asset_id=asset_id))


@servis_bp.route("/hapus/<int:servis_id>", methods=["POST"])
@login_required
def hapus(servis_id: int):
    """Hapus satu catatan servis."""
    # ambil asset_id dulu untuk redirect balik
    from app.services.servis_service import get_servis_by_id
    catatan  = get_servis_by_id(servis_id)
    asset_id = catatan["asset_id"] if catatan else None

    hapus_servis(servis_id)
    flash("Catatan servis dihapus.", "warning")

    if asset_id:
        return redirect(url_for("servis.riwayat", asset_id=asset_id))
    return redirect(url_for("assets.index"))