# app/routes/main_routes.py
from flask import Blueprint, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Redirect dari root ke halaman asset."""
    return redirect(url_for("assets.index"))