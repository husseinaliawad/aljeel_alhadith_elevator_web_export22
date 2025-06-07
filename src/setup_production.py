"""
سكريبت لإعداد التطبيق للنشر في بيئة الإنتاج
"""
import os
import sys
from werkzeug.security import generate_password_hash
from src.models.db import db
from src.models.user import User
from src.main import create_app

def setup_production():
    """إعداد التطبيق للنشر في بيئة الإنتاج"""
    # إنشاء تطبيق بإعدادات الإنتاج
    app = create_app('production')
    
    with app.app_context():
        # إعادة إنشاء قاعدة البيانات
        db.drop_all()
        db.create_all()
        
        # إنشاء مستخدم مسؤول
        admin = User(
            username='admin',
            password='Admin@123',
            full_name='مدير النظام',
            email='admin@example.com',
            role='admin'
        )
        db.session.add(admin)
        
        # إضافة بيانات تجريبية أساسية
        # يمكن إضافة بيانات تجريبية هنا إذا لزم الأمر
        
        # حفظ التغييرات
        db.session.commit()
        
        print("تم إعداد التطبيق للنشر في بيئة الإنتاج بنجاح")
        print("اسم المستخدم: admin")
        print("كلمة المرور: Admin@123")

if __name__ == '__main__':
    setup_production()
