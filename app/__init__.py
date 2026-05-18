from flask import Flask, app, session, render_template
from app.services.user_service import init_default_users
from config import SECRET_KEY, DEBUG
import uuid
from app.services.database import migrate_db             
from app.routes.peminjaman_routes import peminjaman_bp  
  

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(peminjaman_bp) 
    app.secret_key = SECRET_KEY
    app.debug      = DEBUG

     # setup logging — sebelum blueprint didaftarkan
    from app.utils.logger import setup_logger
    setup_logger(app)

    # context processor — inject variabel ke SEMUA template
    # tanpa perlu kirim manual di setiap render_template()
    @app.context_processor
    def inject_globals():
        return {
            "is_admin": session.get("role") == "admin",
            "current_user": session.get("nama", ""),
            "current_role": session.get("role", ""),
        }

    from app.routes.asset_routes import asset_bp
    from app.routes.main_routes import main_bp   
    from app.routes.auth_routes  import auth_bp
    from app.routes.servis_routes import servis_bp 
    from app.routes.user_routes import user_bp
    from app.routes.garansi_routes import garansi_bp
    from app.routes.depresiasi_routes import depresiasi_bp

    app.register_blueprint(asset_bp)
    app.register_blueprint(main_bp)   
    app.register_blueprint(auth_bp) 
    app.register_blueprint(servis_bp)
    app.register_blueprint(user_bp) 
    app.register_blueprint(garansi_bp)
    app.register_blueprint(depresiasi_bp)

    # ── Error handlers ────────────────────────────
    register_error_handlers(app)

    with app.app_context():
        from app.services.user_service import init_default_users
        from app.services.database import migrate_db
        init_default_users()
        migrate_db() 

    from app.services.user_service import init_default_users
    with app.app_context():
        init_default_users()            

    app.logger.info("Aplikasi berhasil diinisialisasi") 
    return app

def register_error_handlers(app: Flask) -> None:
    """Daftarkan semua custom error handler."""

    from app.utils.logger import get_logger
    logger = get_logger("error")

    @app.errorhandler(400)
    def bad_request(e):
        logger.warning("400 Bad Request: %s", str(e))
        return render_template(
            "errors/error.html",
            kode    = 400,
            judul   = "Permintaan Tidak Valid",
            pesan   = "Permintaan yang dikirim tidak dapat diproses.",
            saran   = "Periksa kembali data yang Anda masukkan.",
        ), 400

    @app.errorhandler(403)
    def forbidden(e):
        logger.warning("403 Forbidden: %s", str(e))
        return render_template(
            "errors/error.html",
            kode    = 403,
            judul   = "Akses Ditolak",
            pesan   = "Anda tidak memiliki izin untuk mengakses halaman ini.",
            saran   = "Hubungi administrator jika Anda membutuhkan akses.",
        ), 403

    @app.errorhandler(404)
    def not_found(e):
        logger.warning("404 Not Found: %s", str(e))
        return render_template(
            "errors/error.html",
            kode    = 404,
            judul   = "Halaman Tidak Ditemukan",
            pesan   = "Halaman yang Anda cari tidak ada atau sudah dipindahkan.",
            saran   = "Periksa URL yang Anda masukkan atau kembali ke halaman utama.",
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        # generate tiket error — memudahkan support
        tiket = str(uuid.uuid4())[:8].upper()

        # catat detail error ke log — bukan ke user
        logger.error(
            "500 Server Error [Tiket: %s]: %s",
            tiket, str(e)
        )

        return render_template(
            "errors/error.html",
            kode    = 500,
            judul   = "Terjadi Kesalahan Sistem",
            pesan   = "Sistem mengalami kesalahan yang tidak terduga.",
            saran   = f"Catat kode tiket ini dan hubungi IT: {tiket}",
            tiket   = tiket,
        ), 500