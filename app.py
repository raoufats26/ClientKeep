from flask import Flask
from config import Config
from extensions import db, login_manager, migrate
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to continue.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth      import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.clients   import clients_bp
    from routes.invoices  import invoices_bp
    from routes.reminders import reminders_bp
    from routes.settings  import settings_bp
    from routes.portal    import portal_bp
    from routes.export    import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(export_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
