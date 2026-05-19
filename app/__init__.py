import os
from flask import Flask
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація БД
    from app.models import db
    if not os.path.exists(Config.DATABASE):
        db.init_db()
        # Запустити seed якщо БД нова
        try:
            from seed_data import seed_all
            seed_all(db)
            print("[OK] Baza danyh stvorena ta napovnena pochatkovymy danymy")
        except Exception as e:
            print(f"[WARN] Pomylka pry napovnenni BD: {e}")
    else:
        # Переконатися що таблиці існують
        db.init_db()

    # Реєстрація blueprints
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.main import bp as main_bp
    from app.blueprints.species import bp as species_bp
    from app.blueprints.ingredients import bp as ingredients_bp
    from app.blueprints.rations import bp as rations_bp
    from app.blueprints.optimization import bp as optimization_bp
    from app.blueprints.prices import bp as prices_bp
    from app.blueprints.reports import bp as reports_bp
    from app.blueprints.settings import bp as settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(species_bp)
    app.register_blueprint(ingredients_bp)
    app.register_blueprint(rations_bp)
    app.register_blueprint(optimization_bp)
    app.register_blueprint(prices_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    return app
