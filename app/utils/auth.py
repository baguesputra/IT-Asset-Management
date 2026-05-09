# app/utils/auth.py
# Helper untuk autentikasi.

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator — lindungi route dari user yang belum login.

    Cara pakai:
        @asset_bp.route("/")
        @login_required          ← tambahkan ini
        def index():
            ...

    Cara kerjanya:
    1. User buka route yang dilindungi
    2. Decorator cek session["logged_in"]
    3. Kalau belum login → redirect ke /login
    4. Kalau sudah login → lanjut ke fungsi aslinya
    """
    @wraps(f)   # wraps menjaga nama dan docstring fungsi asli
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated