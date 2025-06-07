"""
سكريبت منفصل لإنشاء مستخدم مسؤول في قاعدة البيانات
"""
from src.main import create_app
from src.models.user import User
from src.models.db import db
from werkzeug.security import generate_password_hash

def create_admin_user():
    """إنشاء مستخدم مسؤول جديد أو إعادة تعيين كلمة المرور"""
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
            # إنشاء مستخدم مسؤول جديد
            admin = User(
                username='admin',
                full_name='مدير النظام',
                email='admin@example.com',
                role='admin'
            )
            admin.password_hash = generate_password_hash('Admin123')
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم مسؤول جديد بنجاح")
            print("اسم المستخدم: admin")
            print("كلمة المرور: Admin123")

if __name__ == '__main__':
    create_admin_user()
