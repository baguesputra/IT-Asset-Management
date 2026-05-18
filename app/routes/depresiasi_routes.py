# app/routes/depresiasi_routes.py

from flask import Blueprint, render_template
from app.utils.auth import login_required, admin_required
from app.services.depresiasi_service import (
    get_semua_dengan_depresiasi,
    get_statistik_depresiasi,
    get_proyeksi_penggantian,
    UMUR_EKONOMIS,
)

depresiasi_bp = Blueprint(
    "depresiasi", __name__, url_prefix="/depresiasi"
)


@depresiasi_bp.route("/")
@login_required
def index():
    """Dashboard depresiasi asset."""
    stats     = get_statistik_depresiasi()
    proyeksi  = get_proyeksi_penggantian()
    semua     = get_semua_dengan_depresiasi()

    return render_template(
        "depresiasi/index.html",
        stats        = stats,
        proyeksi     = proyeksi,
        semua        = semua,
        umur_ekonomis = UMUR_EKONOMIS,
    )