"""
سكريبت لإعادة تعيين كلمة مرور المستخدم المسؤول في بيئة الإنتاج
"""
import os
import sys
from werkzeug.security import generate_password_hash
from src.models.db import db
from src.models.user import User
from src.main import create_app

def reset_admin_password():
    """إعادة تعيين كلمة مرور المستخدم المسؤول في بيئة الإنتاج"""
    # إنشاء تطبيق بإعدادات الإنتاج
    app = create_app('production')
    
    with app.app_context():
        # البحث عن المستخدم المسؤول
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            # إعادة تعيين كلمة المرور
            admin.password_hash = generate_password_hash('Admin123')
            db.session.commit()
            print("تم إعادة تعيين كلمة مرور المستخدم المسؤول بنجاح")
            print("اسم المستخدم: admin")
            print("كلمة المرور: Admin123")
        else:
            # إنشاء مستخدم مسؤول جديد إذا لم يكن موجوداً
            admin = User(
                username='admin',
                password='Admin123',
                full_name='مدير النظام',
                email='admin@example.com',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم مسؤول جديد بنجاح")
            print("اسم المستخدم: admin")
            print("كلمة المرور: Admin123")

if __name__ == '__main__':
    reset_admin_password()
