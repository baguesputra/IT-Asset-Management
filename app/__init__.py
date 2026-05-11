from flask import Flask, session

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "it-asset-rs-2024-ganti-ini-nanti"

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

    app.register_blueprint(asset_bp)
    app.register_blueprint(main_bp)   
    app.register_blueprint(auth_bp) 
    app.register_blueprint(servis_bp)             

    return app