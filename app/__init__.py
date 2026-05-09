from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "it-asset-rs-2024-ganti-ini-nanti"

    from app.routes.asset_routes import asset_bp
    from app.routes.main_routes import main_bp   # ← tambah

    app.register_blueprint(asset_bp)
    app.register_blueprint(main_bp)              # ← tambah

    return app