# app/services/user_service.py
# Logika bisnis untuk manajemen user.

import bcrypt
from datetime import datetime
from typing import Optional
from app.services.database import get_connection


def hash_password(password: str) -> str:
    """
    Hash password menggunakan bcrypt.
    gensalt() generate 'salt' acak — membuat hash
    berbeda meski password sama.

    Contoh:
    hash_password("admin123") → "$2b$12$abc..."
    hash_password("admin123") → "$2b$12$xyz..."  (berbeda!)
    """
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """
    Cek apakah password cocok dengan hash.
    Return True kalau cocok, False kalau tidak.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def buat_user(username: str, password: str, nama: str, role: str = "viewer") -> Optional[dict]:
    """
    Buat user baru dengan password yang sudah di-hash.
    Return None kalau username sudah ada.
    """
    # cek username sudah ada
    if get_user_by_username(username):
        return None

    hashed_password = hash_password(password)
    now             = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    conn.execute("""
        INSERT INTO users (username, password, nama, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (username, hashed_password, nama, role, now))
    conn.commit()
    conn.close()

    return get_user_by_username(username)


def get_user_by_username(username: str) -> Optional[dict]:
    """Ambil data user berdasarkan username."""
    conn   = get_connection()
    cursor = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_semua_user() -> list:
    """Ambil semua user — untuk halaman manajemen user."""
    conn   = get_connection()
    cursor = conn.execute(
        "SELECT id, username, nama, role, created_at FROM users ORDER BY id"
        # password sengaja tidak diambil — tidak perlu ditampilkan
    )
    hasil = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return hasil


def verifikasi_login(username: str, password: str) -> Optional[dict]:
    """
    Verifikasi login — cek username dan password.
    Return data user kalau berhasil, None kalau gagal.
    """
    user = get_user_by_username(username)

    if user is None:
        return None

    if not check_password(password, user["password"]):
        return None

    return user


def update_password(username: str, password_baru: str) -> bool:
    """Ganti password user."""
    user = get_user_by_username(username)
    if user is None:
        return False

    hashed = hash_password(password_baru)
    conn   = get_connection()
    conn.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hashed, username)
    )
    conn.commit()
    conn.close()
    return True


def hapus_user(user_id: int) -> bool:
    """Hapus user berdasarkan ID."""
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def init_default_users() -> None:
    """
    Buat user default kalau tabel users masih kosong.
    Dipanggil sekali saat aplikasi pertama jalan.
    """
    conn  = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    if total > 0:
        return   # sudah ada user, skip

    # buat user default
    buat_user("admin",  "admin123",  "Administrator", "admin")
    buat_user("it",     "it2024",    "Staff IT",      "admin")
    buat_user("viewer", "lihat123",  "Viewer",        "viewer")

    print("✅ User default berhasil dibuat.")