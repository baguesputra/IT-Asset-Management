# coba_db.py — file test sementara, hapus setelah selesai

from app.services.database import init_db, get_connection

# buat database dan tabel
init_db()
print("Database berhasil dibuat!")

# cek tabel yang ada
conn   = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for t in tables:
    print(f"Tabel: {t['name']}")

conn.close()