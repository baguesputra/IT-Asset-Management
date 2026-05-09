# app/routes/auth_routes.py
# Tanggung jawab: handle login dan logout.

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from config import USERS

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

        # cek apakah username ada dan password cocok
        if USERS.get(username) == password:
            # simpan info login ke session
            session["logged_in"] = True
            session["username"]  = username

            flash(f"Selamat datang, {username}!", "success")
            return redirect(url_for("assets.index"))

        # username atau password salah
        flash("Username atau password salah.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Hapus session dan redirect ke login."""
    username = session.get("username", "")

    # clear() hapus semua data di session
    session.clear()

    flash(f"Sampai jumpa, {username}!", "info")
    return redirect(url_for("auth.login"))