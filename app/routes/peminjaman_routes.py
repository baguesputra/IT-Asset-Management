# app/routes/peminjaman_routes.py

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from app.utils.auth import login_required, admin_required
from app.services.asset_service import get_asset_by_id
from app.services.peminjaman_service import (
    catat_peminjaman, konfirmasi_kembali,
    get_peminjaman_aktif, get_peminjaman_by_asset,
    get_statistik_peminjaman, UNIT_RS
)

peminjaman_bp = Blueprint(
    "peminjaman", __name__, url_prefix="/peminjaman"
)


@peminjaman_bp.route("/")
@login_required
def index():
    """Halaman daftar semua peminjaman aktif."""
    aktif  = get_peminjaman_aktif()
    stats  = get_statistik_peminjaman()
    return render_template(
        "peminjaman/index.html",
        aktif = aktif,
        stats = stats,
    )


@peminjaman_bp.route("/catat/<asset_id>",
                     methods=["GET", "POST"])
@admin_required
def catat(asset_id: str):
    """Form catat peminjaman baru."""
    asset = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    # cek asset sedang dipinjam
    if asset["status"] == "Dipinjam":
        flash(
            f"Asset '{asset['name']}' sedang dipinjam.",
            "warning"
        )
        return redirect(
            url_for("assets.detail", asset_id=asset_id)
        )

    # cek asset dalam kondisi bisa dipinjam
    if asset["status"] not in ["Aktif"]:
        flash(
            f"Asset '{asset['name']}' tidak bisa dipinjam "
            f"(status: {asset['status']}).",
            "warning"
        )
        return redirect(
            url_for("assets.detail", asset_id=asset_id)
        )

    if request.method == "POST":
        data = {
            "nama_peminjam":          request.form.get("nama_peminjam"),
            "unit_peminjam":          request.form.get("unit_peminjam"),
            "tanggal_pinjam":         request.form.get("tanggal_pinjam"),
            "tanggal_rencana_kembali": request.form.get("tanggal_rencana_kembali"),
            "keperluan":              request.form.get("keperluan", ""),
        }

        hasil = catat_peminjaman(
            asset_id,
            data,
            dicatat_oleh=session.get("username", "")
        )

        if hasil:
            flash(
                f"Peminjaman berhasil dicatat untuk "
                f"'{asset['name']}'.",
                "success"
            )
            return redirect(url_for("peminjaman.index"))

        flash("Gagal mencatat peminjaman.", "danger")

    from datetime import date
    return render_template(
        "peminjaman/catat.html",
        asset   = asset,
        unit_rs = UNIT_RS,
        today   = date.today().isoformat(),
    )


@peminjaman_bp.route("/kembali/<int:peminjaman_id>",
                     methods=["POST"])
@admin_required
def kembali(peminjaman_id: int):
    """Konfirmasi asset sudah dikembalikan."""
    hasil = konfirmasi_kembali(
        peminjaman_id,
        dicatat_oleh=session.get("username", "")
    )

    if hasil:
        flash(
            f"Asset '{hasil['asset_name']}' "
            f"berhasil dikonfirmasi kembali.",
            "success"
        )
    else:
        flash("Gagal konfirmasi pengembalian.", "danger")

    return redirect(url_for("peminjaman.index"))


@peminjaman_bp.route("/riwayat/<asset_id>")
@login_required
def riwayat(asset_id: str):
    """Riwayat peminjaman satu asset."""
    asset    = get_asset_by_id(asset_id)
    if asset is None:
        flash("Asset tidak ditemukan.", "danger")
        return redirect(url_for("assets.index"))

    riwayat = get_peminjaman_by_asset(asset_id)
    return render_template(
        "peminjaman/riwayat.html",
        asset   = asset,
        riwayat = riwayat,
    )