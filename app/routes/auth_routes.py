# app/routes/auth_routes.py
# Tanggung jawab: handle login dan logout.

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from app.services.user_service import verifikasi_login

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

        # verifikasi lewat database — bukan config
        user = verifikasi_login(username, password)

        if user:
            session["logged_in"] = True
            session["username"]  = user["username"]
            session["role"]      = user["role"]
            session["nama"]      = user["nama"]

            flash(f"Selamat datang, {user['nama']}!", "success")
            return redirect(url_for("assets.index"))

        flash("Username atau password salah.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Hapus session dan redirect ke login."""
    nama = session.get("nama", "")
    session.clear()
    flash(f"Sampai jumpa, {nama}!", "info")
    return redirect(url_for("auth.login"))