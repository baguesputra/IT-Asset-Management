# app/routes/auth_routes.py
# Tanggung jawab: handle login dan logout.

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from app.services.user_service import verifikasi_login
from app.utils.logger import get_logger

logger  = get_logger("auth")    # logger khusus modul auth
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → tampilkan form login
    POST → cek username & password
    """
    # kalau sudah login, langsung ke dashboard
    if session.get("logged_in"):
        return redirect(url_for("assets.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        ip       = request.remote_addr

        # verifikasi lewat database — bukan config
        user = verifikasi_login(username, password)

        if user:
            session["logged_in"] = True
            session["username"]  = user["username"]
            session["role"]      = user["role"]
            session["nama"]      = user["nama"]

             # catat login berhasil
            logger.info(
                "Login berhasil: %s (%s) dari %s",
                username, user["role"], ip
            )

            flash(f"Selamat datang, {user['nama']}!", "success")
            return redirect(url_for("assets.index"))
        
        # catat login gagal — penting untuk deteksi brute force
        logger.warning(
            "Login gagal: username='%s' dari %s",
            username, ip
        )

        flash("Username atau password salah.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Hapus session dan redirect ke login."""
    nama = session.get("nama", "")
    username = session.get("username", "")
    ip       = request.remote_addr
    logger.info("Logout: %s dari %s", username, ip)
    session.clear()
    flash(f"Sampai jumpa, {nama}!", "info")
    return redirect(url_for("auth.login"))