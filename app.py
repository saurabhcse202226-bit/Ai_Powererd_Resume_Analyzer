from flask import Flask
from config import Config
from models.db import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # setup login manager
    from routes.auth import login_manager, init_login_manager
    init_login_manager(app)

    # register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.resume import resume_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        from models.db import seed_data
        seed_data()

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
