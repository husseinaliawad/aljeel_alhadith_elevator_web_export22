"""
سكريبت لإعادة تهيئة قاعدة البيانات وإنشاء حساب مستخدم مسؤول
"""
from src.models.db import db
from src.models.user import User
from src.main import app

def initialize_database():
    """إعادة تهيئة قاعدة البيانات وإنشاء حساب مستخدم مسؤول"""
    with app.app_context():
        # إعادة إنشاء جميع الجداول
        db.drop_all()
        db.create_all()
        
        # إنشاء مستخدم مسؤول جديد
        admin = User(
            username='admin',
            password='Admin@123',
            full_name='مدير النظام',
            email='admin@example.com',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("تم إعادة تهيئة قاعدة البيانات وإنشاء حساب المسؤول بنجاح")
        return True

if __name__ == '__main__':
    initialize_database()
