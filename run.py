# run.py
# Entry point untuk menjalankan Flask web server.
# Jalankan: python run.py

from app import create_app
from config import DEBUG

app = create_app()

if __name__ == "__main__":
    # debug=True → otomatis reload kalau ada perubahan kode
    # host="0.0.0.0" → bisa diakses dari komputer lain di jaringan
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)