# app/routes/garansi_routes.py

from flask import Blueprint, render_template
from app.utils.auth import login_required
from app.services.garansi_service import (
    get_semua_dengan_garansi,
    get_garansi_mau_habis,
    get_statistik_garansi,
)

garansi_bp = Blueprint("garansi", __name__, url_prefix="/garansi")


@garansi_bp.route("/")
@login_required
def index():
    """Dashboard tracking garansi semua asset."""
    stats     = get_statistik_garansi()
    mau_habis = get_garansi_mau_habis(30)
    semua     = get_semua_dengan_garansi()

    return render_template(
        "garansi/index.html",
        stats     = stats,
        mau_habis = mau_habis,
        semua     = semua,
    )