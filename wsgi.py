"""
نقطة الدخول WSGI للتطبيق
"""
from src.main import create_app
from create_admin_endpoint import register_admin_reset_blueprint

app = create_app('production')
register_admin_reset_blueprint(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
