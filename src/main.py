"""
تكامل جميع مسارات التطبيق مع إعدادات البيئة المناسبة
"""
import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from src.config import config
from src.models.db import db

# إنشاء كائنات التطبيق
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
migrate = Migrate()

def create_app(config_name=None):
    """إنشاء وتهيئة تطبيق Flask"""
    # تحديد إعدادات البيئة
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    # إنشاء تطبيق Flask مع مسار الملفات الثابتة الصحيح
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # إضافة context processor للمتغيرات العامة
    @app.context_processor
    def inject_global_vars():
        """توفير المتغيرات العامة لجميع القوالب"""
        notifications = []
        notifications_count = 0
        
        # إذا كان المستخدم مسجل الدخول، يمكن إضافة إشعارات حقيقية هنا
        if current_user and current_user.is_authenticated:
            # يمكن إضافة منطق الإشعارات هنا لاحقاً
            pass
        
        return {
            'notifications': notifications,
            'notifications_count': notifications_count
        }
    
    # تسجيل المسارات
    from src.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from src.routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from src.routes.elevators import elevators as elevators_blueprint
    app.register_blueprint(elevators_blueprint)
    
    from src.routes.requests import requests as requests_blueprint
    app.register_blueprint(requests_blueprint)
    
    from src.routes.parts import parts as parts_blueprint
    app.register_blueprint(parts_blueprint)
    
    from src.routes.contracts import contracts as contracts_blueprint
    app.register_blueprint(contracts_blueprint)
    
    from src.routes.quotes import quotes as quotes_blueprint
    app.register_blueprint(quotes_blueprint)
    
    from src.routes.quality import quality as quality_blueprint
    app.register_blueprint(quality_blueprint)
    
    from src.routes.financial import financial as financial_blueprint
    app.register_blueprint(financial_blueprint)
    
    from src.routes.messaging import messaging_bp
    app.register_blueprint(messaging_bp)
    
    from src.routes.purchases import purchases_bp
    app.register_blueprint(purchases_bp)
    
    from src.routes.settings import settings_bp
    app.register_blueprint(settings_bp)
    
    from src.routes.setup import setup
    app.register_blueprint(setup)
    
    # معالجة الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # إعادة توجيه الصفحة الرئيسية إلى لوحة المعلومات
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.dashboard_view'))
    
    # إضافة route لاختبار الملفات الثابتة
    @app.route('/test-static')
    def test_static():
        return f"""
        <h1>اختبار الملفات الثابتة</h1>
        <p>مسار الملفات الثابتة: {app.static_folder}</p>
        <p>URL الملفات الثابتة: {app.static_url_path}</p>
        <link rel="stylesheet" href="{url_for('static', filename='css/bootstrap.min.css')}">
        <script src="{url_for('static', filename='js/bootstrap.bundle.min.js')}"></script>
        <div class="alert alert-success">إذا ظهر هذا النص بتنسيق جميل، فالملفات الثابتة تعمل!</div>
        """
    
    # إنشاء جميع الجداول إذا لم تكن موجودة
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f'خطأ في إنشاء الجداول: {e}')
    
    return app

# استيراد معالج تسجيل الدخول
from src.models.user import User

@login_manager.user_loader
def load_user(user_id):
    """تحميل المستخدم من قاعدة البيانات"""
    return User.query.get(int(user_id))

# إنشاء تطبيق باستخدام الإعدادات الافتراضية
app = create_app()

# استيراد النماذج لضمان إنشاء الجداول
from src.models.elevator import Elevator
from src.models.maintenance_request import MaintenanceRequest
from src.models.part import Part
from src.models.part_usage import PartUsage
from src.models.scheduled_maintenance import ScheduledMaintenance
from src.models.contract import Contract
from src.models.price import Price
from src.models.quote import Quote
from src.models.quality_compliance.inspection import Inspection
from src.models.quality_compliance.safety_certificate import SafetyCertificate
from src.models.quality_compliance.compliance import ComplianceStandard, ElevatorCompliance
from src.models.financial.receipt import Receipt
from src.models.financial.payment import Payment

# إضافة معالج الأخطاء
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug and not app.testing:
    # إنشاء مجلد السجلات إذا لم يكن موجوداً
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # إعداد ملف السجل
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # إضافة معالج الملف إلى التطبيق
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('تم بدء تشغيل التطبيق')
