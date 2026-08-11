from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.routes.attendance import bp as attendance_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.events import bp as events_bp
    from app.routes.registrations import bp as registrations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(registrations_bp)
