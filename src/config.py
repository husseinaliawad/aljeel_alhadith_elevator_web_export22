"""
ملف التكوين للتطبيق
يحتوي على إعدادات مختلفة للبيئات المختلفة (تطوير، اختبار، إنتاج)
"""
import os

class Config:
    """الإعدادات الأساسية المشتركة بين جميع البيئات"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح_سري_افتراضي_للتطوير_فقط'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.example.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'user@example.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'password'
    
    # إعدادات التطبيق
    APP_NAME = 'برنامج الجيل الحديث للمصاعد'
    COMPANY_NAME = 'الجيل الحديث للأمن والمصاعد'
    ITEMS_PER_PAGE = 10
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بالإعدادات"""
        pass

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev.db'

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///test.db'

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    
    @classmethod
    def init_app(cls, app):
        """تهيئة التطبيق بإعدادات الإنتاج"""
        Config.init_app(app)
        
        # معالجة الأخطاء
        import logging
        from logging.handlers import RotatingFileHandler
        
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

# قاموس التكوينات المتاحة
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
