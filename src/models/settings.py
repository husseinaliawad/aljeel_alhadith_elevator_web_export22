"""
نموذج إعدادات النظام لتطبيق الجيل الحديث للأمن والمصاعد
"""

from src.models.db import db
from datetime import datetime

class SystemSettings(db.Model):
    """نموذج إعدادات النظام"""
    
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, default="الجيل الحديث للأمن والمصاعد")
    company_address = db.Column(db.String(200), nullable=True)
    company_phone = db.Column(db.String(20), nullable=True)
    company_email = db.Column(db.String(100), nullable=True)
    company_website = db.Column(db.String(100), nullable=True)
    tax_number = db.Column(db.String(20), nullable=True)
    commercial_register = db.Column(db.String(20), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    iban = db.Column(db.String(50), nullable=True)
    logo_path = db.Column(db.String(200), nullable=True, default="static/images/logo.png")
    stamp_path = db.Column(db.String(200), nullable=True, default="static/images/company_stamp.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات النظام، إنشاء إعدادات افتراضية إذا لم تكن موجودة"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def update(self, **kwargs):
        """تحديث إعدادات النظام"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
