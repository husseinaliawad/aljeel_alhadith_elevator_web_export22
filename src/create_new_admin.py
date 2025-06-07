"""
سكريبت لإنشاء مستخدم مسؤول جديد بمعلومات مختلفة
"""
from src.main import create_app
from src.models.user import User
from src.models.db import db
from werkzeug.security import generate_password_hash

def create_new_admin_user():
    """إنشاء مستخدم مسؤول جديد بمعلومات مختلفة"""
    # إنشاء تطبيق بإعدادات الإنتاج
    app = create_app('production')
    
    with app.app_context():
        # إنشاء مستخدم مسؤول جديد
        new_admin = User(
            username='superadmin',
            full_name='المدير العام',
            email='superadmin@aljeelalhadith.com',
            role='admin'
        )
        new_admin.password_hash = generate_password_hash('SuperAdmin2025')
        db.session.add(new_admin)
        db.session.commit()
        print("تم إنشاء مستخدم مسؤول جديد بنجاح")
        print("اسم المستخدم: superadmin")
        print("كلمة المرور: SuperAdmin2025")

if __name__ == '__main__':
    create_new_admin_user()
