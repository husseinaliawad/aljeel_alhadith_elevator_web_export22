"""
نموذج المستخدمين لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """نموذج المستخدمين"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default="user")  # admin, user, technician
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, username=None, password=None, full_name=None, email=None, phone=None, role="user"):
        """
        تهيئة كائن المستخدم
        
        المعلمات:
            username (str): اسم المستخدم
            password (str): كلمة المرور
            full_name (str): الاسم الكامل
            email (str): البريد الإلكتروني
            phone (str): رقم الهاتف
            role (str): دور المستخدم (admin, user, technician)
        """
        self.username = username
        self.set_password(password)
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.role = role
    
    def set_password(self, password):
        """
        تعيين كلمة المرور المشفرة
        
        المعلمات:
            password (str): كلمة المرور الجديدة
        """
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        التحقق من صحة كلمة المرور
        
        المعلمات:
            password (str): كلمة المرور المدخلة
            
        العائد:
            bool: True إذا كانت كلمة المرور صحيحة
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل المستخدم
        """
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
