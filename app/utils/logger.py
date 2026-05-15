# app/utils/logger.py
# Setup logging terpusat untuk seluruh aplikasi.
# Import logger dari sini di file manapun yang butuh.

import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_DIR, DEBUG


def setup_logger(app) -> None:
    """
    Setup logging untuk Flask app.
    Dipanggil sekali saat app dibuat di create_app().

    RotatingFileHandler — otomatis buat file baru
    kalau ukuran log sudah terlalu besar.
    Simpan 5 file backup — tidak sampai disk penuh.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    # ── Format log ────────────────────────────────
    # contoh output:
    # [2024-01-15 08:30:45] INFO     auth: Login berhasil: admin
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Handler ke file ───────────────────────────
    # maxBytes=5MB, backupCount=5
    # kalau app.log sudah 5MB → rename jadi app.log.1
    # buat app.log baru — simpan maksimal 5 file lama
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes    = 5 * 1024 * 1024,   # 5 MB
        backupCount = 5,
        encoding    = "utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)   # file: WARNING ke atas

    # ── Handler ke terminal ───────────────────────
    # di development tampil di terminal juga
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if DEBUG:
        console_handler.setLevel(logging.DEBUG)   # terminal: semua level
    else:
        console_handler.setLevel(logging.WARNING) # production: WARNING ke atas

    # ── Pasang ke Flask app logger ────────────────
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # ── Logger untuk tiap modul ───────────────────
    # bisa dipakai di file lain dengan:
    # from app.utils.logger import get_logger
    # logger = get_logger(__name__)
    moduls = ["auth", "asset", "servis", "database", "user"]
    for nama in moduls:
        logger = logging.getLogger(nama)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    app.logger.info("Logging berhasil disetup")


def get_logger(nama: str) -> logging.Logger:
    """
    Return logger untuk modul tertentu.

    Cara pakai di file lain:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Pesan info")
        logger.error("Ada error: %s", str(e))
    """
    return logging.getLogger(nama)