# cek_env.py — hapus setelah test
from config import SECRET_KEY, FLASK_ENV, RS_NAMA, DEBUG

print(f"FLASK_ENV  : {FLASK_ENV}")
print(f"DEBUG      : {DEBUG}")
print(f"RS_NAMA    : {RS_NAMA}")
print(f"SECRET_KEY : {SECRET_KEY[:10]}...")  # tampilkan 10 karakter saja