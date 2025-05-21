from .user_routes import user_bp
from .admin_routes import admin_bp
# 其他...

def register_routes(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)


from routes.admin_routes import admin_bp
app.register_blueprint(admin_bp)
