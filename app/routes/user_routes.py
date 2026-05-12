# app/routes/user_routes.py

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from app.utils.auth import admin_required, login_required
from app.services.user_service import (
    get_semua_user, buat_user,
    hapus_user, update_password
)

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("/")
@admin_required
def index():
    """Halaman daftar semua user — hanya admin."""
    users = get_semua_user()
    return render_template("users/index.html", users=users)


@user_bp.route("/tambah", methods=["POST"])
@admin_required
def tambah():
    """Tambah user baru."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    nama     = request.form.get("nama", "").strip()
    role     = request.form.get("role", "viewer")

    if not all([username, password, nama]):
        flash("Semua field wajib diisi.", "danger")
        return redirect(url_for("users.index"))

    user = buat_user(username, password, nama, role)
    if user is None:
        flash(f"Username '{username}' sudah digunakan.", "danger")
    else:
        flash(f"User '{nama}' berhasil ditambahkan.", "success")

    return redirect(url_for("users.index"))


@user_bp.route("/hapus/<int:user_id>", methods=["POST"])
@admin_required
def hapus(user_id: int):
    """Hapus user — tidak boleh hapus diri sendiri."""
    users = get_semua_user()

    # cari user yang mau dihapus
    target = next((u for u in users if u["id"] == user_id), None)

    # tidak boleh hapus diri sendiri
    if target and target["username"] == session.get("username"):
        flash("Tidak bisa menghapus akun sendiri.", "danger")
        return redirect(url_for("users.index"))

    hapus_user(user_id)
    flash("User berhasil dihapus.", "warning")
    return redirect(url_for("users.index"))


@user_bp.route("/ganti-password", methods=["GET", "POST"])
@login_required
def ganti_password():
    """User bisa ganti password sendiri."""
    if request.method == "POST":
        from app.services.user_service import verifikasi_login, check_password, get_user_by_username

        password_lama = request.form.get("password_lama", "")
        password_baru = request.form.get("password_baru", "")
        konfirmasi    = request.form.get("konfirmasi", "")

        username = session.get("username")
        user     = get_user_by_username(username)

        # cek password lama benar
        if not check_password(password_lama, user["password"]):
            flash("Password lama salah.", "danger")
            return redirect(url_for("users.ganti_password"))

        # cek password baru cocok
        if password_baru != konfirmasi:
            flash("Konfirmasi password tidak cocok.", "danger")
            return redirect(url_for("users.ganti_password"))

        if len(password_baru) < 6:
            flash("Password baru minimal 6 karakter.", "danger")
            return redirect(url_for("users.ganti_password"))

        update_password(username, password_baru)
        flash("Password berhasil diubah.", "success")
        return redirect(url_for("assets.index"))

    return render_template("users/ganti_password.html")